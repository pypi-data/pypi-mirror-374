
import truffle.hyphae.runtime_svc_pb2_grpc as runtime_svc_pb2_grpc
from truffle.hyphae import hooks_pb2 as hooks_pb2
from truffle.hyphae.context_pb2 import Context

from truffle.hyphae.contextmgmt_pb2 import BuildContextRequest, BuildContextResponse, ManageContextRequest
from truffle.hyphae.toolmask_pb2 import ToolMask
from truffle.hyphae.serializestate_pb2 import SaveStateResponse, LoadStateRequest

from typing import Any, Dict, List, Optional, Union
import concurrent.futures as futures

import grpc
from grpc_reflection.v1alpha import reflection
from google.protobuf import empty_pb2 as google_pb2
import logging

from .context_helpers import get_initial_context
from hyphae.api import get_app_env_state, set_app_env_state

from hyphae import hooks

class HyphaeRuntimeServicer(runtime_svc_pb2_grpc.HyphaeRuntimeServicer):
    SERVICE_NAME = 'truffle.hyphae.HyphaeRuntime'
    """
    all the standard stuff u can override / sdk must impl
    HyphaeRuntime is the runtime service for Hyphae, called by the same agentic client that manages toolcalls.
    The client/agent expects implementations of the following methods to be available for it to function.
    Allowing users to override these methods in an SDK scenario allows for customization of the agentic loop iterations and context management.
    """
    def __init__(self):
        super().__init__()
        # Initialize any necessary state or resources here
        self.handle_appenv_state_fn = None
        self.build_tool_mask_fn = None
        self.build_context_fn = None
        self.load_state_fn = None
        self.save_state_fn = None
        self.builds_context = False

    def OnAppStart(self, request : hooks_pb2.OnAppStartRequest, context : grpc.ServicerContext) -> hooks_pb2.OnAppStartResponse:
        """Called when the app starts, before any agentic loop iterations."""
        logging.info(f"OnAppStart(): {request}")
        response = hooks_pb2.OnAppStartResponse()
        if request.HasField('context'):
            response.context.CopyFrom(get_initial_context(request.context))
        else:
            logging.warning("No initial context provided in OnAppStartRequest, using default.")
            response.context = Context()

        set_app_env_state(request.app_env_state)
        return response
    


    def OnLoopStart(self, request: hooks_pb2.OnLoopStartRequest, context: grpc.ServicerContext) -> hooks_pb2.OnLoopStartResponse:
        """Called before the start of an agentic loop iteration."""
        logging.info(f"OnLoopStart(): {request}")
        response = hooks_pb2.OnLoopStartResponse()
        response.builds_context = self.builds_context
        if self.build_tool_mask_fn:
            try:
                self.build_tool_mask_fn(response)
                logging.debug(f"Tool mask built successfully: {response.tool_mask}")
            except Exception as e:
                logging.error(f"Error building tool mask: {e}")
                context.set_details(str(e))
                context.set_code(grpc.StatusCode.INTERNAL)
                return response
        else:
            logging.warning("No build_tool_mask_fn provided, skipping tool mask build.")
            response.tool_mask = ToolMask()
        if request.HasField('app_env_state'):
            logging.info(f"Handling app environment state: {request.app_env_state}")
            if self.handle_appenv_state_fn:
                try:
                    self.handle_appenv_state_fn(request.app_env_state)
                    logging.debug(f"App environment state handled successfully: {request.app_env_state}")
                except Exception as e:
                    logging.error(f"Error handling app environment state: {e}")
                    context.set_details(str(e))
                    context.set_code(grpc.StatusCode.INTERNAL)
                    return response
            else:
                logging.warning("No handle_appenv_state_fn provided, likely unintentional.")
        if hooks.build_context is not None:
            self.builds_context = True
            response.context.CopyFrom(hooks.build_context(request.context))
        return response
    def BuildContext(self, request: BuildContextRequest, context: grpc.ServicerContext) -> BuildContextResponse:
        """Called to build the context for the agent."""
        response = BuildContextResponse()
        if self.build_context_fn:
            try:
                response.context = self.build_context_fn(request)
                logging.debug(f"Context built successfully: {response.context}")
            except Exception as e:
                logging.error(f"Error building context: {e}")
                context.set_details(str(e))
                context.set_code(grpc.StatusCode.INTERNAL)
                return BuildContextResponse()
        else:
            logging.warning("No build_context_fn provided, skipping context build.")
            response.context = Context()
        return response
   
    def OnCtxManage(self, request: ManageContextRequest, context: grpc.ServicerContext) -> Context:
        """Called with the models context, and current length/target length."""
        logging.info(f"Managing context with request: {request}")
        return hooks.manage_context(request)


    def LoadState(self, request: LoadStateRequest, context: grpc.ServicerContext) -> google_pb2.Empty:
        """Called to load a saved state."""
        logging.info(f"Loading state from {request}")
        if self.load_state_fn:
            try:
                state = self.load_state_fn(request)
                logging.info(f"State loaded successfully: {state}")
            except Exception as e:
                logging.error(f"Error loading state: {e}")
                context.set_details(str(e))
                context.set_code(grpc.StatusCode.INTERNAL)
                return google_pb2.Empty()
        else:
            logging.warning("No load_state_fn provided, skipping state load.")
        return google_pb2.Empty()

    def SaveState(self, request: google_pb2.Empty, context: grpc.ServicerContext) -> SaveStateResponse:
        """Called to save the current state."""
        logging.info("Saving state")
        if self.save_state_fn:
            try:
                state = self.save_state_fn()
                logging.info(f"State saved successfully: {state}")
                return SaveStateResponse(app_state=state)
            except Exception as e:
                logging.error(f"Error saving state: {e}")
                context.set_details(str(e))
                context.set_code(grpc.StatusCode.INTERNAL)
                return SaveStateResponse()
        else:
            logging.warning("No save_state_fn provided, skipping state save.")
            return SaveStateResponse()


    def SetTaskFlags(self, request, context):
        """called to set the flags for the app, like if user wants URR disabled, etc.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAppInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    """Implementation of HyphaeRuntime service. """

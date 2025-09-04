




import typing
import types
import os 
import inspect
import functools
import re
import copy 
import json 
import base64
import time
from concurrent import futures
from datetime import datetime
import dataclasses
from dataclasses import dataclass
from collections import OrderedDict

import warnings
warnings.filterwarnings("ignore")
from google.protobuf.descriptor import  FieldDescriptor

from google.protobuf import descriptor_pool

from google.protobuf.json_format import MessageToDict, ParseDict, Parse, MessageToJson
from google import protobuf as pb

import grpc
from grpc_reflection.v1alpha import reflection

import logging
from .runtime_service import *
from .base import *


APP_SOCK = os.getenv("TFW_APP_ADDR", "[::]:7777")
SDK_SOCK = "err"

from truffle.os.app_info_pb2 import AppInfo
from truffle.hyphae import runtime_svc_pb2 
from truffle.hyphae import runtime_svc_pb2_grpc
import truffle.hyphae.annotations_pb2 as annotations_pb2
from truffle.common.app_tool_pb2 import AppTool
from truffle.common.icon_pb2 import Icon
from truffle.hyphae import context_pb2
from truffle.hyphae.hooks_pb2 import OnLoopStartResponse, AppEnvState
from truffle.infer import infer_pb2_grpc as infer_grpc
# ie now infer_grpc.InferenceService works
from google.protobuf import struct_pb2 

from .proto_conv_common import ToolMethod, to_upper_camel
from .func_to_proto import FuncToProto, get_truffle_tool_fns, args_from_func, is_numeric_field, is_float_field
from .methods_to_service import methods_to_service



class TruffleRuntime(BaseRuntime):
    def __init__(self):
        self.cls = None
        self.tool_methods : typing.Dict[str, ToolMethod] = {}
        self.env : AppEnvState = AppEnvState()

    def get_tool_mask(self, check_all: bool = False) -> typing.Dict[str, bool]:
        mask = {}
        for name, tool_method in self.tool_methods.items():
            if tool_method.predicate_fn is not None:
                try:
                    can_call = tool_method.predicate_fn()
                    if not isinstance(can_call, bool):
                        raise ValueError(f"Predicate for {name} must return a boolean, got {type(can_call)}")
                    mask[name] = can_call
                except Exception as e:
                    mask[name] = True
                    logging.error(f"Error calling predicate for {name}: {e}")
            else:
                mask[name] = True
        return mask
    
    def build(self, class_instance):
        start_time = time.time()
        self.cls = class_instance

        

        def attach_func_to_class(func, cls):
            func.__truffle_tool__ = True
            func.__truffle_description__ = func.__name__
            func.__truffle_icon__ = None
            func.__truffle_args__ = None
            func.__truffle_group__ = None
            func.__truffle_internal__ = True
            func.__truffle_flags__ = None

            
            setattr(cls, func.__name__, types.MethodType(func, cls))
            return func  

        tool_fns = get_truffle_tool_fns(self.cls)
        def fn_to_tool_pb(func):
            tool_pb = AppTool(
                tool_display_name=getattr(func, "__truffle_tool_name__", None),
                tool_name=func.__name__,
                tool_description=getattr(func, "__truffle_description__", None),
                tool_origin=AppTool.AppToolOrigin.APP_TOOL_ORIGIN_USER
            )
            if hasattr(func, "__truffle_icon__"):
                if isinstance(func.__truffle_icon__, str):
                    tool_pb.tool_icon.symbol = func.__truffle_icon__
                elif isinstance(func.__truffle_icon__, Icon):
                    tool_pb.tool_icon.CopyFrom(func.__truffle_icon__)
                else:
                    logging.warning(f"Invalid icon type {type(func.__truffle_icon__)} for {func.__name__}")
            tool_pb.tool_icon.symbol = getattr(func, "__truffle_icon__", "")
            tool_pb.tool_flags.update({
                "flags": getattr(func, "__truffle_flags__", 0)
            })
            if getattr(func, "__truffle_args__", None) is not None:
                tool_pb.tool_args.update(getattr(func, "__truffle_args__"))
            else:
                fn_args = args_from_func(func)
                logging.debug(f"Function {func.__name__} w/out desc has args {fn_args}")
                tool_pb.tool_args.update( {arg: "" for arg in fn_args if arg != "return"})
            return tool_pb
        
        package_name = "app." + self.cls.__class__.__name__
        app_info = AppInfo()
        app_info.name = self.cls.__class__.__name__
 
        for name, func in tool_fns.items():
            if to_upper_camel(name) != name:
                name = to_upper_camel(name)
        
            tool_pb = fn_to_tool_pb(func)
            app_info.tools.append(tool_pb)
            ftp = FuncToProto(func, package_name, tool_pb)
            input_desc, output_desc =  ftp.descriptors()
            input_msg, output_msg = ftp.message_classes()

            #todo: fix function names! 
            pred = getattr(func, "__truffle_predicate__", None)
            if pred is not None:
                params = [p for p in inspect.signature(pred).parameters.values() if p.name == 'self']
                if len(params) == 1:
                    f = pred
                    inst = self.cls
                    def argless_pred(f=f, inst=inst):
                        return f(inst)
                setattr(func, "__truffle_predicate__", argless_pred)
                pred = argless_pred

            tool_method = ToolMethod(
                func=func,
                input_desc=input_desc,
                output_desc=output_desc,
                input_msg=input_msg,
                output_msg=output_msg,
                wrapper_fn=None,
                predicate_fn= pred,
                group_name=getattr(func, "__truffle_group__", None), #TODO remove me 
                tool_pb=tool_pb
            )
            self.tool_methods[name] = tool_method
            logging.debug(f"Built tool method {name}")
        
        self._service = methods_to_service(self.tool_methods, package_name, self.cls.__class__.__name__)
        logging.info(f"Built service {self._service.descriptor.name} package {package_name}")


        def handle_request(method : ToolMethod, cls, request, context : grpc.ServicerContext):
            for metadatum in context.invocation_metadata(): # how we add additional info from decs 
                pass
            args_dict = MessageToDict( # we hate this fn 
                request,
                always_print_fields_with_no_presence=True, # we <3 this flag
                preserving_proto_field_name=True,
                descriptor_pool=descriptor_pool.Default()
            )
            fn_args = args_from_func(method.func)
            #do stupid string conversion.. honestly dont ask
            for field  in method.input_msg.DESCRIPTOR.fields:
                if field.name in args_dict:
                    if field.name in fn_args and field.name != "return_value":                            
                        if dataclasses.is_dataclass(fn_args[field.name]):
                            args_dict[field.name] = fn_args[field.name](**args_dict[field.name])
                    if is_numeric_field(field):
                        args_dict[field.name] = float(args_dict[field.name]) if is_float_field(field) else int(args_dict[field.name])
                    if field.type == FieldDescriptor.TYPE_BYTES:
                        if isinstance(args_dict[field.name], str):
                            if hasattr(request, field.name):
                                args_dict[field.name] = getattr(request, field.name)
                            else:
                                #message to dict probably base64'd bytes to a string 
                                try:
                                    args_dict[field.name] = bytes(base64.b64decode(args_dict[field.name]))
                                except Exception as e:
                                    args_dict[field.name] = bytes(args_dict[field.name].encode()) 

                            if type(args_dict[field.name]) != bytes:
                                logging.error(f"Expected bytes for field {field.name}, got {type(args_dict[field.name])}")
                                
            args = list(args_dict.values())

            logging.debug(f"Received request for {method.func.__name__} with args <{args}>")
            #logging.debug(text_format.MessageToString(request, print_unknown_fields=True, use_field_number=True, ))

            try:
                ret = method.func(cls, *args)
                ret_pb = method.output_msg()
                for field in ret_pb.DESCRIPTOR.fields:
                    field : FieldDescriptor = field
                    if field.name != "return_value":
                        continue
                    if field.message_type and field.message_type.has_options and field.message_type.GetOptions().map_entry:
                        if isinstance(ret, dict):
                            map_field = getattr(ret_pb, field.name)
                            map_field.update(ret)
                            logging.debug(f"Updated map field {field.name} with {ret}")
                        else:
                            logging.error(f"Expected dict for map field {field.name}, got {type(ret)}")
                    elif field.label == FieldDescriptor.LABEL_REPEATED:
                        if isinstance(ret, (list, tuple)):
                            getattr(ret_pb, field.name).extend(ret)
                        else:
                            getattr(ret_pb, field.name).append(ret)
                    else:
                        if field.type == FieldDescriptor.TYPE_MESSAGE:
                            logging.debug(f"Message field {field.name} is {field.message_type.name}")
                            if dataclasses.is_dataclass(ret):
                                old = ret 
                                ret = dataclasses.asdict(ret)
                            if isinstance(ret, dict):
                                ParseDict(ret,  getattr(ret_pb, field.name), descriptor_pool=descriptor_pool.Default(), ignore_unknown_fields=True) # this is a hacky way to set the message
                                # getattr(ret_pb, field.name).ParseFromDict(ret)
                            else:
                                logging.warning(f"Expected dict for message field {field.name}, got {type(ret)}")
                                getattr(ret_pb, field.name).CopyFrom(ret) # questionable
                        else:
                            logging.debug(f"setting field {field.name} to {ret}")
                            setattr(ret_pb, field.name, ret)
                context.set_code(grpc.StatusCode.OK)
                context.set_details(f"Success calling {method.func.__name__}")
                return ret_pb
            except Exception as e:
                logging.error(f"Error calling {method.func.__name__}: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error calling {method.func.__name__}: {e}")
                return method.output_msg()
        for name, method in self.tool_methods.items():
            method.wrapper_fn = functools.partial(handle_request, method, self.cls)
        
        class AppService(self._service.service_class):
            def __init__(self, tool_methods, desc):
                super().__init__()
                self.tool_methods = tool_methods
                self.desc = desc
            def __getattribute__(self, name: str) -> typing.Any:
                if name != "tool_methods":
                    if name in self.tool_methods:
                        return self.tool_methods[name].wrapper_fn
                return super().__getattribute__(name)
            
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=2)) # only us hitting this from outside of container
        self._service.registration_function(AppService(self.tool_methods, self._service.descriptor), server) #i honestly dont remember what i was doing with this
        runtime = HyphaeRuntimeServicer()

        def rt_build_tool_mask_fn(response: OnLoopStartResponse):
            response.tool_mask.entries.update(self.get_tool_mask())
        
        def rt_appenv_state_fn(request_env: AppEnvState):
            self.env = request_env
            logging.debug(f"Received AppEnvState: {request_env}")

        runtime.build_tool_mask_fn = rt_build_tool_mask_fn
        runtime.handle_appenv_state_fn = rt_appenv_state_fn
        runtime_svc_pb2_grpc.add_HyphaeRuntimeServicer_to_server(
            runtime, server
        )
        reflection.enable_server_reflection(
            [self._service.descriptor.full_name, reflection.SERVICE_NAME, HyphaeRuntimeServicer.SERVICE_NAME], server
        )
        
        server.add_insecure_port(APP_SOCK)
        old_level = logging.getLogger().level
        logging.getLogger().setLevel( logging.DEBUG)
        logging.getLogger().info(f"starting {self._service.descriptor.full_name} on {APP_SOCK}")
        logging.getLogger().setLevel(old_level )
        server.start()
        logging.info(f"Server started in {time.time() - start_time:.4f} seconds")
        logging.debug("Server is up")
        server.wait_for_termination()
        logging.info("Server terminated")

        
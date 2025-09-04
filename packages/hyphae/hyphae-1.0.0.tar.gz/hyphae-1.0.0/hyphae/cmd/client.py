

from truffle.os.truffleos_pb2_grpc import *

from truffle.os.truffleos_pb2_grpc import TruffleOSStub
import grpc 
import google.protobuf.empty_pb2 as empty_pb2
from truffle.os.app_requests_pb2 import AppInstallRequest, AppInstallResponse
from truffle.os.client_session_pb2 import RegisterNewSessionRequest, RegisterNewSessionResponse, NewSessionStatus
from truffle.os.client_metadata_pb2 import ClientMetadata
from truffle.os.system_info_pb2 import SystemInfo
from truffle.os.hardware_info_pb2 import HardwareInfo
import logging
import os
from pathlib import Path
import uuid 
import platform
 
from hyphae.cmd.creds import resolve_url, get_token_for_url, set_token_for_url, delete_token_for_url, has_token_for_url
import hyphae.cmd.userdata as userdata

# local devices always have a self signed cert, 
#   so you have to disable SSL verification anyways
# this helps keep sdk simple for now 
USE_SSL = False 


def get_client_metadata(m : ClientMetadata) -> ClientMetadata:
    m.platform = f"{platform.system()}-{platform.release()}-{platform.machine()}"
    m.version = f"{platform.version()} hyphae0"
    m.device = f"{platform.node()} - Hyphae SDK"
    return m

def url_for_keyring(url: str = userdata.get_base_url()) -> str:
    return resolve_url(url)

class TruffleOSClient():
    def __init__(self, override_url: str | None = None):
        """
        Initialize the TruffleOS client.
        If override_url is provided, it will use that URL instead of the default one.
        """

        self.url = override_url or userdata.get_base_url()
        logging.debug(f"creating client... using url {self.url}")
        self.url = resolve_url(self.url)
        self._channel = create_truffle_client(self.url)
        if not self._channel:
            raise ValueError(f"Failed to create gRPC channel for URL {self.url}.")
        self._stub = TruffleOSStub(self._channel)
        self._metadata = []
        self._token = None
    def __del__(self):
        """
        Ensure clean up/timely disconnect on destruction.
        """
        if not hasattr(self, '_channel'):
            return 
        if self._channel:
            logging.debug("truffleos client: closing gRPC channel")
            self._channel.close()

    def _use_token(self, token ) -> None:
        self._token = token
        if not self._token:
            raise ValueError(f"Failed to get session token found in keyring for URL {self.url}. ")
        self._metadata = [('session', self._token)]

    def authenticate(self, override_token: str | None = None) -> None:
        """
        Authenticate the client with a session token.
        If override_token is None, it will try to get the token from keyring or auth normally.

        """
        if not override_token:
            #FIXME: this is bad and we should at least do url w/out port 
            token = get_token_for_url(self.url)
        else:
            token = override_token

        if not token:
                user_id = userdata.get_user_id()
                if not user_id:
                    raise ValueError("No user ID found, have you used our GUI client to login?")
                logging.warning(f"No session token found for URL {self.url}, requesting new session for client id {user_id} ")
                logging.info("Please accept the request on another logged in session.")
                request = RegisterNewSessionRequest()

                if os.getenv("TRUFFLE_RECOVERY", None) is not None:
                    logging.info("TRUFFLE_RECOVERY is set, using recovery mode")
                    code = input("Enter one of your recovery codes: ")
                    logging.warning("warning: using code <{code}> - it will no longer be valid after use")
                    request.recovery_code = code
                else:
                    request.user_id = user_id
                get_client_metadata(request.metadata)
                try:
                    logging.debug(f"Registering new session with request: {request}")
                    resp : RegisterNewSessionResponse = self._stub.Client_RegisterNewSession(request) 
                except grpc.RpcError as e:
                    logging.error(f"Failed to register new session: {e}")
                    raise
                if not resp.token or len(resp.token) <= 0:
                    raise ValueError("Verification request failed, no token returned.")
                token = resp.token
                logging.info(f"New session token received: {token}")
                #FIXME: see above FIXME
                set_token_for_url(self.url, token)
        self._use_token(token)
        logging.debug("trying auth: getting system info")

        info = SystemInfo()
        try:
            info : SystemInfo = self._stub.System_GetInfo(empty_pb2.Empty(), metadata=self.grpc_metadata())
            if not info:
                raise ValueError("Failed to get system info, no response received.")
            logging.debug(f"Authenticated with token: {token}")
            if not info.HasField("hardware_info"):
                raise ValueError("sys info does not contain hardware info.")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                logging.error("Authentication failed, clearing stored token.")
                delete_token_for_url(self.url)
                raise ValueError("Authentication failed, please check your session token or user ID.")
            else:
                logging.error(f"Failed to get system info: {e}")
                raise
        logging.info(f"Connected to Truffle: {info.hardware_info.hostname} v{info.hardware_info.ip_address}")

    def stub(self) -> TruffleOSStub:
        """
        Get the gRPC stub for the TruffleOS service.
        """
        return self._stub

    def get_user_id(self) -> str:
        return userdata.get_user_id()

    def get_base_url(self) -> str:
        return userdata.get_base_url()
    def grpc_metadata(self) -> list[tuple[str, str]]:
        if not self._metadata or len(self._metadata) <= 0:
            if self._metadata:
                logging.warning("metadata requested, but currently empty! likely not authenticated")
        return self._metadata
    
    # shims
    def app_install(self, request : AppInstallRequest) -> AppInstallResponse:
        return self._stub.App_Install(request, metadata=self.grpc_metadata())
    
def create_truffle_client(url: str | None = None) -> grpc.Channel:
    """
    Create a gRPC client for the TruffleOS service.
    If override_url is provided, it will use that URL instead of the default one.
    """
    if not url:
        logging.error("No URL provided and unable to find base URL from userdata.")
        raise ValueError("Base URL is required to create a TruffleOS client.")
    if USE_SSL:
        # just lookup how to disable SSL verification in python and use 443 
        raise NotImplementedError("SSL support is not implemented yet.")
    else:
        logging.debug(f"Connecting to TruffleOS at {url}")
        return grpc.insecure_channel(url)
       


    
    

from truffle.infer.infer_pb2_grpc import InferenceServiceStub

from truffle.hyphae.context_pb2 import Context
from truffle.infer.convo.conversation_pb2 import Message
import grpc
from truffle.infer.irequest_pb2 import IRequest
from hyphae.api import get_app_env_state, set_app_env_state
from truffle.infer.model_pb2 import  GetModelListRequest, Model, ModelList
class InferenceClient:
    def __init__(self, url : str ):
        self.channel = grpc.insecure_channel(url)
        self.stub = InferenceServiceStub(self.channel)

    def generate_oneshot(self, model_uuid: str, system_prompt :str, user_prompt : str,  max_tokens: int = 512) -> str:
        r : IRequest = IRequest()
        r.model_uuid = model_uuid
        r.convo.messages.add(role=Message.ROLE_SYSTEM, text=system_prompt)
        r.convo.messages.add(role=Message.ROLE_USER, text=user_prompt)
        r.cfg.max_tokens = max_tokens
        print(f"Sending request to model {model_uuid} with system prompt {system_prompt} and user prompt {user_prompt}")
        response = self.stub.Generate(r)
        return response.text
    
_client : InferenceClient | None = None
def get_inference_client() -> InferenceClient:
    global _client
    if not _client:
        url = get_app_env_state().grpc_address
        print(f"Creating InferenceClient with URL: {url}")
        _client = InferenceClient(url)
    return _client


def find_model_for_summarization() -> str:
    """
    Finds a suitable model for summarization tasks.
    This is a placeholder implementation and should be replaced with actual logic to find the best model.
    """
    # Placeholder: return a hardcoded model UUID
    client = get_inference_client()
    req = GetModelListRequest()
    req.use_filter = False 
    
    model_list : ModelList = client.stub.GetModelList(req)
    for model in model_list.models:
        if model.state != Model.MODEL_STATE_LOADED:
            continue
        if model.config.info.is_agentic:
            continue
        print(f"Found model: {model.name} ({model.uuid}), Agentic: {model.config.info.is_agentic}, State: {model.state}")
        return model.uuid
        
    return "your-summarization-model-uuid"


import truffle.hyphae.runtime_svc_pb2 as rt_pb2 

import truffle.hyphae.runtime_svc_pb2_grpc as rt_pb2_grpc
from truffle.hyphae.contextmgmt_pb2 import BuildContextRequest, BuildContextResponse, ManageContextRequest
from truffle.hyphae.context_pb2 import Context

from truffle.infer.convo.conversation_pb2 import Conversation, Message
from hyphae.infer import get_inference_client, find_model_for_summarization
from truffle.infer.irequest_pb2 import IRequest
from truffle.infer.iresponse_pb2 import IResponse


def manage_context(request: ManageContextRequest) -> Context:
    """
    Default implementation of context management.
    This function can be overridden by users to provide custom context management logic.
    """
    infer = get_inference_client()
    ctx = request.context
    sum_model = find_model_for_summarization()
    print(f"Default manage_context called with request: {request}")
    for block in request.context.blocks:
        print(f"Block ID: {block.block_id}, Role: {block.role}, Entries: {len(block.entries)}")
        if block.role == Message.ROLE_ASSISTANT:
            for entry in block.entries:
                if entry.HasField("text") == False:
                    continue
                # summarize? remove all up to you! 
                
                valid_request = IRequest()
                valid_request.model_uuid = sum_model
                valid_request.convo.messages.add(role=Message.ROLE_SYSTEM, text="You are an expert at summarization. Summarize the following text concisely, focusing on key points. Sub 2 sentences")
                valid_request.convo.messages.add(role=Message.ROLE_USER, text=entry.text)
                valid_request.cfg.max_tokens = 256
                response : IResponse = infer.stub.Generate(valid_request)
                
                entry.text = response.content
                pass 
    
    return ctx
    # context is fully malleable! 
    




get_initial_context = None 


build_context = None


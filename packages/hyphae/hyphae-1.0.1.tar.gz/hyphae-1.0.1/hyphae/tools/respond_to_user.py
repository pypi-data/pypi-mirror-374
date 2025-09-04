from dataclasses import dataclass
from typing import List
import hyphae
from truffle.hyphae.annotations_pb2 import RespondToUserReturnType, FileMetadata, AttachedFile
import os 

@hyphae.tool("Send a message back to the user, usually after performing a task with many tool calls", icon="message")
@hyphae.args(
    response="The message to send back to the user,",
    files="absolute paths to files within your enviroment to send back to the user, if any"
)
def RespondToUser(self, response: str, files: List[str]) -> RespondToUserReturnType:
    """
        Standard tool to send a message back to the user, 
        can be overridden by the app to provide custom functionality.
    """
    ret = RespondToUserReturnType()
    ret.response = response
    for file_path in files:
        if not os.path.isabs(file_path):
            raise ValueError(f"File path must be absolute: {file_path}")
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}!")
        
        attached_file = AttachedFile()
        attached_file.metadata.name = os.path.basename(file_path)
        attached_file.metadata
        ret.files.append(attached_file)
    return ret


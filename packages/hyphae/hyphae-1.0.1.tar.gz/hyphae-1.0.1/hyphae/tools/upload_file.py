import requests
import os, mimetypes
from pathlib import Path
from typing import List, Dict


from truffle.common.file_pb2 import AttachedFile, FileMetadata


from hyphae.api import get_app_env_state, set_app_env_state


def file_to_metadata(path: Path) -> FileMetadata:
    """
    Convert a file path to a FileMetadata object.
    """
    metadata = FileMetadata()
    metadata.name = path.name
    metadata.size = path.stat().st_size
    metadata.path = str(path)
    metadata.mime_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    return metadata

def upload_files(file_path_strs: List[str]) -> List[AttachedFile]:
    """
    Upload files to the Hyphae server and return a List of AttachedFile objects
    """
    paths : Dict[str, Path] = {}

    for fps in file_path_strs:
        path = Path(fps).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {fps}")
        paths[path.name] = path
    if not paths or len(paths) == 0:
        raise ValueError("No valid file paths provided for upload.")



    app_env_state = get_app_env_state()
    print(f"App Env State: {app_env_state}")
    host = app_env_state.http_address
    if not host:
        raise ValueError("HTTP address is not set in the application environment state.")
    auth_token = app_env_state.api_token

    attached_file = AttachedFile()
    files = {}
    for _, file_path in paths.items():
        if not file_path.is_file():
            raise FileNotFoundError(f"File {file_path} does not exist.")
        if not file_path.is_absolute():
            raise ValueError(f"File path {file_path} is not absolute.")
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist.")
        
        files[file_path.name] = (file_path.name, open(file_path, 'rb'), 'application/octet-stream')

    multipart_files = []
    for _, path in paths.items():
        mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        multipart_files.append(
            ("file", (path.name, open(path, "rb"), mime))
        )

    response = requests.post(
        f"{host}/files",
        files=multipart_files,
        headers={"Authorization": f"Bearer {auth_token}"},
        verify=False,
        timeout=20
    )

    if response.status_code != 200:
        raise Exception(f"Failed to upload files: {response.text}")

    resp_json = response.json().get("files", [])

    if not isinstance(resp_json, list) or len(resp_json) == 0:
        raise ValueError("Expected a list of uploaded file responses.")

    attached_files = []
    for f in resp_json:
        if "uuid" not in f or "filename" not in f:
            raise ValueError(f"Uploaded file {f} does not contain a UUID or filename.")
        
        attached_file = AttachedFile()
        attached_file.metadata.CopyFrom(file_to_metadata(paths[f["filename"]]))
        attached_file.file_id = f["uuid"]
        attached_files.append(attached_file)

    return attached_files



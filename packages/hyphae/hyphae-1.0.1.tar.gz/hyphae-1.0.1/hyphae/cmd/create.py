from pathlib import Path
import requests 
import logging 
def write_template_to_dir(dir : Path, name : str = "") -> None:
    if not dir.exists():
        dir.mkdir(parents=True, exist_ok=True)
    app_json_template = """{
    "app_uuid": "",
    "metadata": {
        "name": "NAMEPLACEHOLDER",
        "description": "An app I made",
        "icon" : "icon.png"
    },
    "protocol_version": 0
}"""
    if name is None or len(name) <= 0:
        name = dir.name
    app_json_template = app_json_template.replace("NAMEPLACEHOLDER", name)
    with open(dir / "app.json", "w") as f:
        f.write(app_json_template)

    src_name = name.replace(" ", "").lower() 
    py_name = src_name + ".py"
    (dir / py_name).touch()
    (dir / ".gitignore").write_text("*.pyc\n__pycache__/\n.env\n")
    
    truffile_template = """
FROM hyphaehyphae/alpine-python:arm64

RUN pip3 install --no-cache-dir hyphae>=1.0.0 

RUN mkdir -p /opt/app

COPY PYFILEPLACEHOLDER /opt/app

WORKDIR /opt/app
CMD ["python3", "PYFILEPLACEHOLDER"]

"""
    truffile_template = truffile_template.replace("PYFILEPLACEHOLDER", py_name)
    with open(dir / "Truffile", "w") as f:
        f.write(truffile_template)

    #FIXME 
    tmp_icon_req = requests.get("https://pngimg.com/d/question_mark_PNG68.png")
    if tmp_icon_req.status_code == 200:
        with open(dir / "icon.png", "wb") as icon: icon.write(tmp_icon_req.content)
    else:
        logging.warning("Failed to download default icon.png")  
    logging.info(f"Created new app template in {dir}")

    default_py = r"""import hyphae 

    
from dataclasses import dataclass
    

from typing import Tuple, List, Dict, Any, Union, Annotated


from hyphae.tools.respond_to_user import RespondToUserReturnType

import os, subprocess, traceback
import dataclasses
from pathlib import Path

from hyphae.tools.upload_file import upload_files

class CLASSPLACEHOLDER: 
    def __init__(self):
        self.notepad : str = ""

    @hyphae.tool("Send a message back to the user, usually after performing a task with many tool calls", icon="message")
    @hyphae.args(
        response="The message to send back to the user,",
        files="absolute paths to files within your enviroment to send back to the user, if any"
    )
    def RespondToUser(self, response: str, files: List[str]) -> RespondToUserReturnType:
        r = RespondToUserReturnType()
        r.response = response
        try:
            if files and len(files) > 0:
                uploaded_files = upload_files(files)
                for file in uploaded_files:
                    r.files.append(file)
        except Exception as e:
                raise RuntimeError(f"Failed to upload files: {str(e)}")
        return r
    


    @hyphae.tool("This tool writes a file to the given path with the given content. Only use it if the user requested a report", icon="keyboard")
    @hyphae.args(path="The path to write the file to", content="The content to write to the file")
    def WriteFile(self, path: str, content: str) -> str:
        if len(path) > len(content):
            x = path
            path = content 
            content = x 
        directory = os.path.dirname(path)
        if directory: 
            os.makedirs(directory, exist_ok=True)
        try:
            with open(path, "w") as f:
                f.write(content)
            return f"Wrote {len(content)} bytes successfully to {os.path.basename(path)}"
        except Exception as e:
            return f"Error writing file {path}: {str(e)}\nTraceback: {traceback.format_exc()}"

    @hyphae.tool("Reads a file, execute command can also do this", icon="book.closed")
    @hyphae.args(path="The path to the file to read", max_lines="The maximum number of lines to read, leave 0 for no limit")
    def ReadFile(self, path: str, max_lines: int) -> str:
        if not os.path.exists(path):
            return f"ReadFile Error: <File {path} does not exist.>"
        try:
            with open(path, "r") as f:
                if max_lines > 0:
                    lines = f.readlines()[:max_lines]
                else:
                    lines = f.readlines()
            return "".join(lines)
        except Exception as e:
            return f"ReadFile Error: path {path}: {str(e)}>\nTraceback: {traceback.format_exc()}"
        
    @hyphae.tool("This tool executes a shell command and returns the output. For this enviroment it likely will not be necessary. ", icon="apple.terminal")
    @hyphae.args(command="The shell command to execute", timeout="The timeout (seconds) for the command execution")
    def ExecuteCommand(self, command: str, timeout: int) -> List[str]:
        print("ExecuteCommand: ", command)
        output = ""
        try:
            output = subprocess.check_output(
                command, stderr=subprocess.STDOUT, shell=True, timeout=timeout,
                universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            return ["Shell Command Error (" + str(exc.returncode) + "): " + exc.output, command]
        except subprocess.TimeoutExpired:
            return ["Shell Command Timeout", command]
        except Exception as e:
            return ["Shell Command Error: " + str(e) + '\n Traceback:' + traceback.format_exc(), command]
        else:
            return [output, command]
       
if __name__ == "__main__":
    hyphae.run(CLASSPLACEHOLDER())

"""     
    default_py = default_py.replace("CLASSPLACEHOLDER", src_name.title().replace(" ", "")) #kindof a bad way to do the name 
    with open(dir / py_name, "w") as f:
        f.write(default_py)
    

import argparse
import os 
import requests
import logging
from pathlib import Path
import json
import time
from typing import List, Dict
from truffle.os.truffleos_pb2 import *
from truffle.os.app_info_pb2 import *
from truffle.os.truffleos_pb2_grpc import TruffleOSStub
import grpc 
import google.protobuf.empty_pb2 as empty_pb2
import uuid
import shlex
import zipfile
import tempfile
import traceback
from hyphae.cmd.client import TruffleOSClient


def is_uuid(val: str) -> bool:
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False


CFG_FILE_NAME = "app.json"
AUTO_PARSE_DOCKERFILE = os.environ.get('HYPHAE_PARSE_DOCKERFILE', '1') == '1'
def _find_dot_env(path: Path) -> List[str]:
    common_paths = [
        '.env'
    ]
    for common_path in common_paths:
        env_path = path / common_path
        if env_path.exists():
            return env_path.read_text().splitlines()
    return []

def parse_dockerfile(dockerfile_path):
    # this is dumb and i just had chatgpt write it
    # builder can get this info properly, todo 
    cmd = None
    entrypoint = None
    env = {}
    workdir = "/"

    with open(dockerfile_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("ENV "):
                tokens = shlex.split(line[4:])
                for i in range(0, len(tokens), 2):
                    env[tokens[i]] = tokens[i+1] if i+1 < len(tokens) else ""
            elif line.startswith("WORKDIR "):
                workdir = line[8:].strip()
            elif line.startswith("CMD "):
                cmd = line[4:].strip()
            elif line.startswith("ENTRYPOINT "):
                entrypoint = line[11:].strip()
    if cmd is not None:
        try:
            cmd_array = json.loads(cmd)
            if isinstance(cmd_array, list):
                cmd = cmd_array
            else:
                cmd = [cmd_array]
        except json.JSONDecodeError:
            cmd = [str(cmd)]
    if entrypoint is not None:
        try:
            entrypoint_array = json.loads(entrypoint)
            if isinstance(entrypoint_array, list):
                entrypoint = entrypoint_array
            else:
                entrypoint = [entrypoint_array]
        except json.JSONDecodeError:
            entrypoint = [str(entrypoint)]
        # just add it to cmd so we dont have to support both
        if cmd is None:
            cmd = entrypoint
        else:
            cmd = entrypoint + cmd
    if cmd is None and entrypoint is None:
        raise ValueError("No CMD or ENTRYPOINT found in Dockerfile")

    env_list = [f"{k}={v}" for k, v in env.items()] if len(env) else []
    env_list += _find_dot_env(Path(workdir)) 
    return {
        "env": env_list,
        "cwd": workdir,
        "cmd": cmd
    }

def upload_to_build(zip_path: Path | None, server_url: str, build_id: str = "") -> None:
    if zip_path is None or not zip_path.exists():
        raise FileNotFoundError(f"Zip path not found: {zip_path}")

    with zip_path.open("rb") as f:
        headers = {"Content-Type": "application/zip",
                   "Build-ID": build_id,
                  #"Authorization": f"Bearer {}"
                   }
        try:
            with requests.post(server_url, data=f, headers=headers, stream=True) as r:
                r.raise_for_status()
                print("Build server accepted bundle, streaming logs:\n")
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        print(chunk.decode("utf-8"), end="")
        except requests.HTTPError as e:
            print(f"HTTP error from build server: {e.response.status_code} {e.response.text}")
        except Exception as e:
            print(f"Request failed: {e}")
    logging.info(f"Build and upload completed successfully.")



def save_config(path_str: str, config: Dict) -> None:
    #TODO: We need a app-lock.json like node
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    config_path = path / CFG_FILE_NAME
    with config_path.open("w") as f:
        json.dump(config, f, indent=4)
    logging.info(f"Config saved to {config_path}")

def write_default_config(path_str: str):
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    config = {
       "app_uuid" : None,
       "metadata": {
           "name": "My Hyphae App",
           "description": "A Hyphae app",
           "version": "",
           "icon" : "",
       },
       "runtime": {
          "type": "task",
          "env" : {},
          "cwd": "/",
          "cmd": [],
       }
    }
    save_config(path_str, config)

def update_config(path_str: str) -> str:
    #returns id or empty if we need to generate one
    if not os.path.exists(path_str):
        raise FileNotFoundError(f"Path not found: {path_str}")
    if not os.path.isdir(path_str):
        raise NotADirectoryError(f"Path is not a directory: {path_str}")
    path = Path(path_str)
    config_path = Path(path_str) / CFG_FILE_NAME
    if not config_path.exists():
        logging.error(f"Config file not found at {config_path} - did we initialize this app?")
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with config_path.open("r") as f:
        config = json.load(f)

    dockerfile_path = path / "Dockerfile" if not path / "Truffile" else path / "Truffile"
    if not dockerfile_path.exists():
        raise FileNotFoundError(f"Dockerfile not found in path: {dockerfile_path}")
    if 'metadata' not in config:
        config['metadata'] = {}
    if 'name' not in config['metadata'] or not config['metadata']['name']:
        config['metadata']['name'] = Path(path_str).stem
    if 'description' not in config['metadata'] or not config['metadata']['description']:
        config['metadata']['description'] = f"A Hyphae app"
    if 'icon' in config['metadata'] and config['metadata']['icon']:
        icon_path = path / config['metadata']['icon']
        if not icon_path.exists():
            logging.warning(f"Icon path {icon_path} does not exist!")
        
        
        
    if AUTO_PARSE_DOCKERFILE:
        config['runtime'] = parse_dockerfile(dockerfile_path)
        save_config(path_str, config)
    need_id = True if 'app_uuid' not in config or not config['app_uuid'] else False
    
    if not need_id and not is_uuid(config['app_uuid']):
        logging.error(f"App UUID {config['app_uuid']} is not a valid UUID. Please let the system generate one for you.")
        config['app_uuid'] = None
        save_config(path_str, config)
        raise ValueError(f"App UUID {config['app_uuid']} is not a valid UUID")
    elif not need_id: #is uuid
        logging.info(f"Using existing app UUID: {config['app_uuid']}")
        return config['app_uuid']
    return str()

    
def get_config(path_str: str) -> Dict:
    if not os.path.exists(path_str):
        raise FileNotFoundError(f"Path not found: {path_str}")
    if not os.path.isdir(path_str):
        raise NotADirectoryError(f"Path is not a directory: {path_str}")
    path = Path(path_str)
    config_path = path / CFG_FILE_NAME
    if not config_path.exists():
        logging.error(f"Config file not found at {config_path} - did we initialize this app?")
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with config_path.open("r") as f:
        return json.load(f)

   



def build_app(path_str: str) -> int:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if not path.is_dir():
        if path.suffix == '.hyphae':
            logging.warning(f"Path {path} is a .hyphae bundle, did you mean to upload it instead of build?")
            return 1
    
    app_id = update_config(path_str)
    logging.debug(f"building with config: {get_config(path_str)}")
    

    return 0
def _looks_like_venv(builddir: Path, dirname: str) -> bool:
    venv_path = builddir / dirname
    if not venv_path.is_dir(): return False
    markers = [
        venv_path / 'pyvenv.cfg',
        venv_path / 'bin' / 'activate',
        venv_path / 'bin' / 'activate.fish',
        venv_path / 'bin' / 'activate.csh',
        venv_path / 'Scripts' / 'activate.bat'
    ]
    return any(marker.exists() for marker in markers)

def _make_zip(builddir: Path, dst_file: Path):
    blacklist_files = {'.DS_Store', '.gitignore'}
    blacklist_dirs = {'__pycache__', '.git'}
    assert builddir.exists() and builddir.is_dir(), f"Invalid source directory: {builddir}"
    assert dst_file.suffix == ".hyphae", f"Invalid destination file: {dst_file}"

    with zipfile.ZipFile(dst_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(builddir):
            dirs[:] = [d for d in dirs if d not in blacklist_dirs and not _looks_like_venv(builddir, d)]

            rel_root = os.path.relpath(root, builddir)
            if rel_root != ".":
                zipf.write(root, arcname=rel_root)

            for file in files:
                if (
                    file.startswith(".") or
                    file.endswith(".truffle") or
                    file.endswith(".hyphae") or
                    file in blacklist_files
                ):
                    continue
                full_path = os.path.join(root, file)
                if file == 'Truffile':
                    arcname = os.path.join(rel_root, 'Dockerfile')
                else:
                    arcname = os.path.relpath(full_path, builddir)
                zipf.write(full_path, arcname)

    bundle_size = dst_file.stat().st_size
    if bundle_size > 200 * 1024 * 1024:
        logging.error(f"Bundle size too large ({bundle_size/(1024*1024):.2f} MB > 200 MB)")
        dst_file.unlink()
        return None
    return dst_file

def write_builder_cache(path : Path, build_id: str):
    builder_cache_file = path / ".hyphae-last-build"
    builder_cache_file.write_text(build_id)
def read_builder_cache(path : Path) -> str:
    builder_cache_file =  path / ".hyphae-last-build"
    if not builder_cache_file.exists():
        return ""
    return builder_cache_file.read_text().strip()




def build_from_folder(path: Path) -> AppInstallRequest | None:
    """
    Build an app from a folder and return the app ID and AppInfo.
    """
    install_request = AppInstallRequest()   
    app_id = update_config(str(path))
    cfg = get_config(str(path))
    assert cfg is not None, "Config is None, did you initialize the app?"
    meta = cfg.get('metadata', {})
    
    install_request.app_id = app_id
    install_request.app_info.name = meta.get('name', path.stem)
    install_request.app_info.description = meta.get('description', "A Hyphae app")
    if 'icon' in meta and meta['icon']:
        icon_path = path / meta['icon']
        if not icon_path.exists():
            logging.warning(f"Icon path {icon_path} does not exist!")
        else:
            with icon_path.open("rb") as f:
                install_request.app_info.icon.png_data = f.read()
            logging.debug(f"Using icon from {icon_path} {len(install_request.app_info.icon.png_data)} bytes")

    last_build_id = read_builder_cache(path)
    if last_build_id:
        logging.debug(f"Using last build ID from cache: {last_build_id}")
        install_request.prev_build_id = last_build_id
    return install_request


def build_and_upload_app(path_str: str, override_url : str | None = None, override_token : str | None = None, make_default : bool = False) -> int:
    path = Path(path_str).resolve()
    
    if not path.is_dir():
        raise NotADirectoryError(f"i have to add support for this back")
    logging.info(f"Building app from folder: {path}")
    install_request = build_from_folder(path)
    if install_request is None:
        logging.error(f"Failed to build app from {path}!")
        return 1
    
    app_id = install_request.app_id
    if make_default:
        install_request.make_default = True
        logging.warning(f"Making this app a default for all users")
    logging.info("App Built! Connecting to your Truffle.")
    client = TruffleOSClient() #todo: override url missing 
    client.authenticate() 
    #todo: override token missing
    # - just make all cmds take a shared base args set, hyphae --token 1234 build etc..
    
    resp : AppInstallResponse = client.app_install(install_request)
    logging.info(f"App install response: {resp}")
    
    if resp.HasField('error'):
        logging.error(f"Error from server: {resp.error}")
        return 1
    assert len(resp.token) > 0, "Server did not return a token"
    assert len(resp.app_id) > 0, "Server did not return an app ID"

    build_id = resp.build_id
    token = resp.token
    if not build_id or not token:
        logging.error(f"Failed to get build ID or token from server: {resp}")
        return 1
    

    if resp.app_id != app_id:
        if len(app_id):
            logging.warning(f"App ID mismatch: expected {app_id}, got {resp.app_id}. Using {resp.app_id} for upload.")
        config = get_config(path_str)
        config['app_uuid'] = resp.app_id
        save_config(path_str, config)
    
    output_file = path / f"{path.stem}.hyphae"
    if output_file.exists():
        logging.warning(f"Output file {output_file} already exists, removing it before building.")
        os.unlink(output_file) 
    output_file = _make_zip(path, output_file)
    logging.debug("waiting for build server to be ready")
    time.sleep(1) # FIXME - build server can race by a few 

    build_url = "http://" + client.url + "/build/" + token 
    logging.info(f"Build URL: {build_url}")
    upload_to_build(output_file, build_url, build_id)
    logging.info(f"App uploaded successfully with build ID: {build_id}")
    write_builder_cache(path, build_id)

    return 0

def connect(override_url: str | None, override_userid: str | None = None) -> int:
    logging.info("Connecting...")
    try:
        client = TruffleOSClient(override_url=override_url)
        client.authenticate() 
        logging.info("Connected!")
        return 0
    except Exception as e:
        logging.error(f"Failed to connect: {e}")
        print(traceback.format_exc())
        return 1
    
    



def main():
    parser = argparse.ArgumentParser(description="Hyphae CLI for TruffleOS agentic applications")
    subparsers = parser.add_subparsers(dest='command')

    

    upload_parser = subparsers.add_parser('upload', help='upload an app to your truffle')
    upload_parser.add_argument('path', type=str, help='path to app', default=os.getcwd())
    upload_parser.add_argument('--url', type=str, help='truffle url', default='https://dls.22.itsalltruffles.com')
    upload_parser.add_argument('--token', type=str, help='session', default='')
    upload_parser.add_argument('--default-app', action='store_true', help='make this a default app for all users')
    build_parser = subparsers.add_parser('build', help='build an app into a .hyphae bundle')
    build_parser.add_argument('path', type=str, help='path to app', default='.')
    

    connect_parser = subparsers.add_parser('connect', help='connect to a truffle')
    connect_parser.add_argument('--url', type=str, help='override truffle url', default='', required=False)
    connect_parser.add_argument('--userid', type=str, help="override 4-8 digit user id", default='', required=False)
    creds_parser = subparsers.add_parser('creds', help='manage credentials')
    creds_subparsers = creds_parser.add_subparsers(dest='creds_command', required=True)
    cred_list_parser = creds_subparsers.add_parser('list', help='list current credentials')
    cred_list_parser.add_argument('-v', '--verbose', action='store_true', help='show verbose output <WITH SECRETS>')
    clear_parser = creds_subparsers.add_parser('clear', help='clear  credentials')
    clear_parser.add_argument('--url', type=str, help='URL to clear credentials for', default="")
    clear_parser.add_argument('--current', action='store_true', help='skip confirmation prompt')
    set_parser = creds_subparsers.add_parser('set', help='set credentials for a URL')
    set_parser.add_argument('url', type=str, help='URL to set credentials for')
    set_parser.add_argument('token', type=str, help='Token to set for the URL')
    get_parser = creds_subparsers.add_parser('get', help='get credentials for a URL')
    get_parser.add_argument('url', type=str, help='URL to get credentials for')
    args = parser.parse_args()
    err = 1
    if args.command == 'upload':
        err = build_and_upload_app(args.path, args.url, args.token, args.default_app)
    elif args.command == 'build':
        err = build_app(args.path)
    elif args.command == 'connect':
        override_url = args.url if args.url else None
        err = connect(override_url, args.userid)
    elif args.command == 'creds':
        if args.creds_command == 'list':
            from hyphae.cmd.creds import creds_cmd
            creds_cmd(args.verbose)
            err = 0
        elif args.creds_command == 'clear':
            print(args)
            url = None
            from hyphae.cmd.creds import delete_token_for_url, get_current_url, has_token_for_url
            if args.url and len(args.url) > 0 and not args.current:
                logging.debug(f"Clearing credentials for URL: {args.url}")
                url = args.url
            elif args.current:
                logging.debug("Clearing credentials for current URL")
                from hyphae.cmd.creds import get_token_for_url
                url = get_current_url()
            if url:
                if not has_token_for_url(url):
                    logging.error(f"No credentials found for {url}")
                    exit(1)
                delete_token_for_url(url)
            else:
                logging.error("No current URL found to clear credentials for.")
                raise ValueError("No current URL found to clear credentials for.")

            logging.info(f"Cleared credentials for {url}")
            err = 0
        elif args.creds_command == 'set':
            from hyphae.cmd.creds import set_token_for_url
            set_token_for_url(args.url, args.token)
            logging.info(f"Set credentials for {args.url}")
            err = 0
        elif args.creds_command == 'get':
            from hyphae.cmd.creds import get_token_for_url
            token = get_token_for_url(args.url)
            if token:
                print(f"Token for {args.url}: {token}")
                err = 0
            else:
                print(f"No credentials found for {args.url}")
                err = 1
    else:
        parser.print_help()
        err = 1
    exit(err)

if __name__ == "__main__":
    main()
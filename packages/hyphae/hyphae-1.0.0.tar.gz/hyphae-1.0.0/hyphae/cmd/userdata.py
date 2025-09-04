import os
import sys
import webbrowser
from pathlib import Path
import logging




def get_client_userdata_dir() -> Path:
    if sys.platform == "win32": base = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    elif sys.platform == "darwin": base = os.path.expanduser("~/Library/Application Support")
    else: base = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    CLIENT_DIR_NAME = "TruffleOS-Development" if os.getenv("TRUFFLE_CLIENT_DEV", False) else "TruffleOS"
    userdata = Path(os.path.join(base, CLIENT_DIR_NAME))
    logging.debug(f"User data directory resolved to: {userdata}")
    if not userdata.exists():
        logging.error(f"User data directory {userdata} does not exist")
        logging.error("Please make sure you have Truffle OS installed")
        logging.info("Opening download link... (https://itsalltruffles.com/)")
        webbrowser.open("https://itsalltruffles.com/", new=0, autoraise=True)
        exit(1)
    if not userdata.is_dir(): raise ValueError(f"User data directory {userdata} is not a directory")
    logging.debug(f"get_client_userdata_dir() -> {userdata}")
    return userdata


def get_user_id() -> str:
    if os.getenv("TRUFFLE_CLIENT_ID"):
        return os.getenv("TRUFFLE_CLIENT_ID","")
    try:
        userdata = get_client_userdata_dir()
        user_id_path = userdata / "magic-number.txt"
        if not user_id_path.exists():
            raise ValueError(f"Magic Number file @{user_id_path} does not exist")
        with open(user_id_path, 'r') as f:
            user_id = f.read().strip()
        if not user_id or len(user_id) < 6:
            raise ValueError(f"Magic Number file @{user_id_path} is empty/too short {len(user_id)}")
        
        if not user_id.isdigit():
            raise ValueError(f"Magic Number file @{user_id_path} is not a number")
        if user_id == "1234567891":
            raise ValueError(f"Magic Number file @{user_id_path} is the placeholder number")
        return user_id
    except Exception as e:
        logging.error(f"Error getting user ID: {e}")
        raise


def get_base_url() -> str:
    url = ""
    try:
       path = get_client_userdata_dir()
       url_file = path / "current-url"
       if url_file.exists():
            with open(url_file, "r") as f:
                url_file_contents = f.read().strip()
                if url_file_contents:
                    if len(url_file_contents) <= 0: 
                        raise ValueError("URL file is empty")
                    url = url_file_contents
                    logging.debug(f"Using URL from file: {url}")
    except Exception as e:
        logging.error(f"Error getting base URL fron client: {str(e)}")
    if os.getenv("TRUFFLE_CLIENT_URL"):
        url = os.getenv("TRUFFLE_CLIENT_URL", url)
        logging.debug(f"Using URL from environment variable: {url}")
    if not url or len(url) <= 0:
        raise ValueError("Can't automatically find your Truffle's URL!")
    logging.debug(f"Using URL-  {url}")
    if url.find("http://") != -1:
        logging.warning("Base URL should not be http://, using https:// instead")
        url = url.replace("http://", "https://")
    if url[-1] == "/":
        url = url[:-1]
    return url
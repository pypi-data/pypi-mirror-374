import keyring
import keyring.backends
import keyring.backends.fail
import logging

try:
    key_backend = keyring.get_keyring()
    if key_backend is None or isinstance(key_backend, keyring.backends.fail):
        raise RuntimeError("discovery failed")
    logging.debug(f"Keyring backend: {key_backend}")
except Exception as e:
    logging.warning("Keyring backend init failed, Truffle credentials may not be stored securely.")

    
_SERVICE = "hyphae"


def set_token_for_url(url: str, token: str) -> None:
    keyring.set_password(_SERVICE, url, token)

def get_token_for_url(url: str) -> str | None:
    return keyring.get_password(_SERVICE, url)

def has_token_for_url(url: str) -> bool:
    return get_token_for_url(url) is not None

def delete_token_for_url(url: str) -> None:
    keyring.delete_password(_SERVICE, url)

def strip_url(url : str):
    if url.startswith("https://"):
        url = url.replace("https://", "")
    elif url.startswith("http://"):
        url = url.replace("http://", "")
    if url.find(":"):
        url = url.split(":")[0]
    return url

def resolve_url(url : str, port: int = 80) -> str:
    if url is None or len(url) <= 0:
        raise ValueError("URL cannot be None or empty")
    url = strip_url(url)
    if url.endswith(".local"):
        import socket
        url = socket.gethostbyname(url)
    url = f"{url}:{port}"
    return url

def get_current_url() -> str:
    from hyphae.cmd.userdata import get_base_url
    url = get_base_url()
    if not url or len(url) <= 0:
        raise ValueError("No current device found from Truffle Client")
    return resolve_url(url)

def creds_cmd(show_secrets: bool = False ) -> int:
    """
    Command to manage credentials.
    If show_secrets is True, it will show the tokens.
    """
    from hyphae.cmd.userdata import get_base_url
    base_url = get_base_url()
    if not base_url or len(base_url) <= 0:
        logging.error("No current device found from Truffle Client")
        return 1
    url = resolve_url(base_url)
    logging.debug(f"Creds: Using URL: {url}")
   

    token = get_token_for_url(url)
    if not token or len(token) <= 0:
        logging.info(f"No credential found for: {url}")
        return 1
    
    print("Truffle Client Credentials:")
    print(f"URL: {url}")
    if show_secrets:
        print(f"Token: {token}")
    else:
        print("Token: [hidden]")
    return 0
    


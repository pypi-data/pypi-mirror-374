
import logging 
from typing import Any
import os

def _determine_log_level() -> int:
    if os.getenv("HYPHAE_LOG_DEBUG", None) is not None:
        print("Debug logging enabled")
        return logging.DEBUG
    return logging.INFO

logging.basicConfig(
    level=_determine_log_level(),
    format="%(asctime)s.%(msecs)03d [%(levelname).1s] T%(thread)d: %(message)s",
    datefmt="%H:%M:%S"
)




#greasy
# import sys, os
# def add_to_python_path(new_path):
#     existing_path = sys.path
#     absolute_path = os.path.abspath(new_path)
#     if absolute_path not in existing_path:
#         sys.path.append(absolute_path)
#     return sys.path
# add_to_python_path(os.path.dirname(os.path.abspath(__file__)))



from hyphae.api import get_app_env_state

from .runtime import Runtime, tool, args, group, app, flags, HOST

def run(class_instance: Any) -> Any:
    logging.info(f"Building and running Truffle app: {class_instance.__class__.__name__}")
    rt = Runtime()()
    return rt.build(class_instance)
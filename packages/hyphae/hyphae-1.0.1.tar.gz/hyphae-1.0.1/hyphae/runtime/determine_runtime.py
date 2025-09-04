from enum import Enum
import os

class RuntimeType(Enum):
    DEV = 0,
    CLIENT = 1,
    TRUFFLE = 2

def determine_runtime() -> RuntimeType:
    
    rt_envvar = os.getenv("TRUFFLE_RUNTIME")
    if rt_envvar is None:
        # Default to CLIENT if the environment variable is not set
        return RuntimeType.TRUFFLE
    if rt_envvar and rt_envvar == "CLIENT": 
        return RuntimeType.CLIENT
    return RuntimeType.TRUFFLE


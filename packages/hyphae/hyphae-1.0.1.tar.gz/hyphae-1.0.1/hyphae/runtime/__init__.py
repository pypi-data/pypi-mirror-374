import typing
import logging
from .decs import tool_decorator, args_decorator, group_decorator, flags_decorator


from .determine_runtime import determine_runtime, RuntimeType

HOST = determine_runtime()



if HOST in [RuntimeType.TRUFFLE, RuntimeType.DEV]:
    from .truffle_runtime import TruffleRuntime
    logging.debug("Using proprietary runtime")
elif HOST == RuntimeType.CLIENT:
    logging.debug("Using public runtime")
    from .public import TruffleClientRuntime as TruffleRuntime
else:
    raise ValueError(f"Invalid runtime type: {HOST}")


def Runtime():
    return TruffleRuntime

def group(name: str, leader: bool = False):
    return group_decorator(name, leader)

def tool(description: str = None, icon: str = None, predicate: typing.Callable = None):
    return tool_decorator(description, icon, predicate)

def flags(**kwargs):
    return flags_decorator(**kwargs)  

def args(**kwargs):
    return args_decorator(**kwargs)
    
def app(**kwargs):
    def decorator(func):
        return func 
    return decorator

import typing

from .base import *
import logging


def tool_decorator(description: str = None, icon: str = None, predicate: typing.Callable = None):
    def decorator(func):
        assert verify_func(func), f"Function {func.__name__} cannot be a tool"
        func.__truffle_tool__ = True
        func.__truffle_description__ = description
        func.__truffle_icon__ = icon

        func_attrs = ["__truffle_args__", "__truffle_group__", "__truffle_flags__"]
        for attr in func_attrs:
            if not hasattr(func, attr):
                setattr(func, attr, None)

        
        
        if predicate is not None:
            assert verify_predicate(predicate), f"Function {func.__name__} has an invalid predicate"
            func.__truffle_predicate__ = predicate
        logging.debug(f"@truffle.tool({description},{icon}) - {func.__name__} {' - predicate' if predicate else ''}")
        return func
    return decorator

def args_decorator(**kwargs):
    def decorator(func):
        assert verify_arg_descriptions(func.__name__, kwargs)
        func.__truffle_args__ = kwargs

        logging.debug(f"@truffle.args({kwargs}) for function: {func.__name__}")
        return func
    return decorator

def group_decorator(name: str, leader: bool = False): 
    def decorator(func):
        assert verify_func(func), f"Function {func.__name__} cannot be a group"
        func.__truffle_group__ = name
        func.__truffle_group_leader__ = leader
        logging.debug(f"@truffle.group({name}, {leader}) - {func.__name__}")
        return func
    return decorator

def flags_decorator(**kwargs):
    def decorator(func):
        func.__truffle_flags__ = "nonblock" #todo: make list in future 
        logging.debug(f"@truffle.flags({kwargs}) - {func.__name__}")
        return func
    return decorator
import abc 
import typing
import inspect
import json 

import logging

class BaseRuntime(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build(self, class_instance: typing.Any) -> None:
        pass


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


def get_members(obj : typing.Any, pred: typing.Callable) -> typing.Dict[str, typing.Any]:
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and pred(value):
            pr[name] = value
    return pr

def get_non_function_members(obj):
    return get_members(obj, lambda o: not inspect.ismethod(o))

def get_function_members(obj):
    return get_members(obj, inspect.ismethod)
    

def args_from_func(func : typing.Callable) -> typing.Dict[str, typing.Any]:
    type_hints = typing.get_type_hints(func)
    assert callable(func), f"Expected a function, got type: {type(func)} {func}."
    assert type_hints, f"Function {func.__name__} must have type hints."
    
    assert "return" in type_hints, f"Function {func.__name__} must have a return value and type hint."

    args_dict = {}
    for param_name, param in type_hints.items():
        param_type = type_hints.get(param_name, type(None))
        assert param_type.__name__ != "NoneType", (
            f"Function {func.__name__}: Parameter '{param_name}' has no type hint. Make sure to include a type hint."
        )
        args_dict[param_name] = param_type

    assert "return" in args_dict, f"Args dict missing return value for function {func.__name__}."
    return args_dict


def get_truffle_tool_fns(obj):
    tools = {}
    for name, func in get_function_members(obj).items():
        if hasattr(func, "__truffle_tool__"):
            if hasattr(func, "__self__"):
                tools[name] = func.__func__
            else:
                tools[name] = func
                logging.warning(f"Function {func.__name__} missing self parameter. Trying to make it work.")
    assert tools != {}, f"Class {obj.__class__.__name__} has no truffle tools defined, don't forget to add @truffle.tool to your functions."
    return tools


def verify_func(func : typing.Callable) -> bool:
    assert len(args_from_func(func)), f"Function {func.__name__} invalid"
    return True

def verify_arg_descriptions(fn_name :str, kwargs : typing.Dict[str, typing.Any]) -> bool:
    assert kwargs != None, f"{fn_name} - truffle.args() requires at least one [name, description] pair, got none"
    assert len(kwargs) > 0, f"{fn_name} - truffle.args() requires at least one [name, description] pair, got none"
    for key, value in kwargs.items():
        assert isinstance(key, str),   f"{fn_name}.args({key}='{value}') - Expected string, got type {type(key)} {key}."
        assert isinstance(value, str), f"{fn_name}.args({key}='{value}') - Expected string, got type {type(value)} {value}."
    return True


def verify_predicate(func : typing.Callable) -> bool:
    
    assert callable(func), f"Predicate {func.__name__} must be callable"
    assert inspect.isfunction(func), f"Predicate {func.__name__} must be a function"
    # assert no args, except self
    params = [p for p in inspect.signature(func).parameters.values() if p.name != 'self']
    assert len(params) == 0, f"Predicate {func.__name__} must have no arguments (excluding 'self')"
    ret_ann = inspect.signature(func).return_annotation
    assert ret_ann in (bool, inspect.Signature.empty), \
        f"Predicate {func.__name__} must return a bool or have no annotation (lambda)"
    return True


def check_groups(obj : typing.Any) -> bool:
    groups = {}
    for name, func in get_function_members(obj).items():
        if getattr(func, "__truffle_group__", None) is not None:
            is_leader = getattr(func, "__truffle_group_leader__", False)
            group_name = str(func.__truffle_group__)
            if group_name not in groups:
                groups[group_name] = {"leaders": [], "members": []}
            if is_leader:
                groups[group_name]["leaders"].append(func)
            else:
                groups[group_name]["members"].append(func)

    for group_name, group in groups.items():
        assert len(group["leaders"]) > 0, f"Group {group_name} has no leaders, so all tools in the group will be ignored."
        if len(group["members"]) == 0:
            logging.warning(f"Group {group_name} has no members, so all tools in the group will be available")

    return True

def verify_arg_types(name: str, args: typing.Dict[str, typing.Any]) -> bool:
    for arg_name, arg_type in args.items():
        
        allowed_arg_types = [str, int, float, bool, list, dict]
        allowed_return_types = [str, int, float, bool, list, dict]
        
        if arg_name == 'return':
            assert any(arg_type is t for t in allowed_return_types) or hasattr(arg_type, "__origin__"), \
                f"Function {name} return type has invalid type: {arg_type}. Must be one of: {', '.join(t.__name__ for t in allowed_return_types)}"
        else:
            assert any(arg_type is t for t in allowed_arg_types) or hasattr(arg_type, "__origin__"), \
                f"Function {name} argument {arg_name} has invalid type: {arg_type}. Must be one of: {', '.join(t.__name__ for t in allowed_arg_types)}"
        
        if hasattr(arg_type, "__origin__"):
            origin = arg_type.__origin__
            assert origin in (list, dict), f"Function {name} argument {arg_name} uses unsupported generic type: {origin}"
            
            for inner_type in arg_type.__args__:
                assert inner_type in allowed_arg_types and not (hasattr(inner_type, "__origin__") and inner_type.__origin__ is typing.Union), \
                f"Function {name} argument {arg_name} has invalid inner type: {inner_type}. Optional types are not supported."
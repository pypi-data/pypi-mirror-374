import logging
from .base import *
from dataclasses import is_dataclass




class TruffleClientRuntime(BaseRuntime):
    def __init__(self):
        self.cls = None

    def build(self, class_instance):
        self.cls = class_instance
        
        # assert tools != {} inside 
        tool_fns = get_truffle_tool_fns(self.cls)

        check_groups(self.cls)

        for name , func in tool_fns.items():
            # must have args and types for args
            args = args_from_func(func)
            assert args != None, f"Function {func.__name__} invalid"
            
            verify_arg_types(name, args) # this can be dome in decs tbh
        
        # maybeeee fuzz every tool ??

        logging.info("Validated all tools, building Truffle app...")
        return self.cls
    


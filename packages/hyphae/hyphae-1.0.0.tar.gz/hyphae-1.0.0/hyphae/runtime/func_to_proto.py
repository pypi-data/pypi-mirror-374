
import typing
import inspect
import copy 
import logging

from datetime import datetime
import dataclasses

from collections import OrderedDict

# ALL THE PROTOBUF AND GRPC CODE. TRUFFLE RUNTIME AT EOF 
from google.protobuf import  timestamp_pb2
from google.protobuf.descriptor import  Descriptor, FieldDescriptor, EnumDescriptor
from google.protobuf import descriptor_pool, descriptor_pb2

from google.protobuf import message as message_ 

from .base import *
import truffle.hyphae.annotations_pb2 as annotations_pb2
from truffle.common.app_tool_pb2 import AppTool

from .proto_conv_common import to_upper_camel, add_fd_to_pool, desc_to_message_class, is_numeric_field, is_float_field
class FuncToProto:
    def __init__(self, func: typing.Callable, package: str, tool_pb: AppTool | None = None):
        self.func = func
        self.package = package
      
        self.imports = set() 
        self.imports.add("truffle/hyphae/annotations.proto")
        #fd_pb.dependency.append("truffle/hyphae/annotations.proto")
        self.pool : descriptor_pool.DescriptorPool = descriptor_pool.Default()
        self.name : str = to_upper_camel(func.__name__) #protobufs are picky! 
        
        self.type_mapping  = {
       #     typing.Any: any_pb2.Any, #the people do not deserve this 
            bool: FieldDescriptor.TYPE_BOOL,
            str: FieldDescriptor.TYPE_STRING,
            bytes: FieldDescriptor.TYPE_BYTES,
            datetime: timestamp_pb2.Timestamp,
            float: FieldDescriptor.TYPE_DOUBLE,
            int: FieldDescriptor.TYPE_INT64,
        }

        self.tool_pb = tool_pb if tool_pb is not None else AppTool()
        self.args_dict = args_from_func(func)
        self.tool_pb
        self.field_num_dict = OrderedDict(
            (name, i) for i, name in enumerate(self.args_dict.keys())
        )

        self.input_type, self.output_type = self.make_fake_types(self.name, self.args_dict)

        # self.input_desc = self.convert(self.input_type)
        # self.output_desc = self.convert(self.output_type)

        self.input_desc, self.output_desc = self.convert2(self.input_type, self.output_type)
   
        # clear imports? - nahhhhh


    def descriptors(self) -> typing.Tuple[Descriptor, Descriptor]:
        return self.input_desc, self.output_desc
    def message_classes(self) -> typing.Tuple[typing.Type, typing.Type]:
        return desc_to_message_class(self.input_desc), desc_to_message_class(self.output_desc)
    

    
    def make_fake_types(self, name : str, args_dict: typing.Dict[str, typing.Any] ) -> typing.Tuple[typing.Type, typing.Type]:
        ret_args ={ 'return_value': args_dict['return']}
        output_type = type(name + "Return", (object,), ret_args)
        args_dict.pop('return')
        input_type = type(name + "Args", (object,), args_dict)
        return input_type, output_type
    def make_fake_type(self, name : str, args_dict: typing.Dict[str, typing.Any] ) -> typing.Tuple[typing.Type, typing.Type]:
        return type(name, (object,), args_dict)
   
    def convert2(self, in_type : typing.Any, out_type : typing.Any) -> typing.Tuple[Descriptor, Descriptor]:
        msg_types : typing.List[descriptor_pb2.DescriptorProto] = [
            self._type_to_desc_pb(in_type),
            self._type_to_desc_pb(out_type)
        ]
        full_input_name = f"{self.package}.{msg_types[0].name}"
        full_output_name = f"{self.package}.{msg_types[1].name}"
        # merge msg_types + nested types 
        
        full_name = f"{self.package}.{self.name}"
        fd_pb = descriptor_pb2.FileDescriptorProto(
            name=f"{full_name}.proto",
            package=self.package,
            syntax="proto3",
            dependency=sorted(list(self.imports)),
            message_type=msg_types
        )
        logging.debug(f"Converting: {full_name} {full_input_name} {full_output_name} {list(self.imports)}")
        add_fd_to_pool(fd_pb, self.pool)
        logging.debug(f"Added {full_name} to pool")
        return self.pool.FindMessageTypeByName(full_input_name), self.pool.FindMessageTypeByName(full_output_name)
    def _type_to_desc_pb(self, type_: typing.Any) -> descriptor_pb2.DescriptorProto:
        typename: str = type_.__name__
        desc_pb : descriptor_pb2.DescriptorProto = self._conv(typename, type_)

        #add truffle arg annotations
        for field in desc_pb.field:
            if self.tool_pb.tool_args and field.name in self.tool_pb.tool_args:
                field.options.Extensions[annotations_pb2.arg_description] = self.tool_pb.tool_args[field.name]

        for nested in desc_pb.nested_type:
            
            if self.tool_pb.tool_args and nested.name in self.tool_pb.tool_args:
                nested.options.Extensions[annotations_pb2.arg_description] = self.tool_pb.tool_args[nested.name]

        return desc_pb
    def convert(self, type_ : typing.Any) -> Descriptor:
        typename: str = type_.__name__
        desc_pb = self._type_to_desc_pb(type_)
        fd_pb = descriptor_pb2.FileDescriptorProto(
            name=f"{self.package}.{typename.lower()}.proto",
            package=self.package,
            syntax="proto3",
            dependency=sorted(list(self.imports)),
            message_type=[desc_pb]
        )
        add_fd_to_pool(fd_pb, self.pool)
        full_name = f"{self.package}.{typename}"
        logging.debug(f"Converted: {full_name}")
        return self.pool.FindMessageTypeByName(full_name)

    def _conv(self, name : str, entry : typing.Any) -> descriptor_pb2.DescriptorProto:

        #concrete types
        concrete_type = self.get_concrete_type(entry)
        if concrete_type:
            return self._convert_concrete_type(concrete_type)

        # dicts 
        map_info = self.get_map_key_val_types(entry)
        if map_info:
            return self._convert_map(name, *map_info)

        # returns the final descriptor_pb2.DescriptorProto
        if dataclasses.is_dataclass(entry):
            logging.debug(f"Converting dataclass {name} to protobuf")
            return self._convert_dataclass(name, entry)
        
        
        message_fields = self.get_message_fields(entry)
        if message_fields is not None:
            logging.debug(f"MESSAGE: {name} with fields {message_fields}")
            return self._convert_message(name, entry, message_fields)
        
        raise ValueError(f"Got unsupported entry type({type(entry)}) {entry} for {name}")

    def get_concrete_type(self, entry_type: typing.Any) -> typing.Optional[typing.Type]:
        if entry_type in self.type_mapping or isinstance( entry_type, Descriptor):
           return entry_type
        descriptor_attr = getattr(entry_type, "DESCRIPTOR", None)
        if descriptor_attr is not None:
            return descriptor_attr
        return None
    
    def get_map_key_val_types(self, entry: typing.Any) -> typing.Optional[typing.Tuple[typing.Type, typing.Type]]:
        if typing.get_origin(entry) is dict:
            key_type, val_type = typing.get_args(entry)
            print(key_type, val_type)
            return (
                self._conv("key", key_type),
                self._conv("value", val_type),
            )
        return None
    def get_message_fields(self, entry: typing.Any) -> typing.Optional[typing.Dict[str, descriptor_pb2.FieldDescriptorProto]]:
        obj = entry
        pr = {}
        if issubclass(entry, message_.Message):
            logging.debug(f"Converting protobuf message {entry} to descriptor")
            for field in entry.DESCRIPTOR.fields:
                pr[field.name] = field
            return pr
        for name in dir(obj):
            value = getattr(obj, name)
            if not name.startswith("__") and not inspect.ismethod(value):
                pr[name] = value
            elif dataclasses.is_dataclass(value):
                pr[name] = value
        pr = [(name, value) for name, value in pr.items()]
        return pr
   
    def _convert_concrete_type(self, concrete_type: typing.Type) -> Descriptor:
        entry_type = self.type_mapping.get(concrete_type, concrete_type)
        pb_type_desc = None
        desc_ref = self._get_descriptor(entry_type)
        if desc_ref is not None:
            pb_type_desc = desc_ref
        else:
            if concrete_type not in self.type_mapping:
                raise ValueError(f"Unsupported type {concrete_type}")
            pb_type_value = self.type_mapping[concrete_type]
            pb_type_desc = getattr(pb_type_value, "DESCRIPTOR", None)
            if pb_type_desc is None:
                if not isinstance(pb_type_value, int):
                    raise ValueError(f"Unsupported type {concrete_type}")
                pb_type_desc = pb_type_value
        if isinstance(pb_type_desc,Descriptor):
            self._add_import(pb_type_desc)
            logging.debug("Added descriptor to imports {pb_type_desc.name}")
        return pb_type_desc



    def _convert_map(self, name: str, key_type: int, val_type: Descriptor) -> descriptor_pb2.DescriptorProto:
        nested_name = f"{to_upper_camel(name)}Entry"
        key_field = descriptor_pb2.FieldDescriptorProto(
            name="key",
            type=key_type,
            number=1
        )
        val_field_kwargs = {}
        msg_descriptor_kwargs = {}
        if isinstance(val_type, int):
            val_field_kwargs = {"type": val_type}
        elif isinstance(val_type, EnumDescriptor):
            val_field_kwargs = {
                "type": FieldDescriptor.TYPE_ENUM,
                "type_name": val_type.name,
            }
        elif isinstance(val_type, Descriptor):
            val_field_kwargs = {
                "type": FieldDescriptor.TYPE_MESSAGE,
                "type_name": val_type.name,
            }
        elif isinstance(val_type, descriptor_pb2.EnumDescriptorProto):
            val_field_kwargs = {
                "type": FieldDescriptor.TYPE_ENUM,
                "type_name": val_type.name,
            }
            msg_descriptor_kwargs["enum_type"] = [val_type]
        elif isinstance(val_type, descriptor_pb2.DescriptorProto):
            val_field_kwargs = {
                "type": FieldDescriptor.TYPE_MESSAGE,
                "type_name": val_type.name,
            }
            msg_descriptor_kwargs["nested_type"] = [val_type]
        else:
            raise ValueError(f"Unsupported map value type: {val_type} {val_type.name}")

        val_field = descriptor_pb2.FieldDescriptorProto(
            name="value",
            number=2,
            **val_field_kwargs,
        )
        nested = descriptor_pb2.DescriptorProto(
            name=nested_name,
            field=[key_field, val_field],
            options=descriptor_pb2.MessageOptions(map_entry=True),
            **msg_descriptor_kwargs,
        )
        return nested
    
    def _convert_dataclass(self, name: str, entry: typing.Any) -> descriptor_pb2.DescriptorProto:
        # Convert a dataclass to a protobuf message descriptor
        field_descriptors = []
        nested_messages = []
        nested_names = set()
        message_name = to_upper_camel(name)
        assert dataclasses.is_dataclass(entry), f"Entry {entry} is not a dataclass"

        fields = dataclasses.fields(entry)
        field_no = 1
        for field in fields:
            field_name = field.name
            field_type = field.type
            field_number = field_no
            field_no += 1

            
            # Get the field number based on the current length of field_descriptors

            field_kwargs = {
                "name": field_name,
                "number": field_number,
                "label": FieldDescriptor.LABEL_OPTIONAL,
            }

            if self.is_repeated_field(field_type):
                field_kwargs["label"] = FieldDescriptor.LABEL_REPEATED
            
            field_type = self.get_field_type(field_type)
            nested_name = self.get_field_type_name(field_type, field_name)

            nested_result = self._conv(entry=field_type, name=nested_name)
            nested_results = [(nested_result, {})]


            for nested, extra_kwargs in nested_results:
                nested_field_kwargs = copy.copy(field_kwargs)
                nested_field_kwargs.update(extra_kwargs)

                # int = pb type already 
                if isinstance(nested, int):
                    nested_field_kwargs["type"] = nested

                elif isinstance(nested, Descriptor):
                    nested_field_kwargs["type"] = (
                        FieldDescriptor.TYPE_MESSAGE
                    )
                    nested_field_kwargs["type_name"] = nested.full_name

                elif isinstance(nested, descriptor_pb2.DescriptorProto):
                    nested_field_kwargs["type"] = (
                        FieldDescriptor.TYPE_MESSAGE
                    )
                    nested_field_kwargs["type_name"] = nested.name
                    nested_messages.append(nested)

                    if nested.options.map_entry: # maps only
                        nested_field_kwargs["label"] = (
                            FieldDescriptor.LABEL_REPEATED
                        )

                        while nested.nested_type:
                            nested_type = nested.nested_type.pop()
                            plain_name = nested_type.name
                            nested_name = to_upper_camel(
                                "_".join([field_name, plain_name])
                            )
                            nested_type.MergeFrom(
                                descriptor_pb2.DescriptorProto(name=nested_name)
                            )
                            for field in nested.field:
                                if field.type_name == plain_name:
                                    field.MergeFrom(
                                        descriptor_pb2.FieldDescriptorProto(
                                            type_name=nested_name
                                        )
                                    )

                            nested_messages.append(nested_type)
                                    #end maps only

                field_descriptors.append(
                                                    descriptor_pb2.FieldDescriptorProto(**nested_field_kwargs)
                                                )


                nested_messages = list({nested.name: nested for nested in nested_messages}.values())

                descriptor_proto = descriptor_pb2.DescriptorProto(
                    name=message_name,
                    field=field_descriptors,
                    nested_type=nested_messages
                )
                return descriptor_proto  
    def _convert_message(self, name: str, entry: typing.Any, message_fields: typing.Dict[str, descriptor_pb2.FieldDescriptorProto]) -> descriptor_pb2.DescriptorProto:
        #this mostly hasnt changed from IBM lib i stole it from
        field_descriptors = []
        nested_messages = []
        message_name = to_upper_camel(name)


      
        for field_name, field_def in message_fields:

            field_number = self.get_field_number(
                len(field_descriptors), field_def, field_name=field_name
            )
            field_kwargs = {
                "name": field_name,
                "number": field_number,
                "label": FieldDescriptor.LABEL_OPTIONAL,
            }

            if self.is_repeated_field(field_def):
                field_kwargs["label"] = FieldDescriptor.LABEL_REPEATED
            
            field_type = self.get_field_type(field_def)
            nested_name = self.get_field_type_name(field_type, field_name)
            nested_result = self._conv(entry=field_type, name=nested_name)
            nested_results = [(nested_result, {})]

            for nested, extra_kwargs in nested_results:
                nested_field_kwargs = copy.copy(field_kwargs)
                nested_field_kwargs.update(extra_kwargs)

                # int = pb type already 
                if isinstance(nested, int):
                    nested_field_kwargs["type"] = nested

                elif isinstance(nested, Descriptor):
                    nested_field_kwargs["type"] = (
                        FieldDescriptor.TYPE_MESSAGE
                    )
                    nested_field_kwargs["type_name"] = nested.full_name

                elif isinstance(nested, descriptor_pb2.DescriptorProto):
                    nested_field_kwargs["type"] = (
                        FieldDescriptor.TYPE_MESSAGE
                    )
                    nested_field_kwargs["type_name"] = nested.name
                    nested_messages.append(nested)

                    if nested.options.map_entry:
                        nested_field_kwargs["label"] = (
                            FieldDescriptor.LABEL_REPEATED
                        )

                        while nested.nested_type:
                            nested_type = nested.nested_type.pop()
                            plain_name = nested_type.name
                            nested_name = to_upper_camel(
                                "_".join([field_name, plain_name])
                            )
                            nested_type.MergeFrom(
                                descriptor_pb2.DescriptorProto(name=nested_name)
                            )
                            for field in nested.field:
                                if field.type_name == plain_name:
                                    field.MergeFrom(
                                        descriptor_pb2.FieldDescriptorProto(
                                            type_name=nested_name
                                        )
                                    )
                            nested_messages.append(nested_type)
                field_descriptors.append(
                    descriptor_pb2.FieldDescriptorProto(**nested_field_kwargs)
                )
        nested_messages = list({nested.name: nested for nested in nested_messages}.values())
        descriptor_proto = descriptor_pb2.DescriptorProto(
            name=message_name,
            field=field_descriptors,
            nested_type=nested_messages,
        )
        return descriptor_proto

    
    def _add_import(self, desc: Descriptor) -> None:
        import_file = desc.file.name
        if desc.file.pool != self.pool:
            fd_pb = descriptor_pb2.FileDescriptorProto()
            desc.file.CopyToProto(fd_pb)
            add_fd_to_pool(fd_pb, self.pool)
        self.imports.add(import_file)
    def _get_descriptor(self, entry: typing.Any) -> Descriptor:
        if isinstance(entry, Descriptor):
            return entry
        descriptor_attr = getattr(entry, "DESCRIPTOR", None)
        if descriptor_attr and isinstance(descriptor_attr, Descriptor):
            return descriptor_attr
        return None
    def get_field_type(self, field_def: typing.Any) -> typing.Any:
        if typing.get_origin(field_def) is list:
            args = typing.get_args(field_def)
            if len(args) == 1:
                return args[0]
        return field_def
    def get_field_type_name(self, field_def: typing.Any, field_name: str) -> str:
        if isinstance(field_def, type):
            return field_def.__name__
        return field_name
    def is_repeated_field(self, field_def: typing.Any) -> bool:
        return typing.get_origin(field_def) is list
    def get_field_number(self, num_fields: int, field_def: type, field_name: str) -> int:
        if self.field_num_dict and field_name in self.field_num_dict:
            return self.field_num_dict[field_name] + 1
        elif field_name == "return_value":
            return num_fields + 1
        else:
            logging.warning(f"Field {field_name} not found in field num dict")
        return num_fields + 1

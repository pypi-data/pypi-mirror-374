
from google.protobuf.descriptor import Descriptor, FieldDescriptor, MethodDescriptor, ServiceDescriptor
from google.protobuf import descriptor_pool, descriptor_pb2
from google import protobuf as pb
from grpc import Server 
import logging
import re
import typing
from truffle.common.app_tool_pb2 import AppTool
from dataclasses import dataclass

def to_upper_camel(snake_str: str) -> str:
    if not snake_str:
        return snake_str
    return (
        snake_str[0].upper()
        + re.sub("_([a-zA-Z])", lambda pat: pat.group(1).upper(), snake_str)[1:]
    )
def add_fd_to_pool(fd_pb: descriptor_pb2.FileDescriptorProto, pool: descriptor_pool.DescriptorPool) -> None:
    try:
        logging.debug(f"Adding {fd_pb.name} to pool")
        existing_fd = pool.FindFileByName(fd_pb.name)
        existing_pb = descriptor_pb2.FileDescriptorProto()
        existing_fd.CopyToProto(existing_pb)
        if (
            existing_pb.dependency != fd_pb.dependency and
            existing_pb.message_type.keys() != fd_pb.message_type.keys() and
            existing_pb.service.keys() != fd_pb.service.keys()
        ):
            raise TypeError(f"File {fd_pb.name} already exists in pool and is different") 
    except KeyError:
        try:
            pool.Add(fd_pb)
        except TypeError as te:
            logging.error(f"Error adding {fd_pb.name} to pool")
            raise
def desc_to_message_class(desc: Descriptor) -> typing.Type:
    try:
        message_class = desc._concrete_class
    except (TypeError, SystemError, AttributeError):
        # protobuf version compatibility
        if hasattr(pb.reflection.message_factory, "GetMessageClass"):
            message_class = pb.reflection.message_factory.GetMessageClass(desc)
        else:
            message_class = pb.reflection.message_factory.MessageFactory().GetPrototype(desc)
            
    for nested_message_descriptor in desc.nested_types:
        nested_message_class = desc_to_message_class(
            nested_message_descriptor
        )
        setattr(message_class, nested_message_descriptor.name, nested_message_class)

    return message_class
def is_numeric_field(field: FieldDescriptor):
    numeric_types = [
        FieldDescriptor.TYPE_DOUBLE,
        FieldDescriptor.TYPE_FLOAT,
        FieldDescriptor.TYPE_INT32,
        FieldDescriptor.TYPE_INT64,
        FieldDescriptor.TYPE_UINT32,
        FieldDescriptor.TYPE_UINT64,
        FieldDescriptor.TYPE_SINT32,
        FieldDescriptor.TYPE_SINT64,
        FieldDescriptor.TYPE_FIXED32,
        FieldDescriptor.TYPE_FIXED64,
        FieldDescriptor.TYPE_SFIXED32,
        FieldDescriptor.TYPE_SFIXED64,
    ]
    return field.type in numeric_types


def is_float_field(field: FieldDescriptor):
    return field.type in [FieldDescriptor.TYPE_DOUBLE, FieldDescriptor.TYPE_FLOAT]

class Service(object):
  def GetDescriptor():
    raise NotImplementedError
  def CallMethod(self, method_descriptor, rpc_controller,
                 request, done):
    raise NotImplementedError
  def GetRequestClass(self, method_descriptor):
    raise NotImplementedError

  def GetResponseClass(self, method_descriptor):
    raise NotImplementedError




@dataclass
class GRPCService:
    descriptor: ServiceDescriptor
    registration_function: typing.Callable[[Service, Server], None]
    client_stub_class: typing.Type
    service_class: typing.Type[Service]


@dataclass
class ToolMethod:
    func: typing.Callable
    method_desc: MethodDescriptor = None
    input_desc: Descriptor = None
    output_desc: Descriptor = None
    input_msg: typing.Type = None #actual python proto Message inst
    output_msg: typing.Type = None # ^
    wrapper_fn: typing.Callable = None
    predicate_fn: typing.Callable = None #for conditional masking
    group_name: str = None #for tool group availability
    tool_pb : AppTool = None #options for the tool, like name, description, icon, etc.





import typing
import types

import logging



import grpc
# ALL THE PROTOBUF AND GRPC CODE. TRUFFLE RUNTIME AT EOF 
from google.protobuf.descriptor import MethodDescriptor,   ServiceDescriptor
from google.protobuf.service_reflection import GeneratedServiceType
from google.protobuf import descriptor_pool, descriptor_pb2
# from google.protobuf import service
#from google.protobuf.ervice import Service
from google.protobuf.service_reflection import GeneratedServiceType
from .base import *
import truffle.hyphae.annotations_pb2 as annotations_pb2
from truffle.common.app_tool_pb2 import AppTool

from .proto_conv_common import ToolMethod, to_upper_camel, add_fd_to_pool, desc_to_message_class, GRPCService, Service
def methods_to_service( methods : typing.Dict[str, ToolMethod], package: str, app_name: str ) -> GRPCService:
    pool = descriptor_pool.Default()
    service_fd_proto = _methods_to_service_file_descriptor_proto(
        methods=methods, package=package, pool=pool, app_name=app_name
    )
    assert len(service_fd_proto.service) == 1, (
        f"File Descriptor {service_fd_proto.name} should only have one service"
    )
    service_descriptor_proto = service_fd_proto.service[0]

    add_fd_to_pool(service_fd_proto, pool)
    service_fullname = (
        service_fd_proto.package + "." + app_name
    )  # name if not package else ".".join([package, name])
    service_descriptor = pool.FindServiceByName(service_fullname)

    client_stub = _service_descriptor_to_client_stub(
        service_descriptor, service_descriptor_proto
    )
    registration_function = _service_descriptor_to_server_registration_function(
        service_descriptor, service_descriptor_proto
    )
    service_class = _service_descriptor_to_service(service_descriptor)
    return GRPCService(
        descriptor=service_descriptor,
        service_class=service_class,
        client_stub_class=client_stub,
        registration_function=registration_function,
    )


def _methods_to_service_file_descriptor_proto(methods : typing.Dict[str, ToolMethod], package: str, pool: descriptor_pool.DescriptorPool, app_name : str) -> descriptor_pb2.FileDescriptorProto:
  
    method_descriptor_protos: typing.List[descriptor_pb2.MethodDescriptorProto] = []
    imports: typing.List[str] = []
    imports.append("truffle/common/app_tool.proto")
    imports.append("truffle/hyphae/annotations.proto")
    for name, func in methods.items():
        input_descriptor = func.input_desc
        output_descriptor = func.output_desc
        method_pb =descriptor_pb2.MethodDescriptorProto(
                name=name,
                input_type=input_descriptor.full_name,  # this might be the bug lol
                output_type=output_descriptor.full_name,
                client_streaming=False,
                server_streaming=False,
            )
        tool_pb = func.tool_pb
        if tool_pb is not None:
            # method_pb.options.Extensions[annotations_pb2.tool_description] = tool_pb.tool_description or ""
            # method_pb.options.Extensions[annotations_pb2.tool_icon] = tool_pb.tool_icon.symbol if tool_pb.tool_icon and tool_pb.tool_icon.HasField('symbol') else ""
            # method_pb.options.Extensions[annotations_pb2.tool_name] = tool_pb.tool_name or func.func.__name__
            # method_pb.options.Extensions[annotations_pb2.flags] =  len(tool_pb.tool_flags.values()) or 0
            method_pb.options.Extensions[annotations_pb2.app_tool].CopyFrom(tool_pb)
        method_descriptor_protos.append(method_pb)
            
        imports.append(input_descriptor.file.name)
        imports.append(output_descriptor.file.name)

    imports = sorted(list(set(imports)))

    service_descriptor_proto = descriptor_pb2.ServiceDescriptorProto(
        name=app_name, method=method_descriptor_protos
    )
    logging.debug(f"Service Descriptor Proto: {service_descriptor_proto.name} with {len(service_descriptor_proto.method)} methods package {package} imports {imports}")


    fd_proto = descriptor_pb2.FileDescriptorProto(
        name=f"{package.lower()}.{app_name}.proto",
        package=package,
        syntax="proto3",
        dependency=imports,
        # **proto_kwargs,
        service=[service_descriptor_proto],
    )

    return fd_proto


def _service_descriptor_to_service( service_descriptor: ServiceDescriptor) -> typing.Type[Service]:
    return types.new_class(
        service_descriptor.name,
        (Service,),
        {"metaclass": GeneratedServiceType},
        lambda ns: ns.update({"DESCRIPTOR": service_descriptor}),
    )



def _service_descriptor_to_client_stub(
    service_descriptor: ServiceDescriptor,
    service_descriptor_proto: descriptor_pb2.ServiceDescriptorProto,
) -> typing.Type:
    """Generates a new client stub class from the service descriptor

    Args:
        service_descriptor:  google.protobuf.descriptor.ServiceDescriptor
            The ServiceDescriptor to generate a service interface for
        service_descriptor_proto:  google.protobuf.descriptor_pb2.ServiceDescriptorProto
            The descriptor proto for that service. This holds the I/O streaming information
            for each method
    """
    _assert_method_lists_same(service_descriptor, service_descriptor_proto)

    def _get_channel_func(
        channel: grpc.Channel, method: descriptor_pb2.MethodDescriptorProto
    ) -> typing.Callable:
        if method.client_streaming and method.server_streaming:
            return channel.stream_stream
        if not method.client_streaming and method.server_streaming:
            return channel.unary_stream
        if method.client_streaming and not method.server_streaming:
            return channel.stream_unary
        return channel.unary_unary

  
    def initializer(self, channel: grpc.Channel):
        for method, method_proto in zip(
            service_descriptor.methods, service_descriptor_proto.method
        ):
            setattr(self,method.name,
                _get_channel_func(channel, method_proto)(
                    _get_method_fullname(method),
                    request_serializer=desc_to_message_class(
                        method.input_type
                    ).SerializeToString,
                    response_deserializer=desc_to_message_class(
                        method.output_type
                    ).FromString,
                ),
            )
    return type(
        f"{service_descriptor.name}Stub",
        (object,),
        {
            "__init__": initializer,
        },
    )


def _service_descriptor_to_server_registration_function(
    service_descriptor: ServiceDescriptor,
    service_descriptor_proto: descriptor_pb2.ServiceDescriptorProto,
) -> typing.Callable[[Service, grpc.Server], None]:

    _assert_method_lists_same(service_descriptor, service_descriptor_proto)

    def _get_handler(method: descriptor_pb2.MethodDescriptorProto):
        if method.client_streaming and method.server_streaming:
            return grpc.stream_stream_rpc_method_handler
        if not method.client_streaming and method.server_streaming:
            return grpc.unary_stream_rpc_method_handler
        if method.client_streaming and not method.server_streaming:
            return grpc.stream_unary_rpc_method_handler
        return grpc.unary_unary_rpc_method_handler

    def registration_function(servicer: Service, server: grpc.Server):
        rpc_method_handlers = {
            method.name: _get_handler(method_proto)(
                getattr(servicer, method.name),
                request_deserializer=desc_to_message_class(
                    method.input_type
                ).FromString,
                response_serializer=desc_to_message_class(
                    method.output_type
                ).SerializeToString,
            )
            for method, method_proto in zip(
                service_descriptor.methods, service_descriptor_proto.method
            )
        }
        generic_handler = grpc.method_handlers_generic_handler(
            service_descriptor.full_name, rpc_method_handlers
        )
        server.add_generic_rpc_handlers((generic_handler,))

    return registration_function


def _get_method_fullname(method: MethodDescriptor):
    method_name_parts = method.full_name.split(".")
    return f"/{'.'.join(method_name_parts[:-1])}/{method_name_parts[-1]}"


def _assert_method_lists_same(
    service_descriptor: ServiceDescriptor,
    service_descriptor_proto: descriptor_pb2.ServiceDescriptorProto,
):
    assert len(service_descriptor.methods) == len(service_descriptor_proto.method), (
        f"Method count mismatch: {service_descriptor.full_name} has"
        f" {len(service_descriptor.methods)} methods but proto descriptor"
        f" {service_descriptor_proto.name} has {len(service_descriptor_proto.method)} methods"
    )

    for m1, m2 in zip(service_descriptor.methods, service_descriptor_proto.method):
        assert m1.name == m2.name, f"Method mismatch: {m1.name}, {m2.name}"


# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: input_message.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='input_message.proto',
  package='tutorial',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x13input_message.proto\x12\x08tutorial\"(\n\x0cInputMessage\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t'
)




_INPUTMESSAGE = _descriptor.Descriptor(
  name='InputMessage',
  full_name='tutorial.InputMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='tutorial.InputMessage.id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='tutorial.InputMessage.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=33,
  serialized_end=73,
)

DESCRIPTOR.message_types_by_name['InputMessage'] = _INPUTMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

InputMessage = _reflection.GeneratedProtocolMessageType('InputMessage', (_message.Message,), {
  'DESCRIPTOR' : _INPUTMESSAGE,
  '__module__' : 'input_message_pb2'
  # @@protoc_insertion_point(class_scope:tutorial.InputMessage)
  })
_sym_db.RegisterMessage(InputMessage)


# @@protoc_insertion_point(module_scope)

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: owr.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\towr.proto\x12\x03owr\"\x1e\n\x0c\x61liveRequest\x12\x0e\n\x06nodeid\x18\x01 \x01(\x05\"\x0f\n\raliveResponse\"C\n\nowrRequest\x12\x12\n\nreceiverid\x18\x01 \x01(\x05\x12\x10\n\x08senderid\x18\x02 \x01(\x05\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"\x1b\n\x0bowrResponse\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x32v\n\x03Owr\x12\x32\n\x0bsendMessage\x12\x0f.owr.owrRequest\x1a\x10.owr.owrResponse\"\x00\x12;\n\x10sendAliveMessage\x12\x11.owr.aliveRequest\x1a\x12.owr.aliveResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'owr_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ALIVEREQUEST._serialized_start=18
  _ALIVEREQUEST._serialized_end=48
  _ALIVERESPONSE._serialized_start=50
  _ALIVERESPONSE._serialized_end=65
  _OWRREQUEST._serialized_start=67
  _OWRREQUEST._serialized_end=134
  _OWRRESPONSE._serialized_start=136
  _OWRRESPONSE._serialized_end=163
  _OWR._serialized_start=165
  _OWR._serialized_end=283
# @@protoc_insertion_point(module_scope)

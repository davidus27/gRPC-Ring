#!/bin/bash -e

# build the protobuf files
python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. owr.proto
import logging
import sys
from concurrent import futures


import grpc
import owr_pb2
import owr_pb2_grpc

from dataclasses import dataclass

@dataclass
class NodeInfo:
    node_id: str = None
    previous: str = None
    next: str = None
    skeleton: str = None
    pivot: str = None
    

class Node(owr_pb2_grpc.OwrServicer):
    
    def __init__(self, node_context: NodeInfo):
        self.node_id = node_context.node_id
        self.previous = node_context.previous
        self.next = node_context.next
        self.skeleton = node_context.skeleton
        self.pivot = node_context.pivot
        self.is_ready = False


    def sendMessage(self, request, context):
        print("Received message: " + request.message)
        return owr_pb2.owrResponse(message='hello from node.py')

    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        owr_pb2_grpc.add_OwrServicer_to_server(Node(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()

    def create_skeleton():
        channel = grpc.insecure_channel()
        stub = owr_pb2_grpc.OwrStub(channel)
        response = stub.sendMessage(owr_pb2.owrRequest(message='hello from node.py'))
        print("Greeter client received: " + response.message)



# yields current, previous and next (ip,port) tuple
def get_ring_info(nodes_amount, ip, port):
    pivot = (ip, port) # first one
    for node_id in range(nodes_amount):
        previous = (ip, port + (node_id - 1) % nodes_amount)
        skeleton = (ip, port + node_id)
        next = (ip, port + (node_id + 1) % nodes_amount)
        yield node_id, pivot, previous, skeleton, next


def main():
    nodes_amount = 100
    port = 60000
    ip_address = "127.0.0.1"

    ring_generator = get_ring_info(nodes_amount, ip_address, port)
    for node_id, pivot, previous, skeleton, next in ring_generator:
        print("Pivot:", pivot)
        print("Previous:", previous)
        print("Skeleton:", skeleton)
        print("Next:", next)
        print("Id:", node_id)
        print()

    # create a ring



if __name__ == '__main__':
    logging.basicConfig()
    main()
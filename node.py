import logging
from concurrent import futures
from threading import Thread

import grpc
import owr_pb2
import owr_pb2_grpc

from dataclasses import dataclass
from enum import Enum

@dataclass
class NodeInfo:
    node_id: int = None
    previous: tuple = ()
    next: tuple = ()
    skeleton: tuple = ()
    pivot: tuple = ()

class Direction(Enum):
    NEXT = 0
    PREVIOUS = 1


class Connection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.channel: grpc.Channel = None
        self.stub = None

    def create_channel(self):
        self.channel = grpc.insecure_channel(self.ip + ":" + str(self.port))

    def create_stub(self):
        raise NotImplementedError

    def initialize_client(self):
        self.create_channel()
        self.create_stub()


class PivotConnection(Connection):
    def create_stub(self):
        self.stub = owr_pb2_grpc.PivotStub(self.channel)
    
    def send_am_alive(self, node_id: int):
        return self.stub.receive_alive_message(owr_pb2.alive_request(
            nodeid=node_id
        ))    

    def initialize_server(self, node: grpc.Server):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        owr_pb2_grpc.add_PivotServicer_to_server(node, server)
        server.add_insecure_port(self.ip + ":" + str(self.port))
        server.start()
        return server

class NodeConnection(Connection):
    def create_stub(self):
        self.stub = owr_pb2_grpc.OwrStub(self.channel)

    def send_message(self, sender_id: int, receiver_id: int, message: str, direction: Direction):
        return self.stub.receive_message(owr_pb2.owr_request(
            senderid=sender_id,
            receiverid=receiver_id,
            content=message,
            sending_direction=direction.value
        ))

    def initialize_server(self, node: grpc.Server):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        owr_pb2_grpc.add_OwrServicer_to_server(node, server)
        server.add_insecure_port(self.ip + ":" + str(self.port))
        server.start()
        return server


class Node(owr_pb2_grpc.OwrServicer):
    def __init__(self, node_context: NodeInfo):
        self.node_id = node_context.node_id
        self.is_node_ready = False

        self.previous_node = NodeConnection(*node_context.previous)
        self.skeleton_node = NodeConnection(*node_context.skeleton)
        self.next_node = NodeConnection(*node_context.next)
        self.pivot_node = PivotConnection(*node_context.pivot)


    def receive_message(self, request, context):
        # check if the message is for this node
        logging.info("I am node " + str(self.node_id) + ", message is from " + str(request.senderid) + " to " + str(request.receiverid))

        if request.receiverid == self.node_id:
            logging.info("This message is for me")
            logging.info("Message content: " + str(request.content))
            return owr_pb2.owr_response()
        
        # if not, forward the message to the next node
        direction = Direction(request.sending_direction)
        self.inject_message(request.receiverid, request.content, direction)

        return owr_pb2.owr_response()

    def __send_alive_message(self):
        response = self.pivot_node.send_am_alive(self.node_id)
        logging.info("Alive message sent to pivot node")
        return response

    def inject_message(self, receiver_id: int, message: str, direction: Direction):
        sender_id = self.node_id
        logging.info("Message is going from " + str(sender_id) + " to the next node")

        if direction == Direction.NEXT:
            response = self.next_node.send_message(sender_id, receiver_id, message, direction)
        else:
            response = self.previous_node.send_message(sender_id, receiver_id, message, direction)

        return response


    def create_skeleton(self):
        # start listening on the skeleton node
        server = self.skeleton_node.initialize_server(self)
        # set ready state
        self.is_node_ready = True

        # initialize the connection with the pivot node
        self.pivot_node.initialize_client()

        # inform the pivot node that this node is ready
        self.__send_alive_message()
        logging.info("Skeleton node initialized: " +  str(self.node_id))

        server.wait_for_termination()

    def start_node(self):
        # create a thread that will listen until sel.is_ready == True
        # then send a message to the next node
        thread = Thread(target=self.create_skeleton)
        thread.daemon = True
        thread.start()
        
        # wait until the skeleton node is ready
        while not self.is_node_ready:
            pass

        logging.info("Skeleton node is ready")
        return thread


    def initialize_connections(self):
        # initialize the connections
        self.previous_node.initialize_client()
        self.next_node.initialize_client()
        logging.info("Connections initialized")


class PivotNode(owr_pb2_grpc.PivotServicer):
    def __init__(self, node_id: int, nodes_amount: int, skeleton_node: Connection):
        self.node_id = node_id
        self.nodes_amount = nodes_amount
        self.skeleton_node = PivotConnection(*skeleton_node)

        self.is_node_ready = False
        self.is_all_ready = False
        self.nodes_ready = set()

    def get_is_all_ready(self) -> bool:
        return self.is_all_ready

    def get_node_connection_detail(self) -> tuple:
        return (self.skeleton_node.ip, self.skeleton_node.port)

    def receive_alive_message(self, request, context):
       # this will run only on the pivot node
       alive_node = request.nodeid
       self.nodes_ready.add(alive_node)
       self.is_all_ready = len(self.nodes_ready) == self.nodes_amount
       
       logging.info("Nodes " + str(self.nodes_ready) + " is ready")
       return owr_pb2.alive_response()

    def create_skeleton(self):
        # start listening on the skeleton node
        server = self.skeleton_node.initialize_server(self)
        # set ready state
        self.is_node_ready = True

        logging.info("Pivot node initialized: " +  str(self.node_id))

        server.wait_for_termination()

    def start_node(self):
        # create a thread that will listen until sel.is_ready == True
        # then send a message to the next node
        thread = Thread(target=self.create_skeleton)
        thread.daemon = True
        thread.start()
        
        # wait until the skeleton node is ready
        while not self.is_node_ready:
            pass

        logging.info("Skeleton node is ready")
        return thread

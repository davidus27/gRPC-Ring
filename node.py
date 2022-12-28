import logging
from concurrent import futures
import threading
import time

import grpc
import owr_pb2
import owr_pb2_grpc

from dataclasses import dataclass
from enum import Enum

mutex = threading.Lock()

def log(node_id: int, sender_id: int, receiver_id: int, type=""):
    # fomat: 
    # <Node ID, Time, Sender ID, Receiver ID>
    # make time format hours minutes seconds
    executed_time = time.strftime("%H:%M:%S", time.localtime())
    logging.info(f"<{node_id}, {executed_time}, {sender_id}, {receiver_id}> {type}")

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


class State(Enum):
    CANDIDATE = 0
    DEFEATED = 1
    LEADER = 2


class Connection:
    def __init__(self, node_id, ip, port):
        self.node_id = node_id
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

    def send_election_message(self, node_id: int, direction: Direction):
        return self.stub.receive_election_message(owr_pb2.election_request(
            leading_node_id=node_id,
            direction=direction.value))

    def send_termination_message(self, node_id: int, direction: Direction):
        return self.stub.receive_termination_message(owr_pb2.termination_request(
            terminating_node_id=node_id,
            direction=direction.value
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

        # info about ring, self and pivot
        self.previous_node = NodeConnection(*node_context.previous)
        self.skeleton_node = NodeConnection(*node_context.skeleton)
        self.next_node = NodeConnection(*node_context.next)
        self.pivot_node = PivotConnection(*node_context.pivot)

        # info about election
        self.state = State.CANDIDATE
        self.leading_node_id = None  # minimal value seen so far
        self.sent_em = False
        self.leading_terminated = False

    def receive_message(self, request: owr_pb2.owr_request, context):
        # check if the message is for this node
        log(self.node_id, request.senderid, self.node_id, "MSG")
        logging.debug("I am node " + str(self.node_id) + ", message is from " +
                     str(request.senderid) + " to " + str(request.receiverid))

        if request.receiverid == self.node_id:
            logging.debug("This message is for me")
            logging.debug("Message content: " + str(request.content))
            return owr_pb2.owr_response()

        # if not, forward the message to the next node
        direction = Direction(request.sending_direction)
        self.inject_text_message(request.receiverid, request.content, direction)

        return owr_pb2.owr_response()

    # The As-Far-As-Possible (AFA) LE Algorithm in a Ring
    # (1) At least one node xi (an Initiator) chooses one of its two neighbors
    # (2) and sends eventually an Election Message (EM) with ID(xi) to it.
    # (3) If node xj receives an EM, then
    # (4) xj sends its own EM with ID(xj ) if it did not send before,
    # (5) xj keeps track of the minimum ID seen so far (including its own).
    # (6) if the received ID > ID(xj ), then xj discards the received EM,
    # (7) if the received ID < ID(xj ), then
    # (8) xj becomes Defeated
    # (9) and forwards the received EM along the ring,
    # (10) if the received ID = ID(xj ), then (*my own EM returned*)
    # (11) xi declares itself the leader
    # (12) and sends a Termination Message TM along the ring
    # (to notify the other nodes and terminate globally the execution).

    # main code for the election algorithm
    def receive_election_message(self, request: owr_pb2.election_request, context):
        log(self.node_id, request.leading_node_id, self.node_id, "ALGORITHM")

        if not self.sent_em:
            direction = Direction(request.direction)
            self.sent_em = True
            self.inject_election_message(self.node_id, direction)
            return owr_pb2.election_response()
        
        if request.leading_node_id > self.node_id:
            logging.debug("Discarding the message " + str(request.leading_node_id))
            return owr_pb2.election_response()
        
        if request.leading_node_id < self.node_id:
            logging.debug("I am defeated " +  str(self.node_id) + " by " + str(request.leading_node_id))
            self.state = State.DEFEATED
            direction = Direction(request.direction)
            self.leading_node_id = request.leading_node_id
            self.inject_election_message(request.leading_node_id, direction)
            return owr_pb2.election_response()

        if request.leading_node_id == self.node_id:
            logging.debug("I am the leader " + str(self.node_id))
            self.state = State.LEADER
            self.leading_node_id = self.node_id
            # send the termination message to the next node
            self.inject_termination_message(self.node_id, Direction.NEXT)

            return owr_pb2.election_response()


    def receive_termination_message(self, request, context):
        log(self.node_id, request.terminating_node_id, self.node_id, "TERMINATION")
        logging.debug("Termination message on " + str(self.node_id) + " received from " + str(request.terminating_node_id))
        if self.leading_terminated:
            return owr_pb2.termination_response()

        # set it to true so that the message is not sent again
        self.leading_terminated = True
        # send the message to the next node
        self.inject_termination_message(request.terminating_node_id, Direction(request.direction))
        # end the node
        return owr_pb2.termination_response()
        

    def get_directional_node(self, direction: Direction):
        nodes = [self.next_node, self.previous_node]
        return nodes[direction.value]

    def inject_text_message(self, receiver_id: int, message: str, direction: Direction):
        sender_id = self.node_id
        logging.debug("Message is going from " +
                     str(sender_id) + " to the next node")

        receiving_node = self.get_directional_node(direction)
        # log(self.node_id, sender_id, receiving_node.node_id)
        response = receiving_node.send_message(sender_id,
                                               receiver_id,
                                               message,
                                               direction
                                               )
        return response

    def inject_election_message(self, node_id: int, direction: Direction):
        logging.debug("Sending election message " + str(node_id) + " to " + str(direction))
        receiving_node = self.get_directional_node(direction)
        receiving_node.send_election_message(node_id, direction)


    def inject_termination_message(self, node_id: int, direction: Direction = Direction.NEXT):
        logging.debug("Sending termination message from " + str(self.node_id) + " to " + str(node_id) + " " + str(direction))
        receiving_node = self.get_directional_node(direction)
        receiving_node.send_termination_message(node_id, direction)


    def start_leader_election(self, direction: Direction = Direction.NEXT):
        # start the election by sending a message to the next node
        self.inject_election_message(self.node_id, direction)

    def create_skeleton(self):
        # start listening on the skeleton node
        node_server = self.skeleton_node.initialize_server(self)
        # set ready state
        self.is_node_ready = True

        # initialize the connection with the pivot node
        self.pivot_node.initialize_client()

        # inform the pivot node that this node is ready
        log(self.node_id, self.node_id, self.pivot_node.node_id, "ALIVE_MSG")
        self.pivot_node.send_am_alive(self.node_id)
        logging.debug("Alive message sent to pivot node")
        logging.debug("Skeleton node initialized: " + str(self.node_id))

        node_server.wait_for_termination()

    def start_node(self):
        # create a thread that will listen until sel.is_ready == True
        # then send a message to the next node
        thread = threading.Thread(target=self.create_skeleton)
        thread.daemon = True
        thread.start()

        # wait until the skeleton node is ready
        while not self.is_node_ready:
            pass

        logging.debug("Skeleton node is ready")
        return thread

    def initialize_connections(self):
        # initialize the connections
        self.previous_node.initialize_client()
        self.next_node.initialize_client()
        logging.debug("Connections initialized")


class PivotNode(owr_pb2_grpc.PivotServicer):
    def __init__(self, node_id: int, nodes_amount: int, skeleton_node: Connection):
        self.node_id = node_id
        self.nodes_amount = nodes_amount
        self.skeleton_node = PivotConnection(node_id, *skeleton_node)

        self.is_node_ready = False
        self.is_all_ready = False
        self.nodes_ready = set()

    def get_is_all_ready(self) -> bool:
        return self.is_all_ready

    def get_node_connection_detail(self) -> tuple:
        return (self.node_id, self.skeleton_node.ip, self.skeleton_node.port)

    def set_nodes_amount(self, nodes_amount: int):
        self.nodes_amount = nodes_amount
    
    def reset_ready_state(self):
        self.nodes_ready = set()
        self.is_all_ready = False

    def receive_alive_message(self, request, context):
        # this will run only on the pivot node
        # log(self.node_id, request.nodeid, self.node_id)
        alive_node = request.nodeid
        self.nodes_ready.add(alive_node)
        self.is_all_ready = len(self.nodes_ready) == self.nodes_amount

        logging.debug("Nodes " + str(self.nodes_ready) + " is ready")
        return owr_pb2.alive_response()

    def create_skeleton(self):
        # start listening on the skeleton node
        node_server = self.skeleton_node.initialize_server(self)
        # set ready state
        self.is_node_ready = True

        logging.debug("Pivot node initialized: " + str(self.node_id))

        node_server.wait_for_termination()

    def start_node(self):
        # create a thread that will listen until sel.is_ready == True
        # then send a message to the next node
        thread = threading.Thread(target=self.create_skeleton)
        thread.daemon = True
        thread.start()

        # wait until the skeleton node is ready
        while not self.is_node_ready:
            pass

        logging.debug("Skeleton node is ready")
        return thread

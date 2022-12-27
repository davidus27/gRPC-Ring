from node import *
import logging
import random

# yields current, previous and next (ip,port) tuple
def generate_ring_data(nodes_amount: int, pivot, ip="127.0.0.1", port=60000) -> tuple:
    # generate list of random node ids between 1 and 1000 (without duplicates)
    # node_ids = random.sample(range(1, 1000), nodes_amount)
    for index in range(nodes_amount):
        previous = (ip, port + (index - 1) % nodes_amount)
        skeleton = (ip, port + index)
        next = (ip, port + (index + 1) % nodes_amount)
        # randomly generated int node id between 1 and 1000
        params = NodeInfo(node_id=index,
                pivot=pivot.get_node_connection_detail(),
                previous=previous,
                skeleton=skeleton,
                next=next
        )
        yield Node(params)


def get_pivot(nodes_amount: int, ip="127.0.0.1", port=60000) -> tuple:
    skeleton = (ip, port)
    pivot = PivotNode(1, nodes_amount, skeleton)
    pivot.start_node()
    return pivot


def generate_ring_from_file(file_path: str) -> tuple:
    pass

def create_ring(ring_generator, pivot):
    ring = list(ring_generator)

    for node in ring:
        logging.debug("Started node id: " + str(node.node_id))
        node.start_node()

    while pivot.get_is_all_ready() == False:
        pass

    logging.debug("All nodes are ready")

    # initialize connections
    for node in ring:
        logging.debug("Initialized connections for node id: " + str(node.node_id))
        node.initialize_connections()

    return ring

def main():
    nodes_amount = 5

    # create a pivot node
    pivot_node = get_pivot(nodes_amount)

    # create a generator for the ring
    ring_generator = generate_ring_data(nodes_amount, pivot_node, port=60001)

    # create a ring
    ring = create_ring(ring_generator, pivot_node)
    
    # send a message to the next node
    # ring[0].inject_text_message(1, "Nasdaaarek", Direction.PREVIOUS)

    ring[0].start_leader_election()
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(message)s')
    main()
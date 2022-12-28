from node import *
import sys
import logging
import random

# yields current, previous and next (ip,port) tuple
def generate_ascended_ring(nodes_amount: int, pivot, ip="127.0.0.1", port=60000) -> tuple:
    # generate list of random node ids between 1 and 1000 (without duplicates)
    # node_ids = random.sample(range(1, 1000), nodes_amount)
    for index in range(nodes_amount):
        next_element_index = (index + 1) % nodes_amount
        previous_element_index = (index - 1) % nodes_amount

        previous = (previous_element_index, ip, port + previous_element_index)
        skeleton = (index, ip, port + index)
        next = (next_element_index, ip, port + next_element_index)
        # randomly generated int node id between 1 and 1000
        params = NodeInfo(node_id=index,
                pivot=pivot.get_node_connection_detail(),
                previous=previous,
                skeleton=skeleton,
                next=next
        )
        yield Node(params)

def generate_string_ring(string: str, pivot, ip="127.0.0.1", port=60000) -> tuple:
    string_ids = string.split(",")
    nodes_amount = len(string_ids)
    ids = [ int(x) for x in string_ids ]

    for index, id in enumerate(ids):
        next_element_index = (index + 1) % nodes_amount
        previous_element_index = (index - 1) % nodes_amount

        previous = (ids[previous_element_index], ip, port + previous_element_index)
        skeleton = (ids[index], ip, port + index)
        next = (ids[next_element_index], ip, port + next_element_index)
        # randomly generated int node id between 1 and 1000
        params = NodeInfo(node_id=id,
                pivot=pivot.get_node_connection_detail(),
                previous=previous,
                skeleton=skeleton,
                next=next
        )
        yield Node(params)


def get_pivot(nodes_amount: int = 0, ip="127.0.0.1", port=60000) -> PivotNode:
    skeleton = (ip, port)
    pivot = PivotNode(-1, nodes_amount, skeleton)
    pivot.start_node()
    return pivot


def create_ring(ring_generator, pivot) -> list[Node]:
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

def do_the_thing(ring_generator, pivot):
    ring = create_ring(ring_generator, pivot)
    ring[0].start_leader_election()


def main():
    string_ids = sys.argv[1]
    nodes_amount = len(string_ids)
    # create a pivot node
    pivot_node = get_pivot(nodes_amount)

    # create a generator for the ring
    generate_string_ring(string_ids, pivot_node, port=60001)
    ring_generator = generate_ascended_ring(nodes_amount, pivot_node, port=60001)

    # create a ring
    ring = create_ring(ring_generator, pivot_node)
    
    # send a message to the next node
    # ring[0].inject_text_message(1, "Hello!", Direction.PREVIOUS)

    ring[0].start_leader_election()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    main()
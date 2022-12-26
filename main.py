from node import *
import logging


# yields current, previous and next (ip,port) tuple
def generate_ring_data(nodes_amount: int, pivot, ip="127.0.0.1", port=60000) -> tuple:
    for node_id in range(nodes_amount):
        previous = (ip, port + (node_id - 1) % nodes_amount)
        skeleton = (ip, port + node_id)
        next = (ip, port + (node_id + 1) % nodes_amount)
        params = NodeInfo(node_id=node_id,
                pivot=pivot.get_node_connection_detail(),
                previous=previous,
                skeleton=skeleton,
                next=next
        )
        yield Node(params)


def get_pivot(nodes_amount: int, ip="127.0.0.1", port=60000) -> tuple:
    pivot = PivotNode(NodeInfo(node_id=-1,
                pivot=(ip, port),
                previous=(None, None),
                skeleton=(ip, port),
                next=(None, None)
        ))
    pivot.set_nodes_amount(nodes_amount)
    pivot.start_node()
    return pivot


def generate_ring_from_file(file_path: str) -> tuple:
    pass

def create_ring(ring_generator, pivot):
    ring = list(ring_generator)

    for node in ring:
        logging.info("Started node id: " + str(node.node_id))
        node.start_node()

    while pivot.get_is_all_ready() == False:
        pass

    logging.info("All nodes are ready")

    # initialize connections
    for node in ring:
        logging.info("Initialized connections for node id: " + str(node.node_id))
        node.initialize_connections()

    return ring

def main():
    nodes_amount = 100

    # create a pivot node
    pivot_node = get_pivot(nodes_amount)

    # create a generator for the ring
    ring_generator = generate_ring_data(nodes_amount, pivot_node, port=60001)

    # create a ring
    ring = create_ring(ring_generator, pivot_node)
    
    # send a message to the next node
    ring[0].inject_message(1, "Nasdaaarek", Direction.PREVIOUS)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, datefmt="%H:%M:%S")
    main()
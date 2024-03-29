# All nodes in the network know the ip address
# and the port of the bootstrap node.
BOOTSTRAP_IP = "127.0.0.1"
# BOOTSTRAP_PORT = "5000"
BOOTSTRAP_PORT = "9876"

block_capacity = 5 # default value for the capacity of the blocks
total_nodes = 0 # initialize the total number of nodes in the network

def set_block_capacity(value):
    """Updates the global variable block_capacity with the given value."""
    # The given value should be passed to the main program as a command-line argument.
    global block_capacity
    block_capacity = value

def set_total_nodes(value):
    """Updates the global variable total_nodes with the given value."""
    # The given value should be passed to the main program as a command-line argument.
    global total_nodes
    total_nodes = value
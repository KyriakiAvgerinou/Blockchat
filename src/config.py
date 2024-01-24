block_capacity = 5 # default value for the capacity of the blocks

def set_block_capacity(value):
    """Updates the global variable block_capacity with the given value."""
    # The given value should be passed to the main program as a command-line argument.
    global block_capacity
    block_capacity = value
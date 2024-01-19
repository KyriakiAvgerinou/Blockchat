from block import Block
from libraries.custom_exceptions import BootstrapError
from libraries.module_library import calculate_hash

class Blockchain:
    """
    The blockchain.

    Attributes:
        blocks (list): the blocks that have been validated and have entered the blockchain.
    """

    def __init__(self, bootstrap_node):
        """Inits the blockchain."""
        if bootstrap_node.id != 0:
            raise BootstrapError("The node initiating the blockchain is not the bootstrap node.")
        self.blocks = []
        self.create_genesis_block(bootstrap_node)

    def __str__(self):
        """Returns a string representation of the blockchain."""
        return str(self.__class__) + ": " + str(self.__dict__)

    def create_genesis_block(self, bootstrap_node):
        """Creates the genesis block on behalf of the bootstrap node and places it into the blockchain."""
        genesis_block = Block(validator = bootstrap_node, index = 0, previous_hash = "1")
        self.blocks.append(genesis_block)

    def add_block(self, block):
        """Adds a new, validated block into the blockchain."""
        initial_block_hash = block.hash
        block.update_index(self.blocks[-1].index)
        block.update_previous_hash(self.blocks[-1].hash)
        block.get_new_hash()
        if block.is_valid():
            self.blocks.append(block)
        else:
            block.index = None
            block.previous_hash = None
            block.hash = initial_block_hash ## FIX ME: This or get_new_hash() or exception

    def is_valid(self):
        """Checks if the chain is valid."""
        for i in range(1, len(self.blocks)): # skip the validation of the genesis block
            current_block = self.blocks[i]
            previous_block = self.blocks[i-1]
            # Current block hash validation, i.e. the data in the block has not been tampered with.
            if current_block.hash != calculate_hash(current_block.to_dict()):
                print(f"Invalid hash in block: {i}")
                return False
            # Previous block hash validation, i.e. the blocks in the blockchain are linked in the correct order.
            if current_block.previous_hash != previous_block.hash:
                print(f"Mismatched previous hash in block: {i}")
                return False
        return True
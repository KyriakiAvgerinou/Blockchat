from libraries.module_library import calculate_hash
from transaction import Transaction
from time import time
from libraries.custom_exceptions import BlockCapacityError

class Block:
    """
    A block in the blockchain.

    Attributes:
        hash (str): the hash of the block.
        index (int): the index of the block once it enters the blockchain.
        previous_hash (str): the hash of the previous block in the blockchain.
        transactions (list): the transactions that have been added to the block.
        validator (Node object): the node object that creates the block.
        timestamp (float): the timestamp when the block is created.
    """

    def __init__(self, validator, index = None, previous_hash = None): # arguments index and previous_hash are inputted for the genesis block
        """Inits a block."""
        self.index = index
        self.previous_hash = previous_hash # Needed for validation purposes.
        self.transactions = [] # a list of the transaction objects (in dictionary form) that belong to the block
        self.validator = validator
        self.timestamp = time()
        self.hash = None
        self.get_new_hash()

    def __str__(self):
        """Returns a string representation of the block."""
        return str(self.__class__) + ": " + str(self.__dict__)

    def to_dict(self):
        """Converts the self block object to dict for the get_new_hash() function."""
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": [transaction.hash for transaction in self.transactions],
            "validator": self.validator.id,
            "timestamp": self.timestamp
        }

    def get_new_hash(self):
        """Calculates the hash of the block."""
        self.hash = calculate_hash(self.to_dict())

    def add_transaction(self, transaction, capacity):
        """Adds a new transaction to the block."""
        try:
            if len(self.transactions) < capacity:
                self.transactions.append(transaction)
            else:
                raise BlockCapacityError("Block capacity exceeded. The addition is declined.")
        except BlockCapacityError as e:
            # print(f"{e}")
            return False
        return True

    def update_index(self, old_index):
        """Updates the index of the block just before it enters the blockchain."""
        new_index = old_index + 1
        self.index = new_index

    def update_previous_hash(self, previous_block):
        """Updates the previous_hash of the block just before it enters the blockchain."""
        self.previous_hash = previous_block.hash

    def is_valid(self):
        """"""
        ## FIX ME ##
        return True
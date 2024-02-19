from libraries.module_library import calculate_hash
from node import Node
from time import time

class Transaction:
    """
    A transaction of coins or messages in the blockchain network.

    Attributes:
        hash (str): the hash of the transaction.
        sender (Node object): the sender node object.
        nonce (int): the nonce of the transaction - number used only once - comes from the wallet of the sender node.
        recipient_id (int): the id of the recipient node.
        recipient_public_key (str): the public key of the recipient node.
        bcc (int): the amount of coins to transfer.
        message (str): the message to transfer.
        type (str): the type of the transaction --> 'coins' or 'message'. If both coins and a message are transferred, then self.type = 'coins'.
        signature (bytes object): the signature that verifies that the transaction was created by the sender node.
        timestamp (float): the timestamp when the transaction was created.
    """

    def __init__(self, sender, recipient_id, recipient_public_key, bcc = None, message = None):
        """Initiates a transaction."""
        self.sender = sender # sender node
        self.nonce = None
        self.recipient_id = recipient_id
        self.recipient_public_key = recipient_public_key
        self.bcc = bcc
        self.message = message
        if self.bcc:
            self.type = "coins"
        elif self.message:
            self.type = "message"
        else:
            raise TypeError("New object Transaction missing required argument: bcc or message.")
        self.signature = bytes() # placeholder for signature
        self.timestamp = time()
        self.hash = self.get_hash()

    def __str__(self):
        """Returns a string representation of the transaction."""
        return str(self.__class__) + ": " + str(self.__dict__)

    def to_dict(self):
        """Converts the self transaction object to dict for the get_hash() function."""
        # We don't calculate the hash using the entire transaction object.
        # We merely include the attributes that uniquely identify the transaction and are not expected to change once the transaction is created.
        return {
            "sender_public_key": self.sender.wallet.public_key,
            "recipient_public_key": self.recipient_public_key,
            "type": self.type,
            "bcc": self.bcc,
            "message": self.message,
            "timestamp": self.timestamp,
        }

    def get_hash(self):
        """Calculates the hash of the transaction."""
        return calculate_hash(self.to_dict())

    def get_signature(self):
        """Signs the hash of the self transaction using the private key of the sender node (the private key of the wallet of the sender node)."""
        if self.signature == bytes():
            self.signature = self.sender.wallet.sign_data(self.hash)

    def update_nonce(self):
        """
        Updates the nonce of the transaction.
        It is called once the transaction is validated by all the nodes in the network
        and the transaction is ready to be added to the sender's wallet.
        """
        if self.nonce is None:
            self.nonce = self.sender.wallet.get_next_nonce()

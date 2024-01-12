import rsa

class Wallet:
    """
    The wallet of a node in the network.

    Attributes:
        public_key (str): the public key of the wallet (also serves as the address of the wallet).
        private_key (str): the private key of the wallet.
        last_nonce (int): a counter that maintains the number of the distinct transactions that the wallet has created as a sender.
        balance (int): the total balance of the wallet.
        transactions (list): the transactions of the wallet.
    """

    def __init__(self, initial_balance = 0):
        """Inits a wallet."""
        self._public_key, self._private_key = self.generate_key_pair()
        self.last_nonce = 0
        self.balance = initial_balance
        self.transactions = []

    def __str__(self):
        """Returns a string representation of the wallet."""
        return str(self.__class__) + ": " + str(self.__dict__)

    @property
    def public_key(self):
        """So that the public key of the wallet does not change externally."""
        return self._public_key

    @property
    def private_key(self):
        """So that the private key of the wallet does not change externally."""
        return self._private_key

    def get_next_nonce(self):
        """Returns the last given nonce to the last transaction created by the self sender wallet."""
        # Called by class transaction to update node.wallet.transaction.nonce
        # every time the self sender wallet creates a new transaction.
        self.last_nonce += 1
        return self.last_nonce

# ======================================================================================================================================================
# Wallet's Cryptographic Operations
# ======================================================================================================================================================

    def generate_key_pair(self):
        """Generates the public - private key pair of the wallet using the rsa module."""
        public_key, private_key = rsa.newkeys(2048) # You can adjust the key size for better key generation timing (i.e. 1024).
        return public_key.save_pkcs1().decode(), private_key.save_pkcs1().decode()

    def sign_data(self, data):
        """Returns the digital signature for the given piece of data using the private key of the wallet."""
        signature = rsa.sign(data.encode(), rsa.PrivateKey.load_pkcs1(self.private_key), "SHA-256")
        return signature

    def verify_signature(self, data, signature, public_key):
        """Verifies whether the signature on the given piece of data derives from the wallet with the given public key (True) or not (False).
            It also detects whether the given data has been altered or tampered with."""
        try:
            rsa.verify(data.encode(), signature, rsa.PublicKey.load_pkcs1(public_key))
            return True
        except rsa.VerificationError:
            return False
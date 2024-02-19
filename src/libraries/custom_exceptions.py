class BootstrapError(Exception):
    """Custom error for invalid node on blockchain initialization."""
    pass

class BlockCapacityError(Exception):
    """Custom error for adding a transaction to the block when its capacity has already been filled."""
    pass

class SessionInitializationError(Exception):
    """Custom error raised when required command-line arguments are not defined at the beginning of the session."""
    pass

class InsufficientBalanceError(Exception):
    """Custom error for projecting a negative wallet balance."""
    pass

class TransactionValidationError(Exception):
    """Custom error for detecting transaction validation failure across the nodes in the network."""
    pass

class BootstrapError(Exception):
    """Custom error for invalid node on blockchain initialization."""
    pass

class BlockCapacityError(Exception):
    """Custom error for adding a transaction to the block when its capacity has already been filled."""
    pass

class SessionInitializationError(Exception):
    """Custom error raised when required command-line arguments are not defined at the beginning of the session."""
    pass

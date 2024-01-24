class BootstrapError(Exception):
    """Custom error for invalid node on blockchain initialization."""
    pass

class BlockCapacityError(Exception):
    """Custom error for adding a transaction to the block when its capacity has already been filled."""
    pass
import hashlib
import json

def to_json(obj):
    """Converts the given object into a json string."""
    return json.dumps(obj, sort_keys = True)

def calculate_hash(obj):
    """Calculates and returns a hash for the given object."""
    hash = hashlib.sha256(to_json(obj).encode()).hexdigest()
    return hash
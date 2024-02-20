import hashlib
import json
import requests

def to_json(obj):
    """Converts the given object into a json string."""
    return json.dumps(obj, sort_keys = True)

def calculate_hash(obj):
    """Calculates and returns a hash for the given object."""
    hash = hashlib.sha256(to_json(obj).encode()).hexdigest()
    return hash

def make_get_request(ip, port, endpoint):
    """Makes a GET request to http://{ip}:{port}/blockchat/{endpoint} and returns the response."""
    url = f"http://{ip}:{port}/blockchat/{endpoint}"
    response = requests.get(url)
    return response

def make_post_request(ip, port, endpoint, data = None):
    """Makes a POST request to http://{ip}:{port}/blockchat/{endpoint} with the given data and returns the response."""
    url = f"http://{ip}:{port}/blockchat/{endpoint}"
    response = requests.post(url, data)
    return response

def transaction_total_expenses(bcc = None, message = None):
    """
    Calculates the total expenses of the transaction:
    - When transferring bcc, there is a fee of 3%.
    - When sending a message, there is a fee of 1 bcc per character in the message.
    """
    total = 0
    if bcc:
        total += bcc * 1.03 # include the amount of bcc being transferred
    if message:
        total += len(message.strip())
    return total

def retrieve_from_ring_node(ring, ring_node_id, request):
    """Returns the ip address, the port or the public key of the ring node, given its id."""
    for ring_node in ring:
        if ring_node["id"] == ring_node_id:
            if request == "ip":
                return ring_node["ip"]
            elif request == "port":
                return ring_node["port"]
            elif request == "public_key":
                return ring_node["public_key"]
            else:
                raise ValueError("Request back only 'ip', 'port' or 'public_key'.")

def standardize_transaction_input(recipient_id, bcc = None, message = None):
    """Standardizes the input data for the 'blockchat/make_transaction' endpoint."""
    if bcc is None and message is None:
        raise TypeError("You should input at least one quantity for the transaction, either coins or a message.")
    return {
        "recipient_id": recipient_id,
        "bcc": bcc,
        "message": message
    }

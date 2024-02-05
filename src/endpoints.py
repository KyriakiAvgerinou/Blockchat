from flask import Blueprint, request, jsonify
from node import Node

# Init the current node.
node = Node()

# Define the blockchat_bp blueprint for the endpoints.
blockchat_bp = Blueprint("blockchat_bp", __name__)

@blockchat_bp.route("/register_node", methods = ["POST"])
def register_node():
    """
    Request to the bootstrap node only:
        - Register a new node in the network and add it to the ring.
    """
    # Calculate the id for the new node.
    new_node_id = len(node.ring)

    # Retrieve the new node data from the request.
    new_node_ip = request.form.get("ip")
    new_node_port = request.form.get("port")
    new_node_public_key = request.form.get("public_key")

    # Register the new node.
    node.register_node_to_ring(new_node_id, new_node_ip, new_node_port, new_node_public_key)

    # Return the id of the new node.
    return jsonify({"id": new_node_id})

@blockchat_bp.route("/get_ring", methods = ["GET"])
def get_ring():
    """
    Request to the bootstrap node only:
        - Send the current ring of nodes.
    """
    return jsonify({"ring": node.ring})
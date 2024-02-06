from flask import Blueprint, request, jsonify
from node import Node
import pickle

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

@blockchat_bp.route("/post_ring", methods = ["POST"])
def post_ring():
    """
    Called for all the nodes in the network, except for the bootstrap node.
    Updates the ring of the current node with the final ring of nodes in the network.
    """
    node.ring = pickle.loads(request.get_data())
    return jsonify({"message": f"Update node {node.id} ring successful."})

@blockchat_bp.route("/ask_chain", methods = ["POST"])
def ask_chain():
    """
    The requesting node asks the receiving node for their self.chain.
    """
    requesting_node = pickle.loads(request.get_data())
    node.share_chain(requesting_node)
    return jsonify({"message": f"Update node {requesting_node['id']} chain from node {node.id} successful."})

@blockchat_bp.route("/post_chain", methods = ["POST"])
def post_chain():
    """
    Updates the chain of the current node with the given blockchain.
    """
    node.chain = pickle.loads(request.get_data())
    return jsonify({"message": f"Update node {node.id} chain successful."})

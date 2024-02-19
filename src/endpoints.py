from flask import Blueprint, request, jsonify
from node import Node
import pickle
import config
from libraries.custom_exceptions import InsufficientBalanceError, TransactionValidationError
from libraries.module_library import retrieve_from_ring_node

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

@blockchat_bp.route("/get_total_nodes", methods = ["GET"])
def get_total_nodes():
    """
    Get config.total_nodes from the current installation.
    """
    return jsonify({"total_nodes": config.total_nodes})

@blockchat_bp.route("/get_block_capacity", methods = ["GET"])
def get_block_capacity():
    """
    Get config.block_capacity from the current installation.
    """
    return jsonify({"block_capacity": config.block_capacity})

@blockchat_bp.route("/make_transaction", methods = ["POST"])
def make_transaction():
    """
    Makes a new transaction.
    The sender node is the current node.
    """
    # Retrieve transaction input data.
    recipient_id = request.form.get("recipient_id")
    recipient_id = int(recipient_id)
    bcc = request.form.get("bcc")
    if not bcc:
        bcc = 0
    else:
        bcc = int(bcc)
    message = request.form.get("message")

    # Get recipient public_key.
    recipient_public_key = retrieve_from_ring_node(node.ring, recipient_id, "public_key")

    # Make the transaction.
    try:
        node.create_transaction(recipient_id, recipient_public_key, bcc, message)
    # Catch InsufficientBalanceError.
    except InsufficientBalanceError:
        return jsonify({"message": f"Transaction of {bcc} BCC and message: '{message}' from node {node.id} to node {recipient_id} declined due to insufficient sender balance."}), 400
    # Catch TransactionValidationError.
    except TransactionValidationError:
        return jsonify({"message": f"Transaction of {bcc} BCC and message: '{message}' from node {node.id} to node {recipient_id} failed to validate."}), 403

    return jsonify({"message": f"Transaction of {bcc} BCC and message: '{message}' from node {node.id} to node {recipient_id} successful."})

@blockchat_bp.route("/validate_transaction", methods = ["POST"])
def validate_transaction():
    """Asks the current node to validate the input transaction."""
    transaction = pickle.loads(request.get_data())
    validation_result, validation_description = node.validate_transaction(transaction)
    if not validation_result:
        return jsonify({"message": f"Transaction validation by node {node.id} failed: {validation_description}"}), 403

    return jsonify({"message": "Transaction validation successful."})

@blockchat_bp.route("/update_balance", methods = ["POST"])
def update_balance():
    """Updates the balance of the current node with the input amount."""
    amount = request.form.get("amount")
    if not amount:
        amount = 0
    else:
        amount = int(amount)
    try:
        node.wallet.update_balance(amount)
    except InsufficientBalanceError:
        return jsonify({"message": f"Node {node.id}'s projected balance is negative. Balance update with {amount} BCC rejected."}), 400
    if amount > 0:
        return jsonify({"message": f"{amount} bcc successfully added to node {node.id}'s balance."})
    elif amount < 0:
        return jsonify({"message": f"{amount} bcc successfully subtracted from node {node.id}'s balance."})
    else:
        return jsonify({"message": f"{amount} bcc sent. Node {node.id}'s balance remains the same."})

@blockchat_bp.route("/get_balance", methods = ["GET"])
def get_balance():
    """Get the current balance of the current node."""
    return jsonify({"current_balance": node.wallet.balance})

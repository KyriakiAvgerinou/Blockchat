from flask import Blueprint
from node import Node

# Init the current node.
node = Node()

# Define the blockchat_bp blueprint for the endpoints.
blockchat_bp = Blueprint("blockchat_bp", __name__)

"""
@blockchat_bp.route("/request", methods = [""])
def request():
    pass
"""
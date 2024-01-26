from flask import Flask
from endpoints import blockchat_bp
from argparse import ArgumentParser
import config

app = Flask(__name__) # initialize the application
app.register_blueprint(blockchat_bp, url_prefix = "/blockchat") # register blockchat_bp blueprint

if __name__ == "__main__":
    # Parse the command-line arguments.
    parser = ArgumentParser(description = "The Blockchat Application.")

    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    # Retrieve the port for the incoming HTTP requests.
    required.add_argument("-prt", "--port", type = int, help = "insert port for incoming HTTP requests", required = True)
    # Retrieve the total number of nodes participating in the network.
    required.add_argument("-nds", "--nodes", type = int, choices = [5, 10], help = "insert total number of nodes in the network", required = True)
    # Retrieve the transaction capacity of the blocks.
    required.add_argument("--capacity", type = int, choices = [5, 10, 20], help = "insert block capacity", required = True)
    # Retrieve whether the current node is the bootstrap node.
    optional.add_argument("-btstrp", "--bootstrap", action = "store_true", help = "insert if the current node is the bootstrap")

    args = parser.parse_args()
    port = args.port # get the port
    config.set_total_nodes(args.nodes) # set the global variable total_nodes
    config.set_block_capacity(args.capacity) # set the global variable block_capacity
    is_bootstrap = args.bootstrap # get whether the node is the bootstrap

    app.run(debug = True)
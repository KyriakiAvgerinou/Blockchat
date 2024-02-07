from flask import Flask
from endpoints import node, blockchat_bp
from argparse import ArgumentParser
import config
from blockchain import Blockchain
import socket
import pickle
import threading
from libraries.module_library import make_get_request, make_post_request

# Get the ip address and the port of the bootstrap node defined by the config file.
BOOTSTRAP_IP = config.BOOTSTRAP_IP
BOOTSTRAP_PORT = config.BOOTSTRAP_PORT

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
    total_nodes = config.total_nodes
    config.set_block_capacity(args.capacity) # set the global variable block_capacity
    is_bootstrap = args.bootstrap # get whether the node is the bootstrap

    if is_bootstrap:
        """
        If the current node is the bootstrap node:
            - Initiate the bootstrap node (id = 0, ip = config.BOOTSTRAP_IP, port = config.BOOTSTRAP_PORT, is_bootstrap = True),
            - register the bootstrap node in the ring,
            - deposit 1000 * (the total number of nodes in the network) BCC in the bootstrap's wallet,
            - initiate the blockchain and generate the genesis block.
        """
        node.id = 0
        node.ip = BOOTSTRAP_IP
        node.port = BOOTSTRAP_PORT
        node.is_bootstrap = True
        node.wallet.balance = 1000 * total_nodes
        node.register_node_to_ring(node.id, node.ip, node.port, node.wallet.public_key)
        node.chain = Blockchain(node) # in the initialization of the blockchain, the genesis block is automatically generated
        # app.run(debug = True, host = node.ip, port = node.port)
        app.run(host = node.ip, port = node.port) # run the Flask development server and specify the ip address and port on which the Flask server should listen
    else:
        """
        If the current node is not the bootstrap node:
            - Initiate the current node,
            - ask the bootstrap node to register them, add them to the ring of nodes and give them their id.
        If the current node is the last one to enter the network:
            - send bootstrap's FINAL ring of nodes to all the nodes in the network,
            - send bootstrap's initial version of the blockchain to all the nodes in the network.
        """
        # Get the ip address of the device.
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        # Initialize the current node.
        node.ip = ip_address
        node.port = port

        # Send an HTTP POST request to the bootstrap node to register the current node.
        node_data = {
            "ip": node.ip,
            "port": node.port,
            "public_key": node.wallet.public_key
        }
        registration_response = make_post_request(BOOTSTRAP_IP, BOOTSTRAP_PORT, endpoint = "register_node", data = node_data)

        # Retrieve the id for the current node.
        node.id = registration_response.json()["id"]

        # If the current node is the last one to enter the network,
        # send the final ring of nodes and the initial blockchain with only the genesis block
        # to all the nodes in the network.
        if node.id == total_nodes - 1:

            # Get the final ring of nodes from the bootstrap node.
            bootstrap_ring = make_get_request(BOOTSTRAP_IP, BOOTSTRAP_PORT, endpoint = "get_ring")
            bootstrap_ring = bootstrap_ring.json()["ring"]

            # Send the final ring and the initial blockchain to all the nodes in the network.
            def thread_function(): # there were concurrency issues that were resolved via threading
                # When you start a new thread to handle the loop,
                # it runs concurrently with the main thread,
                # which continues executing the subsequent code,
                # including starting the Flask server for the last node.
                # By the time the POST requests refer to the last node,
                # its server will be up.
                for ring_node in bootstrap_ring[1:]: # exclude the bootstrap node
                    # Post the bootstrap_ring to ring_node's ring.
                    post_ring_response = make_post_request(ring_node["ip"], ring_node["port"], endpoint = "post_ring", data = pickle.dumps(bootstrap_ring))
                    # Ask the bootstrap node to post its self.chain to ring_node's chain.
                    post_chain_response = make_post_request(BOOTSTRAP_IP, BOOTSTRAP_PORT, endpoint = "ask_chain", data = pickle.dumps(ring_node))
                    print(post_ring_response.json()["message"])
                    print(post_chain_response.json()["message"])
            req = threading.Thread(target = thread_function, args = ())
            req.start()

        # app.run(debug = True, host = node.ip, port = node.port)
        app.run(host = node.ip, port = node.port) # run the Flask development server and specify the ip address and port on which the Flask server should listen
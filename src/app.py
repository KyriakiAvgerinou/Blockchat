from flask import Flask
from endpoints import node, blockchat_bp
from argparse import ArgumentParser
import config
from blockchain import Blockchain
import socket
import pickle
import threading
from libraries.functions_library import make_get_request, make_post_request, standardize_transaction_input
from libraries.custom_exceptions import SessionInitializationError

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
    # Retrieve the total number of nodes participating in the network. This is defined by the bootstrap node only.
    optional.add_argument("-nds", "--nodes", type = int, choices = [5, 10], help = "insert total number of nodes in the network")
    # Retrieve the transaction capacity of the blocks. This is defined by the bootstrap node only.
    optional.add_argument("--capacity", type = int, choices = [5, 10, 20], help = "insert block capacity")
    # Retrieve whether the current node is the bootstrap node.
    optional.add_argument("-btstrp", "--bootstrap", action = "store_true", help = "insert if the current node is the bootstrap")

    args = parser.parse_args()
    port = args.port # get the port
    nodes = args.nodes # temporarily hold args.nodes
    capacity = args.capacity # temporarily hold args.capacity
    is_bootstrap = args.bootstrap # get whether the node is the bootstrap

    if is_bootstrap:
        """
        If the current node is the bootstrap node:
            - set the global variables total_nodes and block_capacity in the bootstrap's installation.
            Also:
            - Initiate the bootstrap node (id = 0, ip = config.BOOTSTRAP_IP, port = config.BOOTSTRAP_PORT, is_bootstrap = True),
            - register the bootstrap node in the ring,
            - deposit 1000 * (the total number of nodes in the network) BCC in the bootstrap's wallet,
            - initiate the blockchain and generate the genesis block.
        """

        # Check that the total number of nodes and the block capacity have been specified in the command-line arguments.
        if nodes is None or capacity is None:
            raise SessionInitializationError("It is mandatory for the bootstrap node to specify the total number of nodes and the block capacity.")

        config.set_total_nodes(nodes) # set the global variable total_nodes
        total_nodes = config.total_nodes
        config.set_block_capacity(capacity) # set the global variable block_capacity

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
        If the registration is successful, retrieve the total number of nodes and the block capacity from the bootstrap node.
        If the current node is the last one to enter the network:
            - send bootstrap's FINAL ring of nodes to all the nodes in the network,
            - send bootstrap's initial version of the blockchain to all the nodes in the network,
            - send 1000 BCC to every node in the network.
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

        # Retrieve the total number of nodes from the bootstrap node.
        nodes = make_get_request(BOOTSTRAP_IP, BOOTSTRAP_PORT, endpoint = "get_total_nodes")
        nodes = nodes.json()["total_nodes"]
        # Set the global variable total_nodes in the current node's installation.
        config.set_total_nodes(nodes)
        total_nodes = config.total_nodes

        # Retrieve block capacity from the bootstrap node.
        capacity = make_get_request(BOOTSTRAP_IP, BOOTSTRAP_PORT, endpoint = "get_block_capacity")
        capacity = capacity.json()["block_capacity"]
        # Set the global variable block_capacity in the current node's installation.
        config.set_block_capacity(capacity)

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

                # Now that everyone in the network has the ring and the initial image of the blockchain,
                # the bootstrap will send everyone 1000 BCC,
                # so that we can get started.
                for ring_node in bootstrap_ring[1:]:
                    transaction_data = standardize_transaction_input(
                        recipient_id = ring_node["id"],
                        bcc = 1000,
                        message = "Here's your first 1000 BCC from the bootstrap node <3."
                    )
                    transaction_response = make_post_request(BOOTSTRAP_IP, BOOTSTRAP_PORT, endpoint = "make_transaction", data = transaction_data)
                    print(transaction_response.json()["message"].encode("utf-8"))

                # This is for testing the code.
                # Print out the balance of every node after the previous transactions.
                # for ring_node in bootstrap_ring:
                #    print(ring_node["id"])
                #    current_balance_response = make_get_request(ring_node["ip"], ring_node["port"], endpoint = "get_balance")
                #    print(current_balance_response.json()["current_balance"])

            req = threading.Thread(target = thread_function, args = ())
            req.start()

        # app.run(debug = True, host = node.ip, port = node.port)
        app.run(host = node.ip, port = node.port) # run the Flask development server and specify the ip address and port on which the Flask server should listen

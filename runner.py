"""
File: runner.py
Description:

    Runs all the nodes in the network.
    There are two case-scenarios: one with 5 nodes and one with 10 nodes.
    The bootstrap node is always the first one to run, to initialize the session.
    The block capacity is retrieved as a required command-line argument.
    The Blockchat Application resides in src/app.py.
    Before running a node, the python virtual environment is activated.
    Git Bash is used as the terminal emulator.

Usage: run "python runner.py --capacity {capacity, choices = [5, 10, 20]}"
"""

import subprocess
from src.config import BOOTSTRAP_PORT
from argparse import ArgumentParser
import time

def run_node(port, nodes, capacity):
    """
    Runs new node on port {port}.

    Input:
        port (int): port on which the new node will operate.
        nodes (int): the total number of nodes in the network.
        capacity (int): the block capacity.
    """
    blockchat_file = "src/app.py" # path to the Blockchat Application file

    venv_command = "source .venv/bin/activate" # the command that activates the python virtual environment

    # If this is the bootstrap node,
    # promulgate that this is the bootstrap node (-btstrp)
    # and set the total number of nodes and the block capacity for the session.
    if port == BOOTSTRAP_PORT:
        command = f"{venv_command} && python {blockchat_file} -prt {port} -nds {nodes} --capacity {capacity} -btstrp"
    else:
        command = f"{venv_command} && python {blockchat_file} -prt {port}"

    # Run command in a new terminal window.
    subprocess.Popen(["C:\\path\\to\\git-bash.exe", "-c", command])
    time.sleep(6)

if __name__ == "__main__":
    # Get block capacity from command-line arguments.
    parser = ArgumentParser(description = "Runner script.")
    parser.add_argument("--capacity", type = int, choices = [5, 10, 20], help = "insert block capacity", required = True)
    args = parser.parse_args()
    capacity = args.capacity

    # 5 nodes case-scenario
    node_ports = [BOOTSTRAP_PORT, {node_port_1}, {node_port_2}, {node_port_3}, {node_port_4}]
    # 10 nodes case-scenario
    # node_ports = [BOOTSTRAP_PORT, ]
    nodes = len(node_ports) # the total number of nodes

    # Start each node in a separate terminal
    for port in node_ports:
        run_node(port, nodes, capacity)

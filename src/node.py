from wallet import Wallet
from libraries.module_library import make_post_request, transaction_total_expenses, calculate_hash, retrieve_from_ring_node
import pickle
from transaction import Transaction
from libraries.custom_exceptions import InsufficientBalanceError, TransactionValidationError
import threading

class Node:

    def share_chain(self, requesting_node):
        """The self node posts its chain to the requesting_node's chain."""
        response = make_post_request(requesting_node["ip"], requesting_node["port"], endpoint = "post_chain", data = pickle.dumps(self.chain))
        return response.json()["message"]

    def create_transaction(self, recipient_id, recipient_public_key, bcc = None, message = None):
        """
        Creates a new transaction.
        The sender is the self node and the recipient is defined by the method's arguments.
        """
        # Get recipient ip address and port for future requests.
        recipient_ip = retrieve_from_ring_node(self.ring, recipient_id, "ip")
        recipient_port = retrieve_from_ring_node(self.ring, recipient_id, "port")

        # Calculate the total expenses of the transaction (before actually creating the transaction).
        total_expenses = transaction_total_expenses(bcc, message)

        # Check that the sender node has sufficient balance to make the transaction.
        if self.wallet.balance < total_expenses:
            raise InsufficientBalanceError(f"Transaction of {bcc} bcc and message: '{message}' from node {self.id} to node {recipient_id} declined due to insufficient sender balance.")

        # Create the transaction.
        trans = Transaction(self, recipient_id, recipient_public_key, bcc, message)
        # Make the total expenses of the transaction transaction specific.
        total_expenses = trans.total_expenses()

        # Subtract the total costs of the transaction from the sender's wallet.
        self.wallet.update_balance(-total_expenses)

        # Sign the transaction.
        trans.get_signature()

        # If the transaction is validated across all nodes in the network,
        # give the transaction its nonce,
        # add the transaction to the sender's wallet,
        # and broadcast the transaction to all the nodes in the network
        # to add the new transaction to their current_block.
        if self.broadcast_transaction_to_validate(trans):
            trans.update_nonce()
            self.wallet.transactions.append(trans)
            # Send the transaction bcc to the recipient node.
            if bcc > 0:
                send_recipient_bcc = make_post_request(recipient_ip, recipient_port, endpoint = "update_balance", data = {"amount": bcc})
                print(send_recipient_bcc.json()["message"])
            self.broadcast_transaction_to_block
        else:
        # If the transaction fails to validate,
        # return the total costs of the transaction back to the sender's wallet,
        # delete the created transaction,
        # and raise a validation error.
            self.wallet.update_balance(total_expenses)
            del trans
            raise TransactionValidationError("Τransaction of {bcc} bcc and message: '{message}' from node {self.id} to node {recipient_id} failed to validate across the nodes in the network.")

    def broadcast_transaction_to_validate(self, transaction):
        """
        Broadcasts the input transaction to all the nodes in the network
        and asks them to validate it.
        Returns True if all nodes validate the transaction,
        else returns False.
        """
        # To broadcast the transaction to all the nodes in the network at the same time,
        # we will create a distinct thread for every node in the network.
        def thread_function(ring_node, responses):
            validation_response = make_post_request(ring_node["ip"], ring_node["port"], endpoint = "validate_transaction", data = pickle.dumps(transaction))
            responses.append(validation_response)

        threads = [] # list to hold the threads
        responses = [] # list to store the responses from the /validate_transaction requests

        for ring_node in self.ring:
            # if ring_node["id"] != self.id: # exclude the sender node of the transaction
            thread = threading.Thread(target = thread_function, args = (ring_node, responses))
            threads.append(thread)
            thread.start()

        # Wait for all the generated subthreads to complete.
        # It is very important to collect the responses from all the nodes before proceeding.
        for thread in threads:
            thread.join()

        # If any node rejects the transaction, return False.
        for response in responses:
            if response.status_code < 200 or response.status_code >= 300:
                return False

        # At this point all nodes have validated the transaction.
        # Return True.
        return True

    def validate_transaction(self, transaction):
        """
        Validates an incoming transaction on behalf of the self node:
            - verify the signature of the transaction,
            - check whether the sender node has sufficient balance to make the transaction.
        """
        # Recalculate the hash of the transaction
        # and verify the signature of the transaction against this hash.
        # This ensures that the signature corresponds to the specific transaction data and hasn't been tampered with.
        recalculated_hash = calculate_hash(transaction.to_dict())
        if not transaction.verify_signature(recalculated_hash):
        # if not self.wallet.verify_signature(recalculated_hash, transaction.signature, transaction.sender.public_key):
            return False, "Invalid signature."

        if transaction.sender.wallet.balance < 0: # the total expenses of the transaction have already been subtracted from the sender's balance in the create_transaction() method
            return False, "Insufficient balance."

        return True, "Transaction validation successful."

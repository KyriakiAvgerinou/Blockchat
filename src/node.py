from libraries.module_library import make_post_request
import pickle

class Node:

    def share_chain(self, requesting_node):
        """The self node posts its chain to the requesting_node's chain."""
        response = make_post_request(requesting_node["ip"], requesting_node["port"], endpoint = "post_chain", data = pickle.dumps(self.chain))
        return response.json()["message"]

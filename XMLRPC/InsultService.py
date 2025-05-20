from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import threading
import time
import random
import sys
import redis
from socketserver import ThreadingMixIn

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class InsultService:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        # List of unique insults
        self.list_name = "XMLRPC-list"
        # Subscribers hold the XMLRPC URL of interested clients
        self.subscribers = []
        # Start the broadcaster thread (daemon so it ends with the main thread)
        self.broadcast_thread = threading.Thread(target=self._broadcast_insults, daemon=True)
        self.broadcast_thread.start()

    def add_insult(self, insult):
        """Adds an insult if it is not already present."""
        self.client.sadd(self.list_name, insult)

    def get_insults(self):
        """Returns the list of stored insults."""
        return list(self.client.smembers(self.list_name))

    def subscribe(self, callback_url):
        """Adds a subscriber identified by the XMLRPC callback URL.
        The subscriber must expose a method called 'notify' to receive broadcasted insults."""
        if callback_url not in self.subscribers:
            self.subscribers.append(callback_url)
            return True
        return False

    def _broadcast_insults(self):
        """Every 5 seconds, selects a random insult and notifies all subscribers."""
        while True:
            i_list = list(self.client.smembers(self.list_name))
            if len(i_list) > 0:
                insult = random.choice(i_list)
                for sub_url in self.subscribers:
                    try:
                        client = xmlrpc.client.ServerProxy(sub_url)
                        client.notify(insult)
                    except Exception as e:
                        print(f"Error broadcasting to {sub_url}: {e}")
            time.sleep(5)

def run_insult_service(port):
    server = ThreadedXMLRPCServer(("localhost", port), allow_none=True, logRequests=False)
    service = InsultService()
    server.register_instance(service)
    print(f"InsultService running on port {port}...")
    server.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python insultservice.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    run_insult_service(port)

import Pyro4
import threading
import time

@Pyro4.expose
class CallbackHandler:
    def receive_insult(self, insult):
        print(f"\nReceived broadcast insult: {insult}")

def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    
    handler = CallbackHandler()
    uri = daemon.register(handler)
    
    insult_service = Pyro4.Proxy("PYRONAME:insult.service")
    insult_service.subscribe(uri)
    
    print("Subscribed to insults. Waiting for broadcasts...")
    # Use regular thread for daemon
    daemon_thread = threading.Thread(target=daemon.requestLoop, daemon=True)
    daemon_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Unsubscribing...")
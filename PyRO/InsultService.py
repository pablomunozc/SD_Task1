import Pyro4
import threading
import time
import random

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultService:
    def __init__(self):
        self.insults = []
        self.subscribers = []
        self.lock = threading.Lock()
        self.broadcaster_thread = threading.Thread(target=self.broadcast_insults, daemon=True)
        self.broadcaster_thread.start()

    def add_insult(self, insult):
        with self.lock:
            if insult not in self.insults:
                self.insults.append(insult)
                print(f"Added new insult: {insult}")

    def get_insults(self):
        with self.lock:
            return self.insults.copy()

    def subscribe(self, callback):
        with self.lock:
            if callback not in self.subscribers:
                self.subscribers.append(callback)

    def broadcast_insults(self):
        while True:
            time.sleep(5)
            with self.lock:
                if not self.insults:
                    continue
                current_insults = self.insults.copy()
                subscribers = self.subscribers.copy()
            insult = random.choice(current_insults)
            for callback in subscribers:
                try:
                    callback.receive_insult(insult)
                except Pyro4.errors.ConnectionClosedError:
                    with self.lock:
                        if callback in self.subscribers:
                            self.subscribers.remove(callback)
                except Exception as e:
                    print(f"Error calling callback: {e}")

def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(InsultService)
    service_name = f"insult.service.{random.randint(0, 1000)}"
    ns.register(service_name, uri)
    print(f"InsultService is ready. Service name: {service_name}")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
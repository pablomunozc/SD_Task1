import Pyro4
import threading
import time
import random
from statistics import mean

SERVICE_NAME = "insult.service"
NUM_THREADS = 2       # Number of concurrent worker threads
TEST_DURATION = 30     # Duration of the test in seconds

# Collect latency statistics
timings = {
    'add': [],
    'get': [],
    'subscribe': []
}

class DummyCallback(object):
    def __init__(self, id):
        self.id = id
        self.received = 0

    @Pyro4.expose
    def receive_insult(self, insult):
        # Just count received insults
        self.received += 1


def worker(thread_id):
    uri = ns.lookup(SERVICE_NAME)
    service = Pyro4.Proxy(uri)
    callback = DummyCallback(thread_id)
    daemon = Pyro4.Daemon()
    cb_uri = daemon.register(callback)
    service.subscribe(callback)

    threading.Thread(target=daemon.requestLoop, daemon=True).start()

    end_time = time.time() + TEST_DURATION
    while time.time() < end_time:
        # Randomly choose operation
        op = random.choice(['add', 'get'])
        if op == 'add':
            insult = f"insult-{thread_id}-{random.randint(0,10000)}"
            start = time.time()
            try:
                service.add_insult(insult)
            except Exception as e:
                print(f"Error in add_insult: {e}")
            timings['add'].append(time.time() - start)
        else:
            start = time.time()
            try:
                _ = service.get_insults()
            except Exception as e:
                print(f"Error in get_insults: {e}")
            timings['get'].append(time.time() - start)
    daemon.shutdown()
    print(f"Thread {thread_id} received {callback.received} insults")

if __name__ == '__main__':
    # Locate name server and launch workers
    ns = Pyro4.locateNS()

    print(f"Starting stress test: {NUM_THREADS} threads for {TEST_DURATION}s")
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    # Report results
    print("Stress test complete. Latencies:")
    for op in timings:
        if timings[op]:
            print(f" {op}: avg={mean(timings[op]) * 1000:.2f} ms, max={max(timings[op]) * 1000:.2f} ms, min={min(timings[op]) * 1000:.2f} ms")
        else:
            print(f" {op}: no data")


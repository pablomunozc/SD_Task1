import time
import xmlrpc.client
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed

# 🔁 Llista de nodes InsultService
SERVER_URLS = [
    "http://localhost:9000",
    "http://localhost:9001",
    "http://localhost:9002"
]
server_cycle = itertools.cycle(SERVER_URLS)

# 🔧 Configuració
NUM_REQUESTS = 6000
MAX_WORKERS = 30  # Concurrency level

def make_request():
    url = next(server_cycle)
    try:
        proxy = xmlrpc.client.ServerProxy(url)
        return proxy.get_insults()
    except Exception as e:
        return f"Error from {url}: {e}"

def stress_test():
    start_time = time.time()
    successes, failures = 0, 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(make_request) for _ in range(NUM_REQUESTS)]
        for future in as_completed(futures):
            result = future.result()
            if isinstance(result, list):
                successes += 1
            else:
                failures += 1

    end_time = time.time()
    print(f"\n✅ Total requests: {NUM_REQUESTS}")
    print(f"✅ Successes: {successes}")
    print(f"❌ Failures: {failures}")
    print(f"⏱️ Total time: {end_time - start_time:.2f} s")
    print(f"⚡ Requests per second: {NUM_REQUESTS / (end_time - start_time):.2f}")

if __name__ == "__main__":
    stress_test()

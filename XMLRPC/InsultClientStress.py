import time
import xmlrpc.client
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuració
SERVER_URL = "http://localhost:9000"
NUM_REQUESTS = 1000
MAX_WORKERS = 10  # Concurrency level

def make_request():
    try:
        proxy = xmlrpc.client.ServerProxy(SERVER_URL)
        return proxy.get_insults()
    except Exception as e:
        return f"Error: {e}"

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

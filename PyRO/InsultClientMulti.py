import time
import Pyro4
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor, as_completed

NUM_REQUESTS = 6000
MAX_WORKERS = 30

def discover_services():
    ns = Pyro4.locateNS()
    services = ns.list(prefix="insult.service.")
    return services.values()

def stress_test():

    services = discover_services()
    if not services:
        raise Exception("No se encontraron servicios registrados!")
    
    print(f"🌍 Nodos descubiertos: {len(services)}")
    uri_pool = cycle(services)

    def make_request():
        try:
            current_uri = next(uri_pool)
            proxy = Pyro4.Proxy(current_uri)
            return proxy.get_insults()
        except Exception as e:
            return f"Error: {e}"

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

    total_time = time.time() - start_time
    print(f"\n✅ Total requests: {NUM_REQUESTS}")
    print(f"🌐 Nodes used: {len(services)}")
    print(f"✅ Successes: {successes}")
    print(f"❌ Failures: {failures}")
    print(f"⏱️ Total time: {total_time:.2f} s")
    print(f"⚡ Requests/sec: {NUM_REQUESTS / total_time:.2f}")

if __name__ == "__main__":
    stress_test()
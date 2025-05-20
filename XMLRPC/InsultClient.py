import threading
import time
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

# Callback handler for receiving broadcast notifications.
class InsultClient:
    def notify(self, insult):
        print(f"[Broadcast Received] {insult}")
        return True

def run_callback_server(port):
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True, logRequests=False)
    server.register_instance(InsultClient())
    print(f"Callback server running on port {port}")
    server.serve_forever()

def main():
    # Set up and run the callback server in a separate thread.
    callback_port = 9002
    callback_thread = threading.Thread(target=run_callback_server, args=(callback_port,), daemon=True)
    callback_thread.start()

    # Create proxies for the InsultService and InsultFilterService.
    insult_service = xmlrpc.client.ServerProxy("http://localhost:9000", allow_none=True)
    filter_service = xmlrpc.client.ServerProxy("http://localhost:9001", allow_none=True)

    # Subscribe to the InsultService broadcasts.
    callback_url = f"http://localhost:{callback_port}"
    if insult_service.subscribe(callback_url):
        print("Subscribed to insult broadcasts.")
    else:
        print("Already subscribed or subscription failed.")

    # Interact with the InsultService.
    print("\n--- InsultService Actions ---")
    insultList=["malxinat", "bretol", "baliga-balaga", "estaquirot", "milhomes", "esquifit"]

    for insult in insultList:
        if insult_service.add_insult(insult):
            print(f"Insult added: '{insult}'")
        else:
            print(f"Insult already exists: '{insult}'")

    print("\nCurrent insults stored:")
    insults = insult_service.get_insults()
    print(insults)

    # Interact with the InsultFilter Service.
    print("\n--- InsultFilterService Actions ---")
    sample_text = "Ets un estaquirot, un bretol, un milhomes esquifit i malxinat"
    print("Original text:")
    print(sample_text)

    response = filter_service.filter_text(sample_text)
    print("Filter service response:", response)

    # Give the filter service a moment to process the text.
    time.sleep(1)

    print("\nFiltered texts:")
    filtered_texts = filter_service.get_filtered_texts()
    print(filtered_texts)

    # Keep the client running so that broadcast messages can be received.
    print("\nClient running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Client exiting.")

if __name__ == '__main__':
    main()

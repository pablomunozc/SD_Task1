from xmlrpc.server import SimpleXMLRPCServer
import threading
import queue
import re

class InsultFilterService:
    def __init__(self, insults):
        # This service needs an initial list of insults to search for.
        # In a real application, you might share this with the InsultService or load it from a common source.
        self.insults = insults
        self.results = []      # List to store filtered texts
        self.work_queue = queue.Queue()
        # Start the worker thread (daemon so it stops with the main thread)
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def filter_text(self, text):
        """Submits text for processing.
        The text will be filtered for insults and then stored in the results list.
        Returns a confirmation message."""
        self.work_queue.put(text)
        return "Text submitted for filtering."

    def get_filtered_texts(self):
        """Returns the list of filtered texts."""
        return self.results

    def _process_queue(self):
        """Continuously processes texts from the queue.
        For each text, any occurrence of an insult is replaced with 'CENSORED' (case-insensitive)."""
        while True:
            text = self.work_queue.get()
            filtered_text = text
            for insult in self.insults:
                if insult in filtered_text:
                    filtered_text=filtered_text.replace(insult, "CENSORED")
            self.results.append(filtered_text)
            self.work_queue.task_done()

def run_insult_filter_service(insults):
    # The filter service runs on localhost at port 9001
    server = SimpleXMLRPCServer(("localhost", 9001), allow_none=True)
    service = InsultFilterService(insults)
    server.register_instance(service)
    print("InsultFilterService running on port 9001...")
    server.serve_forever()

if __name__ == '__main__':
    # For demonstration, we initialize with a default insult list.
    # In practice, this might be dynamically updated or shared with the InsultService.
    default_insults = ["malxinat", "bretol", "baliga-balaga", "estaquirot", "milhomes", "esquifit"]
    run_insult_filter_service(default_insults)
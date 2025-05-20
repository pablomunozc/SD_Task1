import Pyro4
import threading
from queue import Queue

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultFilterService:
    def __init__(self):
        # Local predefined list of insults
        self.insults = ["bretol", "estaquirot", "baliga-balaga", "milhomes", "malxinat"]
        self.work_queue = Queue()
        self.results = []
        self.results_lock = threading.Lock()
        
        # Start worker threads
        self.worker_threads = []
        for _ in range(3):
            worker = threading.Thread(target=self.process_text, daemon=True)
            worker.start()
            self.worker_threads.append(worker)

    def submit_text(self, text):
        self.work_queue.put(text)

    def process_text(self):
        while True:
            text = self.work_queue.get()
            # Case-insensitive check with stemming
            filtered_words = []
            for word in text.split():
                if word.lower() in self.insults:
                    filtered_words.append("CENSORED")
                else:
                    filtered_words.append(word)
            filtered_text = ' '.join(filtered_words)
            
            with self.results_lock:
                self.results.append(filtered_text)
            self.work_queue.task_done()

    def get_filtered_texts(self):
        with self.results_lock:
            return self.results.copy()

def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(InsultFilterService)
    ns.register("insult.filter.service", uri)
    print("InsultFilterService is ready.")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
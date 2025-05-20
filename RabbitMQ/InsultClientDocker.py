import time
import pika
from concurrent.futures import ThreadPoolExecutor, as_completed

# 🔧 Configuración
NUM_REQUESTS = 120000
MAX_WORKERS = 90
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'add_insult_queue'

class QueueMonitor:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOST,  
            port=5672,         
            virtual_host='/',
            credentials=pika.PlainCredentials('guest', 'guest'))
)
        self.channel = self.connection.channel()
        
    def get_message_count(self):
        queue = self.channel.queue_declare(queue=QUEUE_NAME, passive=True)
        return queue.method.message_count
    
    def purge_queue(self):
        self.channel.queue_purge(QUEUE_NAME)
        
    def close(self):
        self.connection.close()

def worker_task(num_requests):
    successes = 0
    failures = 0
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = conn.channel()
        
        for _ in range(num_requests):
            try:
                channel.basic_publish(
                    exchange='',
                    routing_key=QUEUE_NAME,
                    body='Insulto de stress test',
                    properties=pika.BasicProperties(delivery_mode=1)
                )
                successes += 1
            except Exception as e:
                failures += 1
                print(f"Error enviando mensaje: {str(e)}")
        
        conn.close()
    except Exception as e:
        failures = num_requests
        print(f"Error conexión RabbitMQ: {str(e)}")
    
    return successes, failures

def stress_test():
    monitor = QueueMonitor()
    monitor.purge_queue()
    start_time = time.time()

    # Fase de envio masivo
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        requests_per_worker = NUM_REQUESTS // MAX_WORKERS
        remaining = NUM_REQUESTS % MAX_WORKERS
        
        futures = []
        for _ in range(MAX_WORKERS):
            futures.append(executor.submit(worker_task, requests_per_worker))
        
        if remaining > 0:
            futures.append(executor.submit(worker_task, remaining))

        total_successes, total_failures = 0, 0
        for future in as_completed(futures):
            successes, failures = future.result()
            total_successes += successes
            total_failures += failures

    # Fase de espera hasta cola vacía
    while True:
        current_count = monitor.get_message_count()
        if current_count == 0:
            break
        print(f"Esperando... Mensajes pendientes: {current_count}")
        time.sleep(0.5)
    
    end_time = time.time()
    monitor.close()

    # Resultados
    total_time = end_time - start_time
    print("\n📊 Resultados finales:")
    print(f"• Total requests: {NUM_REQUESTS}")
    print(f"• Éxitos: {total_successes}")
    print(f"• Fallos: {total_failures}")
    print(f"• Tiempo total: {total_time:.2f} segundos")
    print(f"• Throughput: {NUM_REQUESTS / total_time:.2f} ops/seg")

if __name__ == "__main__":
    stress_test()
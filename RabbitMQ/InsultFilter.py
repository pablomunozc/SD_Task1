import pika
import threading
import json

class InsultFilter:
    def __init__(self):
        self.static_insults = ["dummy", "stupid", "jerk"]  # Example static list
        self.results = []
        self.lock = threading.Lock()
        
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        
        # Declare queues
        self.channel.queue_declare(queue='filter_text_queue')
        self.channel.queue_declare(queue='get_results_queue')
        
        # Prefetch count for fair dispatch
        self.channel.basic_qos(prefetch_count=1)
        
        # Set up consumers
        self.channel.basic_consume(queue='filter_text_queue', on_message_callback=self.handle_filter_text, auto_ack=True)
        self.channel.basic_consume(queue='get_results_queue', on_message_callback=self.handle_get_results)

    def handle_filter_text(self, ch, method, properties, body):
        text = body.decode()
        filtered_words = []
        for word in text.split():
            if word.lower() in self.static_insults:
                filtered_words.append("CENSORED")
            else:
                filtered_words.append(word)
        filtered_text = ' '.join(filtered_words)
        with self.lock:
            self.results.append(filtered_text)

    def handle_get_results(self, ch, method, props, body):
        with self.lock:
            response = json.dumps(self.results)
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self.channel.start_consuming()

if __name__ == '__main__':
    filter_service = InsultFilter()
    filter_service.run()
import pika
import sys

def send_text_to_filter(text):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='filter_text_queue')
    channel.basic_publish(
        exchange='',
        routing_key='filter_text_queue',
        body=text
    )
    print(f" [x] Sent text for filtering: {text}")
    connection.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python filter_client.py <text>")
        sys.exit(1)
    send_text_to_filter(' '.join(sys.argv[1:]))
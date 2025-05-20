import pika
import sys

def add_insult(insult):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='add_insult_queue')
    channel.basic_publish(
        exchange='',
        routing_key='add_insult_queue',
        body=insult
    )
    print(f" [x] Sent insult: {insult}")
    connection.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python add_insult_client.py <insult>")
        sys.exit(1)
    add_insult(' '.join(sys.argv[1:]))
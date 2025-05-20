import pika
import threading
import time
import json
import redis
import os
import socket
from threading import Thread

class InsultService:
    def __init__(self):
        # Conexión a Redis
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

        # Conexión para agregar y recuperar insultos
        self.main_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.main_channel = self.main_connection.channel()
        
        # Declarar colas
        self.main_channel.queue_declare(queue='add_insult_queue')
        self.main_channel.queue_declare(queue='get_insults_queue')
        
        # Configurar consumidores
        self.main_channel.basic_consume(queue='add_insult_queue', on_message_callback=self.handle_add_insult, auto_ack=True)
        self.main_channel.basic_consume(queue='get_insults_queue', on_message_callback=self.handle_get_insults)
        
        # Conexión separada para broadcasting
        self.broadcast_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.broadcast_channel = self.broadcast_connection.channel()
        self.broadcast_channel.exchange_declare(exchange='insult_broadcast', exchange_type='fanout')
        
        # Iniciar hilo de broadcasting
        self.broadcaster_thread = threading.Thread(target=self.broadcast_insult)
        self.broadcaster_thread.daemon = True
        self.broadcaster_thread.start()

        # Registro del nodo
        self.node_id = socket.gethostname()
        self.redis = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'))
        self.redis.sadd("insult_service:nodes", self.node_id)
        
        # Heartbeat
        self.heartbeat_thread = Thread(target=self.send_heartbeat)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def send_heartbeat(self):
        while True:
            self.redis.expire("insult_service:nodes", 300)  # 5 minutos de TTL
            self.redis.sadd("insult_service:nodes", self.node_id)
            time.sleep(60)


    def handle_add_insult(self, ch, method, properties, body):
        insult = body.decode()
        # Agregar insulto a Redis (set automáticamente maneja duplicados)
        self.redis.sadd('insults', insult)

    def handle_get_insults(self, ch, method, props, body):
        # Obtener todos los insultos de Redis
        insults = self.redis.smembers('insults')
        # Convertir bytes a strings y crear lista
        insult_list = [insult.decode('utf-8') for insult in insults]
        response = json.dumps(insult_list)
        
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def broadcast_insult(self):
        while True:
            time.sleep(5)
            # Obtener insulto aleatorio de Redis
            insult = self.redis.srandmember('insults')
            if insult:
                self.broadcast_channel.basic_publish(
                    exchange='insult_broadcast',
                    routing_key='',
                    body=insult  # Ya está en bytes desde Redis
                )
    

    def run(self):
        self.main_channel.start_consuming()

if __name__ == '__main__':
    service = InsultService()
    service.run()
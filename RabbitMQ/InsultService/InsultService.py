import pika
import threading
import time
import json
import redis
import os
import socket
from threading import Thread
from pika.exceptions import AMQPConnectionError

class InsultService:
    def __init__(self):
        self.rabbit_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.redis_host = os.getenv('REDIS_HOST', 'redis')
        self.max_retries = 5
        self.retry_interval = 5  # segundos
        
        # Conexión a RabbitMQ con reintentos
        self._connect_rabbitmq()
        
        # Conexión a Redis
        self.redis = redis.Redis(host=self.redis_host, port=6379, db=0)

        self.main_channel = self.main_connection.channel()
        
        # Declarar colas
        self.main_channel.queue_declare(queue='add_insult_queue')
        self.main_channel.queue_declare(queue='get_insults_queue')
        
        # Configurar consumidores
        self.main_channel.basic_consume(queue='add_insult_queue', on_message_callback=self.handle_add_insult, auto_ack=True)
        self.main_channel.basic_consume(queue='get_insults_queue', on_message_callback=self.handle_get_insults)

        # Registro del nodo
        self.node_id = socket.gethostname()
        self.redis.sadd("insult_service:nodes", self.node_id)
        
        # Heartbeat
        self.heartbeat_thread = Thread(target=self.send_heartbeat)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def _connect_rabbitmq(self):
        """Establece conexión con RabbitMQ con reintentos"""
        for i in range(self.max_retries):
            try:
                self.main_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.rabbit_host,
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                print("✅ Conexión exitosa con RabbitMQ")
                return
            except AMQPConnectionError as e:
                print(f"⚠️ Intento {i+1}/{self.max_retries} fallido: {e}")
                if i < self.max_retries - 1:
                    time.sleep(self.retry_interval)
        
        raise RuntimeError("No se pudo conectar a RabbitMQ después de varios intentos")

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
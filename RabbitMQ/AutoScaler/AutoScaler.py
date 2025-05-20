import time
import requests
import subprocess
import docker
import redis
from threading import Thread
from datetime import datetime, timedelta
import os

class AutoScaler:
    def __init__(self):
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')  # Nombre del servicio
        self.rabbitmq_api = f"http://{self.rabbitmq_host}:15672/api"
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')
        self.redis_host = os.getenv('REDIS_HOST', 'redis')
        self.min_nodes = 1
        self.max_nodes = 10
        self.scale_up_threshold = 50  # Mensajes por nodo
        self.scale_down_threshold = 10
        self.cooldown = timedelta(seconds=30)
        self.last_scale_time = datetime.now() - self.cooldown
        self.docker_client = docker.from_env()
        self.current_nodes = 0
        
        # Registro de nodos en Redis
        self.redis = redis.Redis(host=self.redis_host, port=6379, db=0)
        self.redis_key = "insult_service:nodes"
        
        # Iniciar monitorización
        Thread(target=self.monitor_loop, daemon=True).start()
    
    def get_queue_stats(self):
        try:
            response = requests.get(
                f"{self.rabbitmq_api}/queues/%2F/add_insult_queue",
                auth=(self.rabbitmq_user, self.rabbitmq_pass),
                timeout=5
            )
            return response.json()
        except Exception as e:
            print(f"Error RabbitMQ API: {e}")
            return None
    
    def get_active_nodes(self):
        return self.redis.scard(self.redis_key)
    
    def scale_service(self, desired_count):
        if datetime.now() - self.last_scale_time < self.cooldown:
            return
            
        current_nodes = self.get_active_nodes()
        
        if desired_count == current_nodes:
            return
        elif desired_count > current_nodes:
            self.scale_up(desired_count - current_nodes)
        else:
            self.scale_down(current_nodes - desired_count)
        
        self.last_scale_time = datetime.now()
    
    def scale_up(self, num_nodes):
        print(f"🔼 Escalando +{num_nodes} nodos", flush=True)
        network = self.docker_client.networks.get("rabbitmq_app_network")  # Nombre exacto de la red
        for _ in range(num_nodes):
            container = self.docker_client.containers.run(
                "insult-service-image",
                detach=True,
                environment={
                    "RABBITMQ_HOST": "rabbitmq",
                    "REDIS_HOST": self.redis_host
                },
                network=network.name
            )
            node_id = container.id[:12]
            self.redis.sadd(self.redis_key, node_id)
    
    def scale_down(self, num_nodes):
        print(f"🔽 Reduciendo -{num_nodes} nodos", flush=True)
        nodes = [node_id.decode('utf-8') for node_id in self.redis.smembers(self.redis_key)]
        for node_id in nodes[:num_nodes]:
            try:
                container = self.docker_client.containers.get(node_id)
                container.stop(timeout=30)
                self.redis.srem(self.redis_key, node_id)
            except Exception as e:
                print(f"Error deteniendo nodo {node_id}: {e}", flush=True)
    
    def calculate_desired_nodes(self, queue_length, current_nodes):
        if current_nodes == 0:
            return self.min_nodes
            
        messages_per_node = queue_length / current_nodes
        
        if messages_per_node > self.scale_up_threshold:
            return min(current_nodes + 1, self.max_nodes)
        elif messages_per_node < self.scale_down_threshold:
            return max(current_nodes - 1, self.min_nodes)
        return current_nodes
    
    def monitor_loop(self):
        while True:
            stats = self.get_queue_stats()
            if not stats:
                time.sleep(5)
                continue
                
            current_nodes = self.get_active_nodes()
            queue_length = stats.get('messages_ready', 0)
            print(f"Cola actual: {queue_length}", flush=True)
            desired_nodes = self.calculate_desired_nodes(queue_length, current_nodes)
            self.scale_service(desired_nodes)
            
            time.sleep(5)

if __name__ == "__main__":
    scaler = AutoScaler()
    while True: 
        time.sleep(1)
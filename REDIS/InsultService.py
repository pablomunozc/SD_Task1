import redis
import random
import threading
import time


def broadcast():
    while True:
        insults = client.smembers(list_name)
        if len(list(insults)) > 0:
            insult = random.choice(list(insults))
            client.publish(channel_name, insult)
        time.sleep(5)  # Simulating delay between messages

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "insult_queue"
list_name = "INSULTS"
channel_name = "insult_channel"

print("Consumer is waiting for tasks...")

t = threading.Thread(target=broadcast)
t.start()

while True:
    task = client.blpop(queue_name, timeout=0)  # Blocks indefinitely until a task is available
    if task:
        client.sadd(list_name, task[1])



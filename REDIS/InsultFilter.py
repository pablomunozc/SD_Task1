import redis
import random
import threading
import time


# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "work_queue"
list_name = "result_list"
insults_name = "INSULTS"


while True:
    task = client.blpop(queue_name, timeout=0)  # Blocks indefinitely until a task is available
    if task:
        message = task[1]
        insults = client.smembers(insults_name)
        for insult in list(insults):
            if insult in message:
                message = message.replace(insult, "CENSORED")
        print(f"Message received: {message}")
        client.lpush(list_name, message)
        
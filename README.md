# SD_Task1
Task1 Implementation from SD

## XML-RPC
### Requirements
- xmlrpc
- redis
- itertools
### How to use
- python3 InsultService.py
- python3 InsultFilter.py
- python3 InsultClient.py (for single-node)
- python3 InsultClientMulti.py (for 3 nodes)

## PyRO
### Requirements
- Pyro4
- itertools
### How to use
- Start PyRO.naming service
- python3 InsultService.py (up to 3)
- python3 InsultFilter.py
- python3 InsultClientMulti.py

## REDIS
### Requirements
- redis
### How to use
- Start REDIS database
- python3 InsultService.py (up to 3)
- python3 InsultFilter.py
- python3 InsultClientMulti.py

## RabbitMQ
### Requirements
- pika
- docker
- redis
### How to use (without scaling)
- Start RabbitMQ service
- python3 InsultService.py (up to 3)
- python3 InsultFilter.py
- python3 InsultClientMulti.py
### How to use (with dynamic scaling)
- docker-compose build
- docker-compose up -d

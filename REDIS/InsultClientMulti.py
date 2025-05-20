import time
import random
import redis
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración
REDIS_HOST = "localhost"
REDIS_PORT = 6379
QUEUE_NAME = "insult_queue"
NUM_REQUESTS = 12000
MAX_WORKERS = 100  # Nivel de concurrencia

# Configurar el cliente Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_timeout=5  # Tiempo de espera para operaciones
)

def generate_insult():
    """Genera un insulto aleatorio simple"""
    return f"insulto-{random.randint(1, 1000000)}"

def make_request():
    try:
        insult = generate_insult()
        # Usamos LPUSH para añadir al principio de la lista
        result = redis_client.lpush(QUEUE_NAME, insult)
        return result
    except Exception as e:
        return e

def stress_test():
    start_time = time.time()
    successes, failures = 0, 0
    redis_client.delete(QUEUE_NAME)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(make_request) for _ in range(NUM_REQUESTS)]
        
        for future in as_completed(futures):
            result = future.result()
            if isinstance(result, int) and result > 0:
                successes += 1
            else:
                failures += 1

    insertion_time = time.time() - start_time
    print(f"\n📤 Inserción completada en {insertion_time:.2f}s")
    print(f"✅ Inserciones exitosas: {successes}/{NUM_REQUESTS}")

    # Esperar a que se vacíe la cola
    print("\n⏳ Esperando a que la cola se vacíe...")
    queue_processing_start = time.time()
    
    try:
        while True:
            current_length = redis_client.llen(QUEUE_NAME)
            # Verificar si la cola está vacía
            if current_length == 0:
                processing_time = time.time() - queue_processing_start
                print(f"\n🔄 Tiempo de procesamiento de la cola: {processing_time:.2f}s")
                break
    except KeyboardInterrupt:
        print("\n❌ Interrupción manual - Deteniendo el monitoreo")
        processing_time = time.time() - queue_processing_start
        print(f"⏱ Tiempo parcial de procesamiento: {processing_time:.2f}s")
        raise

    total_time = time.time() - start_time
    
    # Estadísticas finales
    print("\n📈 Resumen final:")
    print(f"⏱ Tiempo total (inserción + procesamiento): {total_time:.2f}s")
    print(f"⚡ Tasa global: {NUM_REQUESTS / total_time:.2f} ops/s")
    print(f"📤 Velocidad inserción: {NUM_REQUESTS / insertion_time:.2f} ops/s")
    print(f"📥 Velocidad procesamiento: {NUM_REQUESTS / processing_time:.2f} ops/s")

if __name__ == "__main__":
    stress_test()
from fastapi import FastAPI
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import threading
import time

app = FastAPI(title="Users Service with Kafka")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
REQUEST_TOPIC = "user_requests"
RESPONSE_TOPIC = "product_responses"

users_db = {
    1: {
        "id": 1,
        "name": "Alice Martin",
        "email": "alice.martin@example.com",
        "city": "Paris",
        "role": "student"
    },
    2: {
        "id": 2,
        "name": "Bob Karim",
        "email": "bob.karim@example.com",
        "city": "Lyon",
        "role": "developer"
    },
    3: {
        "id": 3,
        "name": "Chloe Bernard",
        "email": "chloe.bernard@example.com",
        "city": "Marseille",
        "role": "designer"
    },
    4: {
        "id": 4,
        "name": "David Morel",
        "email": "david.morel@example.com",
        "city": "Toulouse",
        "role": "qa"
    },
    5: {
        "id": 5,
        "name": "Emma Laurent",
        "email": "emma.laurent@example.com",
        "city": "Nantes",
        "role": "product-owner"
    },
    6: {
        "id": 6,
        "name": "Farid Naji",
        "email": "farid.naji@example.com",
        "city": "Lille",
        "role": "data-analyst"
    },
    7: {
        "id": 7,
        "name": "Grace Dupont",
        "email": "grace.dupont@example.com",
        "city": "Bordeaux",
        "role": "student"
    },
    8: {
        "id": 8,
        "name": "Hugo Petit",
        "email": "hugo.petit@example.com",
        "city": "Rennes",
        "role": "devops"
    },
    9: {
        "id": 9,
        "name": "Ines Faure",
        "email": "ines.faure@example.com",
        "city": "Nice",
        "role": "student"
    },
    10: {
        "id": 10,
        "name": "Jules Simon",
        "email": "jules.simon@example.com",
        "city": "Strasbourg",
        "role": "backend-engineer"
    }
}

producer = None

responses_cache = {}


def get_kafka_producer(retries: int = 20, delay_seconds: float = 1.0):
    global producer

    if producer is not None:
        return producer

    for _ in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            return producer
        except NoBrokersAvailable:
            time.sleep(delay_seconds)

    raise NoBrokersAvailable()


def consume_product_responses():
    while True:
        try:
            consumer = KafkaConsumer(
                RESPONSE_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="latest",
                group_id="users-service-group"
            )

            for message in consumer:
                payload = message.value
                user_id = payload.get("user_id")
                if user_id is not None:
                    responses_cache[user_id] = payload.get("products", [])
        except NoBrokersAvailable:
            time.sleep(1.0)


@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=consume_product_responses, daemon=True)
    thread.start()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        return {"error": "User not found"}

    try:
        producer_client = get_kafka_producer()
    except NoBrokersAvailable:
        return {**user, "products": [], "warning": "Kafka unavailable"}

    responses_cache.pop(user_id, None)
    producer_client.send(REQUEST_TOPIC, {"user_id": user_id})
    producer_client.flush()

    timeout_seconds = 10
    start = time.time()

    while time.time() - start < timeout_seconds:
        if user_id in responses_cache:
            return {**user, "products": responses_cache.pop(user_id)}
        time.sleep(0.1)

    return {**user, "products": [], "warning": "Timeout waiting for Kafka response"}

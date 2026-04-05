from fastapi import FastAPI
from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import time

app = FastAPI(title="Users Service with Kafka")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
REQUEST_TOPIC = "user_requests"
RESPONSE_TOPIC = "product_responses"

users_db = {
    1: {"id": 1, "name": "Alice"},
    2: {"id": 2, "name": "Bob"}
}

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

responses_cache = {}


def consume_product_responses():
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


@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=consume_product_responses, daemon=True)
    thread.start()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        return {"error": "User not found"}

    responses_cache.pop(user_id, None)
    producer.send(REQUEST_TOPIC, {"user_id": user_id})
    producer.flush()

    timeout_seconds = 10
    start = time.time()

    while time.time() - start < timeout_seconds:
        if user_id in responses_cache:
            return {**user, "products": responses_cache.pop(user_id)}
        time.sleep(0.1)

    return {**user, "products": [], "warning": "Timeout waiting for Kafka response"}

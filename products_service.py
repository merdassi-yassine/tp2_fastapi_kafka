from fastapi import FastAPI
from kafka import KafkaProducer, KafkaConsumer
import json

app = FastAPI(title="Products Service with Kafka")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
REQUEST_TOPIC = "user_requests"
RESPONSE_TOPIC = "product_responses"

products_db = {
    1: [{"id": 1, "name": "Book"}, {"id": 2, "name": "Pen"}],
    2: [{"id": 3, "name": "Laptop"}]
}

producer = None
consumer = None


@app.get("/products/{user_id}")
def get_products(user_id: int):
    return products_db.get(user_id, [])


def init_kafka():
    global producer, consumer

    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    if consumer is None:
        consumer = KafkaConsumer(
            REQUEST_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
            group_id="products-service-group"
        )


def process_requests():
    init_kafka()
    print("Products service is listening on Kafka...")
    for message in consumer:
        payload = message.value
        user_id = payload.get("user_id")
        products = products_db.get(user_id, [])

        producer.send(RESPONSE_TOPIC, {
            "user_id": user_id,
            "products": products
        })
        producer.flush()


if __name__ == "__main__":
    process_requests()

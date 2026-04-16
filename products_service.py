from fastapi import FastAPI
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import time

app = FastAPI(title="Products Service with Kafka")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
REQUEST_TOPIC = "user_requests"
RESPONSE_TOPIC = "product_responses"

products_db = {
    1: [
        {"id": 101, "name": "Python Book", "category": "books", "price": 29.90, "stock": 14},
        {"id": 102, "name": "Notebook A5", "category": "stationery", "price": 6.50, "stock": 40},
        {"id": 103, "name": "Blue Pen", "category": "stationery", "price": 1.20, "stock": 120}
    ],
    2: [
        {"id": 201, "name": "Laptop 14", "category": "electronics", "price": 899.00, "stock": 5},
        {"id": 202, "name": "Wireless Mouse", "category": "electronics", "price": 24.99, "stock": 26},
        {"id": 203, "name": "USB-C Hub", "category": "electronics", "price": 39.00, "stock": 18}
    ],
    3: [
        {"id": 301, "name": "Graphic Tablet", "category": "design", "price": 159.00, "stock": 7},
        {"id": 302, "name": "Color Markers Set", "category": "design", "price": 32.90, "stock": 12}
    ],
    4: [
        {"id": 401, "name": "Mechanical Keyboard", "category": "electronics", "price": 79.00, "stock": 9},
        {"id": 402, "name": "Monitor 24", "category": "electronics", "price": 199.00, "stock": 11}
    ],
    5: [
        {"id": 501, "name": "Planner 2026", "category": "office", "price": 14.90, "stock": 25},
        {"id": 502, "name": "Sticky Notes Pack", "category": "office", "price": 4.80, "stock": 60}
    ],
    6: [
        {"id": 601, "name": "External SSD 1TB", "category": "storage", "price": 119.00, "stock": 13},
        {"id": 602, "name": "Data Cable", "category": "accessories", "price": 9.50, "stock": 48},
        {"id": 603, "name": "Webcam HD", "category": "electronics", "price": 49.00, "stock": 16}
    ],
    7: [
        {"id": 701, "name": "Backpack", "category": "lifestyle", "price": 42.00, "stock": 10},
        {"id": 702, "name": "Water Bottle", "category": "lifestyle", "price": 12.00, "stock": 33}
    ],
    8: [
        {"id": 801, "name": "Server Guide", "category": "books", "price": 34.50, "stock": 8},
        {"id": 802, "name": "Ethernet Cable", "category": "network", "price": 7.90, "stock": 70},
        {"id": 803, "name": "Raspberry Pi Kit", "category": "hardware", "price": 95.00, "stock": 6}
    ],
    9: [
        {"id": 901, "name": "Noise Cancelling Headset", "category": "audio", "price": 129.00, "stock": 9},
        {"id": 902, "name": "E-Reader", "category": "electronics", "price": 119.00, "stock": 7}
    ],
    10: [
        {"id": 1001, "name": "API Design Book", "category": "books", "price": 31.00, "stock": 15},
        {"id": 1002, "name": "Docking Station", "category": "electronics", "price": 149.00, "stock": 4},
        {"id": 1003, "name": "Desk Lamp", "category": "office", "price": 27.90, "stock": 20}
    ]
}

producer = None
consumer = None


@app.get("/products/{user_id}")
def get_products(user_id: int):
    return products_db.get(user_id, [])


def init_kafka(retries: int = 20, delay_seconds: float = 1.0):
    global producer, consumer

    for _ in range(retries):
        try:
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

            return
        except NoBrokersAvailable:
            time.sleep(delay_seconds)

    raise NoBrokersAvailable()


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

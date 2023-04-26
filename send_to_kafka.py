import logging
import os
import random
import string
import time

from dotenv import load_dotenv
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError

from protobuf_schema.input_message_pb2 import InputMessage

# Load env variables from .env
load_dotenv(".env")
fake = Faker()

ACCOUNT_IDS_RANGE = (100, 304)

# Set up Kafka
INPUT_EVENTS_TOPIC = 'input_events'


class CustomKafkaProducer:
    def __init__(self, bootstrap_servers):
        self.producer_config = {
            'connection': {'bootstrap_servers': bootstrap_servers},
            'producer': {'value_serializer': lambda m: m.SerializeToString()}
        }
        self.producer = None

    def create_producer(self):
        try:
            self.producer = KafkaProducer(**self.producer_config['connection'], **self.producer_config['producer'])
            logging.info("Kafka producer created successfully.")
        except KafkaError as e:
            logging.error("Error creating Kafka producer: %s", e)

    def send_event(self, topic, event):
        if self.producer is None:
            logging.error("Kafka producer not initialized.")
            return

        try:
            # Send the message to the specified Kafka topic
            future = self.producer.send(topic, event)
            record_metadata = future.get(timeout=10)
            logging.info("Event sent: %s", event)
            logging.info("Topic: %s, partition: %s, offset: %s", record_metadata.topic, record_metadata.partition, record_metadata.offset)
        except KafkaError as e:
            logging.error("Error sending event: %s", e)

    def close_producer(self):
        if self.producer is not None:
            self.producer.flush()
            self.producer.close()
            logging.info("Kafka producer closed.")
        else:
            logging.error("Kafka producer not initialized.")


def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def generate_event(event_id: int = random.randint(0, 100), event_name: str = None):
    if not event_name:
        event_name = fake.name()
    event = InputMessage()
    event.id = event_id
    event.name = event_name
    return event


if __name__ == "__main__":
    # Set up logging
    setup_logging()
    # pprint(clients_info)
    # Replace with your Kafka broker addresses and desired API version
    bootstrap_servers = os.getenv("BOOTSTRAP_SERVER", 'localhost:9092')
    # Create an instance of CustomKafkaProducer
    kafka_producer = CustomKafkaProducer(bootstrap_servers)

    # Initialize the Kafka producer
    kafka_producer.create_producer()
    try:
        for i in range(5):
            # Send the message to the Kafka topic
            generated_event = generate_event(event_id=i)
            kafka_producer.send_event(INPUT_EVENTS_TOPIC, generated_event)
            # Sleep for a while before sending the next message
            time.sleep(0.2)
    except KeyboardInterrupt:
        logging.info("Interrupted by user. Closing Kafka producer.")
    finally:
        # Close the Kafka producer
        kafka_producer.close_producer()

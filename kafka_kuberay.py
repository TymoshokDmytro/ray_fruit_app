import os
import random

import ray
from faker import Faker
from ray import serve
from starlette.requests import Request

fake = Faker()


@serve.deployment
class CustomKafkaProducer:
    def __init__(self, consumer_bind=None):
        from kafka import KafkaProducer

        self.producer_config = {
            'connection': {'bootstrap_servers': os.getenv("BOOTSTRAP_SERVER", "localhost:9093")},
            'producer': {'value_serializer': lambda m: m.SerializeToString()}
        }
        self.producer = KafkaProducer(**self.producer_config['connection'], **self.producer_config['producer'])
        self.consumer_bind = consumer_bind
        self.state = True

    async def __call__(self, request: Request):
        from kafka.errors import KafkaError
        if self.producer is None:
            print("Kafka producer not initialized.")
            return
        payload = await request.json()
        topic = payload['topic'] if "topic" in payload else os.getenv("INPUT_EVENTS_TOPIC")
        events_num = payload['events_num']
        try:
            for i in range(events_num):
                event = self.generate_event(event_id=i)
                # Send the message to the specified Kafka topic
                future = self.producer.send(topic, event)
                record_metadata = future.get(timeout=10)
                print("Event sent: %s", event)
                print("Topic: %s, partition: %s, offset: %s", record_metadata.topic, record_metadata.partition, record_metadata.offset)
            return f"{events_num} events generated"
        except KafkaError as e:
            print("Error sending event: %s", e)

    def generate_event(self, event_id: int = random.randint(0, 100), event_name: str = None):
        from protobuf_schema.input_message_pb2 import InputMessage
        if not event_name:
            event_name = fake.name()
        event = InputMessage()
        event.id = event_id
        event.name = event_name
        return event

    def close_producer(self):
        if self.producer is not None:
            self.producer.flush()
            self.producer.close()
            print("Kafka producer closed.")
        else:
            print("Kafka producer not initialized.")
        self.state = False

    def shutdown_event(self):
        self.producer.close()

    async def get_state(self):
        return self.state

    # Called by Serve to check the replica's health.
    async def check_health(self):
        if not self.state:
            # The specific type of exception is not important.
            raise RuntimeError("Kafka Producer is broken.")


@serve.deployment
class AsyncKafkaProducer:
    def __init__(self):
        from aiokafka import AIOKafkaProducer

        self.kafka_params = {
            'connection': {'bootstrap_servers': os.getenv("BOOTSTRAP_SERVER")},
            'producer': {'value_serializer': lambda m: m.SerializeToString()}
        }
        self.topic = os.getenv("OUTPUT_EVENTS_TOPIC")
        self.producer = AIOKafkaProducer(**self.kafka_params['connection'],
                                         **self.kafka_params['producer'])

        self.state = True

    async def produce_event(self, event_id, name):
        from protobuf_schema.output_message_pb2 import OutputMessage

        await self.producer.start()
        # create output event
        output_event = OutputMessage()
        output_event.id = event_id
        output_event.name = name

        try:
            msg = await self.producer.send_and_wait(self.topic, output_event)
            print(msg)
        except:
            await self.producer.stop()
            self.state = False

    async def shutdown_event(self):
        await self.producer.stop()

    async def get_state(self):
        return self.state

    # Called by Serve to check the replica's health.
    async def check_health(self):
        if not self.state:
            # The specific type of exception is not important.
            raise RuntimeError("Kafka Producer is broken.")


@serve.deployment
class AsyncKafkaConsumer:
    def __init__(self, producer):
        from faker import Faker
        from protobuf_schema.input_message_pb2 import InputMessage
        from aiokafka import AIOKafkaConsumer
        import asyncio

        self.fake = Faker()
        self.kafka_params = {
            'connection': {'bootstrap_servers': os.getenv("BOOTSTRAP_SERVER")},
            'consumer': {'group_id': 'ray',
                         'enable_auto_commit': True,
                         'auto_offset_reset': 'earliest',
                         'value_deserializer': InputMessage.FromString
                         }
        }
        self.topic = os.getenv("INPUT_EVENTS_TOPIC")
        self.consumer = AIOKafkaConsumer(self.topic,
                                         **self.kafka_params['connection'],
                                         **self.kafka_params['consumer'])

        self.producer = producer
        asyncio.create_task(self.consume_events())
        self.state = True

    async def consume_events(self, count=1):
        await self.consumer.start()
        self.state = True
        try:
            async for msg in self.consumer:
                print("consumed: ", msg.topic, msg.partition, msg.offset, "\n", msg.value, "\n", msg.timestamp)
                event = msg.value
                event_id = event.id
                event_name = event.name
                print(event_id, event_name)
                ray.get(await self.producer.produce_event.remote(event_id=event_id, name=event_name))
        finally:
            await self.consumer.stop()
            self.state = False

    async def shutdown_event(self):
        await self.consumer.stop()

    async def get_state(self):
        return self.state

    # Called by Serve to check the replica's health.
    async def check_health(self):
        if not self.state:
            # The specific type of exception is not important.
            raise RuntimeError("Kafka Consumer is broken.")


kafka_producer = AsyncKafkaProducer.bind()
kafka_consumer = AsyncKafkaConsumer.bind(kafka_producer)
test_kafka_producer = CustomKafkaProducer.bind(kafka_consumer)

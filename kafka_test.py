import ray
from ray import serve

ray.init(runtime_env={"pip": ["requirements.txt"]})
serve.start(http_options={"host": "0.0.0.0", "port": 8000})


@serve.deployment(num_replicas=1,
                  ray_actor_options={
                      "num_cpus": 0.2,
                      "num_gpus": 0,
                      "runtime_env": {
                          "env_vars": {
                              "OUTPUT_EVENTS_TOPIC": 'output_events',
                              "BOOTSTRAP_SERVER": "localhost:9093"
                          }
                      }
                  },
                  health_check_period_s=5,
                  health_check_timeout_s=1
                  )
class AsyncKafkaProducer:
    def __init__(self):
        from aiokafka import AIOKafkaProducer
        import os

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


@serve.deployment(num_replicas=1,
                  ray_actor_options={
                      "num_cpus": 0.2,
                      "num_gpus": 0,
                      "runtime_env": {
                          "env_vars": {
                              "INPUT_EVENTS_TOPIC": 'input_events',
                              "BOOTSTRAP_SERVER": "localhost:9093"
                          }
                      }
                  },
                  health_check_period_s=5,
                  health_check_timeout_s=1
                  )
class AsyncKafkaConsumer:
    def __init__(self, producer):
        from faker import Faker
        from protobuf_schema.input_message_pb2 import InputMessage
        from aiokafka import AIOKafkaConsumer
        import os
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

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
from google.protobuf.message import Message
from .vertica_datacontract_pb2 import Issue

class KafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str,
        schema_registry_url: str,
        client_id: str = "python-producer",
    ):
        self.producer = Producer(
            {
                "bootstrap.servers": bootstrap_servers,
                "client.id": client_id,
            }
        )

        self.schema_registry_client = SchemaRegistryClient(
            conf={"url": schema_registry_url}
        )
        self.serializers_cache = {}

    def _get_serializer(self, proto_message_type):
        if proto_message_type not in self.serializers_cache:
            self.serializers_cache[proto_message_type] = ProtobufSerializer(
                msg_type=proto_message_type,
                schema_registry_client=self.schema_registry_client,
            )
        return self.serializers_cache[proto_message_type]

    def send_to_kafka(self, proto_message: Message, topic: str, key=None):
        serializer = self._get_serializer(proto_message.__class__)

        value = serializer(
            message=proto_message,
            ctx=SerializationContext(topic=topic, field=MessageField.VALUE),
        )
        

        self.producer.produce(
            topic=topic,
            key=key,
            value=value,
        )

    def flush(self, timeout=5.0):
        self.producer.flush(timeout=timeout)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()


# Предположим, у нас есть сгенерированный protobuf класс
# from my_protobuf_pb2 import MyMessage

# Создаем продюсер

with KafkaProducer(
    bootstrap_servers="localhost:9092",
    schema_registry_url="http://localhost:8081",
    client_id="my-app-producer"
) as producer:
    
    # Создаем и отправляем сообщение
    message = Issue()
    message.row_id = 123
    message.id = "test_message_1"
    
    producer.send_to_kafka(
        proto_message=message,
        topic="vertica_datacontract",
        # key="key-123"  # опционально
    )
    # Можно отправлять несколько сообщений
    # for i in range(5):
    #     msg = Issue()
    #     msg.row_id = i
    #     msg.id = f"message_{i}"
        
    #     producer.send_to_kafka(
    #         proto_message=msg,
    #         topic="vertica_datacontract",
    #         # key=f"key-{i}"
    #     )
# producer = KafkaProducer(
#     bootstrap_servers="localhost:9092",
#     schema_registry_url="http://localhost:8081"
# )

# # Создаем protobuf сообщение
# message = Issue()
# message.row_id = 123
# message.id = "test message"
# # message.timestamp = 1700000000
# print(message)
# # Отправляем сообщение
# producer.send_to_kafka(
#     proto_message=message,
#     topic="my-topic",
#     key="message-key-123"  # опционально
# )

# Можно отправлять несколько сообщений
# for i in range(10):
#     msg = MyMessage()
#     msg.id = i
#     msg.name = f"message_{i}"
#     producer.send_to_kafka(msg, "my-topic", f"key_{i}")

# Финальная отправка всех сообщений
# producer.flush()

# uv run python -m src.tests.test_send_to_kafka
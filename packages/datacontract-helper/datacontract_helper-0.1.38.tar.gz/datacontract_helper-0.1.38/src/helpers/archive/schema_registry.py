import json
import logging

from datacontract.data_contract import DataContract
import click
import requests

from src.settings import SCHEMA_REGISTRY_HOST, SCHEMA_REGISTRY_PORT

# from src import commands


log = logging.getLogger(name="").getChild(suffix=__name__)


# # Получить список всех subjects
# curl -X GET http://localhost:8081/subjects
# nshokurov@MB-YLV2KQ4C ~
# % curl -X GET http://localhost:8081/subjects                                                    [2025-09-03 15:56:37]
# ["persons-topic-value","your_topic-value"]%    

# # Получить все версии схемы для subject
# curl -X GET http://localhost:8081/subjects/vertica_datacontract/versions

# # Получить конкретную версию схемы
# curl -X GET http://localhost:8081/subjects/vertica_datacontract/versions/1
# echo $(curl -X GET http://localhost:8081/subjects/vertica_datacontract/versions/1) 

class SchemaRegistry:

    def __init__(
        self,
    ):
        ...

    def publush(
        self,
        filename: str,
        subject_name: str = "vertica_datacontract",
    ):  

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()

        # Запрос на регистрацию схемы
        response: requests.Response = requests.post(
            url=f"{SCHEMA_REGISTRY_HOST}:{SCHEMA_REGISTRY_PORT}/subjects/{subject_name}/versions",
            headers={
            "Content-Type": "application/vnd.schemaregistry.v1+json"
        },
            json={
                "schemaType": "PROTOBUF",
                "schema": data_contract.export(export_format="protobuf")["protobuf"]
        }, timeout=200
        )
        click.echo(message=response.url)
        click.echo(message=response.status_code)

    def validate_custom(self, filename: str):
        

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()

        click.echo(message=f" hello is custom validate {filename}")


    def validate_schema_registry(
        self,
        subject_name: str,
        filename: str,
        version: str = "latest",
    ):

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()
        exported: dict = data_contract.export(export_format="protobuf")
        print(exported["protobuf"])


        response: requests.Response = requests.post(
            url=f"{SCHEMA_REGISTRY_HOST}:{SCHEMA_REGISTRY_PORT}/compatibility/subjects/{subject_name}/versions/{version}",
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            data=json.dumps(obj={"schema": exported["protobuf"], "schemaType": "PROTOBUF"}),
            timeout=20,
        )
        click.echo(message=response.text)





        # import vertica_datacontract_pb2

        # # uv run python -m src publish-schema-registry --fields '{"col1": 1}'
        # schema_registry_conf: dict = {
        #     "url": f"{SCHEMA_REGISTRY_HOST}:{SCHEMA_REGISTRY_PORT}"
        # }
        # schema_registry_client: SchemaRegistryClient = SchemaRegistryClient(
        #     conf=schema_registry_conf
        # )
        # print(vertica_datacontract_pb2.Issue)
        # protobuf_serializer: ProtobufSerializer = ProtobufSerializer(vertica_datacontract_pb2.Issue, schema_registry_client)
        # print(protobuf_serializer._schema)
        # print(protobuf_serializer._schema_id)
        
        # protobuf_schema = protobuf_serializer
        # print(protobuf_schema)
            
        # Регистрация схемы вручную
        #subject = 'your_topic-value'  # Обычно схема регистрируется на теме с суффиксом "-value"
        # schema_id = schema_registry_client.register_schema(subject, protobuf_schema)

        # producer_conf = {
        #     'bootstrap.servers': bootstrap_servers,
        #     'key.serializer': None,  # если ключ не нужен или сериализатор свой
        #     'value.serializer': protobuf_serializer
        # }

        # schema_str: str = f"""
        # {
        # "type": "record",
        # "name": "User",
        # "namespace": namespace,
        # "fields": fields
        # }
        # """

        # schema_id: int = schema_registry_client.register_schema(
        #     subject_name=subject_name, schema=AvroSchema(schema_str)
        # )
        # # protobuf_schema_id = client.register_schema("subject-proto", ProtobufSchema(proto_schema_str))
        # log.info(f"Schema published with ID: {schema_id}")


# # Публикация схемы
# curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
#   --data '{
#     "schema": "{\"type\":\"record\",\"name\":\"User\",\"namespace\":\"com.example.avro\",\"fields\":[{\"name\":\"id\",\"type\":\"int\"},{\"name\":\"name\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"},{\"name\":\"created_at\",\"type\":{\"type\":\"long\",\"logicalType\":\"timestamp-millis\"}}]}"
#   }' \
#   http://localhost:8081/subjects/users-value/versions

# # Ответ: {"id":1}


# # Получить список всех subjects
# curl -X GET http://localhost:8081/subjects
# nshokurov@MB-YLV2KQ4C ~
# % curl -X GET http://localhost:8081/subjects                                                    [2025-09-03 15:56:37]
# ["persons-topic-value","your_topic-value"]%    

# # Получить все версии схемы для subject
# curl -X GET http://localhost:8081/subjects/vertica_datacontract/versions

# # Получить конкретную версию схемы
# curl -X GET http://localhost:8081/subjects/vertica_datacontract/versions/1
# echo $(curl -X GET http://localhost:8081/subjects/vertica_datacontract/versions/1) 

# http://localhost:8081/subjects/your_topic-value/versions/1

# # Проверить совместимость новой схемы
# curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
#   --data '{
#     "schema": "{\"type\":\"record\",\"name\":\"User\",\"fields\":[{\"name\":\"id\",\"type\":\"int\"},{\"name\":\"name\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"},{\"name\":\"age\",\"type\":[\"null\",\"int\"],\"default\":null}]}"
#   }' \
#   http://localhost:8081/compatibility/subjects/users-value/versions/latest

import importlib
import inspect
import logging
import os
# from pathlib import Path
import pathlib
import shutil
import subprocess
import sys
import tempfile
import types
# import vertica_datacontract_pb2__created
import zipfile
import io

from datacontract.data_contract import DataContract

import click
import requests
from confluent_kafka import Consumer, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
from google.protobuf.message import Message
from grpc_tools import protoc
# from person_pb2 import Person
from requests.auth import HTTPBasicAuth

from src.settings import (BOOTSTRAP_PORT, BOOTSTRAP_SERVER, KAFKA_TOPIC,
                          SCHEMA_REGISTRY_HOST, SCHEMA_REGISTRY_PORT)

log = logging.getLogger(name="").getChild(suffix=__name__)


def send_to_kafka(
    proto_message,
    bootstrap_servers: str = f"{BOOTSTRAP_SERVER}:{BOOTSTRAP_PORT}",
    topic: str = KAFKA_TOPIC,
    key=None,
):

    protobuf_serializer: ProtobufSerializer = ProtobufSerializer(
        msg_type=proto_message.__class__,
        schema_registry_client=SchemaRegistryClient(
            conf={"url": f"{SCHEMA_REGISTRY_HOST}:{SCHEMA_REGISTRY_PORT}"}
        ),
    )

    producer: Producer = Producer(
        {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "python-producer",
        }
    )

    value = protobuf_serializer(
        message=proto_message,
        ctx=SerializationContext(topic=topic, field=MessageField.VALUE),
    )

    producer.produce(
        topic=topic,
        # key=key,
        value=value,
    )
    producer.flush()


SEND_TO_KAFKA_TXT: str = """
def send_to_kafka(
    proto_message,
    bootstrap_servers: str,
    topic: str,
    key=None,
):

    protobuf_serializer: ProtobufSerializer = ProtobufSerializer(
        msg_type=proto_message.__class__,
        schema_registry_client=SchemaRegistryClient(
            conf={"url": f"{SCHEMA_REGISTRY_HOST}:{SCHEMA_REGISTRY_PORT}"}
        ),
    )

    producer: Producer = Producer(
        {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "python-producer",
        }
    )

    value = protobuf_serializer(
        message=proto_message,
        ctx=SerializationContext(topic=topic, field=MessageField.VALUE),
    )

    producer.produce(
        topic=topic,
        # key=key,
        value=value,
    )
    producer.flush()

"""


class ModuleBuilder:

    def __init__(self): ...


    def create_wheel(
        self,
        proto_file_name: str = "vertica_datacontract_pb2",
        module_folder: str = "vertica_datacontract",
        version: str = "0.1.8",
    ):

        # VERSION: str = "0.1.8"

        # MODULE_NAME: str = "vertica-datacontract-tool"
        # MODULE_NAME: str = "vertica_datacontract_tool"

        # у нас должен быть файл proto.py:
        # PROTO_FILE_NAME: str = "vertica_datacontract_pb2"

        # MODULE_FOLDER: str = "vertica_datacontract"

        # pyproject_toml_content: str = """
        # [build-system]
        # requires = ["setuptools", "wheel"]
        # build-backend = "setuptools.build_meta"
        # """

        setup_file_content: str = f"""
from setuptools import setup, find_packages

setup(
    name="{module_folder}",
    version="{version}",# my_package.__version__,
    # author=my_package.__author__,
    packages=find_packages(),
    install_requires=[
        "protobuf>=3.20.0",
        "build>=1.3.0",
        "confluent-kafka[all]>=2.11.1",
        "pip>=25.2",
        ],

)
"""

        with tempfile.TemporaryDirectory() as tmpdirname:
            setup_file: str = os.path.join(tmpdirname, "setup.py")

            with open(setup_file, "w") as f:
                f.write(setup_file_content)

            module_folder_path: str = os.path.join(tmpdirname, module_folder)
            os.makedirs(module_folder_path)  # , exist_ok=True)

            init_file: str = os.path.join(module_folder_path, "__init__.py")

            with open(f"{proto_file_name}.py", "r") as proto1:
                with open(init_file, "w") as f:
                    f.write(proto1.read())
                    f.write("\n\n")
                    f.write(SEND_TO_KAFKA_TXT)

            with open(init_file, "r") as f:
                print("its __init__.py")
                print(f.read())
            with open(setup_file, "r") as f:
                print("its setup.py")
                print(f.read())

            subprocess.run(
                args=["python", "setup.py", "bdist_wheel"],
                check=True,
                cwd=tmpdirname,  # указать working directory
            )

            dist_folder: str = os.path.join(tmpdirname, "dist")
            wheels: list[str] = [
                os.path.join(dist_folder, filepath)
                for filepath in os.listdir(dist_folder)
            ]
            print({"wheels": wheels})

            for wheel in wheels:
                subprocess.run(
                    args=["python", "-m", "pip", "install", wheel],
                    check=True,
                    cwd=tmpdirname,  # указать working directory
                )

            real_dir = os.getcwd()
            for wheel in wheels:
                print(f"try copy2 {wheel}")
                shutil.copy2(src=wheel, dst=real_dir)

    def publish_package(
        self,
        file_path: str = "",
        nexus_url: str = "",
        nexus_repo_path: str = "",
        username: str = "",
        password: str = "",
    ):
        with open(file=file_path, mode="rb") as file:

            response: requests.Response = requests.put(
                url=f"{nexus_url}/repository/{nexus_repo_path}/{os.path.basename(p=file_path)}",
                auth=HTTPBasicAuth(username=username, password=password),
                data=file,
                headers={"Content-Type": "application/json"},
                timeout=20,
            )
            response.raise_for_status()
            click.echo(message=f"The file has been successfully uploaded to Nexus: {response.url}")

    def validate_custom(self, filename: str):

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()

        click.echo(message=f" hello is custom validate {filename}.yaml")

    def create_yaml_from_sql(self, filename: str = "test"):
        # TODO: может можно как-то питоновским кодом сделать, без subprocess

        create_yaml: str = (
            f"""uv run datacontract import --format sql --source {filename}.sql --output {filename}.yaml"""
        )
        click.echo(message=create_yaml)

        result: subprocess.CompletedProcess = subprocess.run(
            args=create_yaml,
            shell=True,
            executable="/bin/bash",  # или '/bin/zsh'
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo(message=result)

    def create_proto_from_yaml(self, filename: str = "vertica_datacontract"):
        """нужен файлик your-datacontract.yaml"""

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()

        file_to_create: str = f"{filename}.proto"

        with open(file=file_to_create, mode="wb") as f:
            f.write(data_contract.export(export_format="protobuf")["protobuf"].encode())
        
        click.echo(message=f"created file: {file_to_create}")


    def generate_python_code_from_proto(self, filename: str):
        # TODO: мне кажется здесь надо принимать не название .proto файла, а сам файл в качестве аргумента

        protoc.main(["protoc", "--python_out=.", f"{filename}.proto"])
        click.echo(message=f"created file {filename}_pb2.py")

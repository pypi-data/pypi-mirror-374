import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from datacontract.data_contract import DataContract

import click
import requests

from src.settings import SCHEMA_REGISTRY_HOST, SCHEMA_REGISTRY_PORT

# from src import commands


log = logging.getLogger(name="").getChild(suffix=__name__)


class ContractValidator:
    def __init__(self): ...


    def validate_custom(self, filename: str):
        

        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()

        click.echo(message=f" hello is custom validate {filename}")


        
    def validate_schema_registry(
        self,
        subject_name: str,
        version: str,
        filename: str,
    ):

        url: str = (
            f"{SCHEMA_REGISTRY_HOST}:{SCHEMA_REGISTRY_PORT}/compatibility/subjects/{subject_name}/versions/{version}"
        )

        # proto_file_name: str = "person.proto"
        data_contract: DataContract = DataContract(
            data_contract_file=f"{filename}.yaml"
        )
        data_contract.lint()
        exported: dict = data_contract.export(export_format="protobuf")
        print(exported["protobuf"])
        # # Сохранение результата в файл
        # with open(file=f"{filename}.proto", mode="wb") as f:
        #     f.write(exported["protobuf"].encode())


        schema_content = exported["protobuf"]
        # with open(file=f"{proto_file}.proto", mode="r") as f:
        #     schema_content: str = f.read()
        # print({"schema_content": schema_content})

        url: str = (
            f"{SCHEMA_REGISTRY_HOST}:{SCHEMA_REGISTRY_PORT}/compatibility/subjects/{subject_name}/versions/{version}"
        )
        click.echo(message={"url": url})
        response: requests.Response = requests.post(
            url=url,
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            data=json.dumps(obj={"schema": schema_content, "schemaType": "PROTOBUF"}),
            timeout=20,
        )
        click.echo(message=response.text)

import logging
import sys
from pathlib import Path

import click

from src.helpers import ModuleBuilder
from src.settings import (BOOTSTRAP_PORT, BOOTSTRAP_SERVER, KAFKA_TOPIC,
                          SCHEMA_REGISTRY_HOST, SCHEMA_REGISTRY_PORT)


# Добавляем текущую директорию в путь импорта
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(object=current_dir))


log: logging.Logger = logging.getLogger(name=__name__)
log.setLevel(level=logging.DEBUG)


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


@click.group()
@click.pass_context
def cli(
    ctx,
):
    ctx.ensure_object(dict)
    print("is cli")


@cli.command()
@click.option("--filename")
@click.option("--subject-name")
def publish_schema_registry(
    filename: str,
    subject_name: str,
):
    """
    uv run --env-file .env python -m src publish-schema-registry --filename "vertica_datacontract" --subject-name vertica_datacontract

    """
    ModuleBuilder().publish_schema_registry(
        filename=filename, subject_name=subject_name
    )


@cli.command()
@click.option("--filename", default="vertica_datacontract")
@click.option(
    "--subject-name",
    default="vertica_datacontract",
)
@click.option("--version", default="latest")
def validate_schema_registry(
    filename: str = "vertica_datacontract",
    subject_name: str = "vertica_datacontract",
    version: str = "latest",
):
    """
    vertica_datacontract.proto

    uv run --env-file .env python -m src validate-schema-registry --filename "vertica_datacontract" --subject-name vertica_datacontract
    """
    ModuleBuilder().validate_custom(filename=filename)

    ModuleBuilder().validate_schema_registry(
        subject_name=subject_name, version=version, filename=filename
    )


@cli.command()
@click.option("--filename", required=False, type=str, help="Название файла")
def validate_custom(filename: str):
    """
    uv run --env-file .env python -m src validate-custom --filename vertica_datacontract

    """
    ModuleBuilder().validate_custom(filename=filename)


@cli.command()
@click.option("--filename", required=True, type=str, help="Название файла")
def create_yaml_from_sql(filename: str):
    """
    нужен ddl.sql

    uv run --env-file .env python -m src create-yaml-from-sql --filename vertica_datacontract
    """
    ModuleBuilder().create_yaml_from_sql(filename=filename)


# не уверен, что эта команда нужна
@cli.command()
@click.option("--filename", required=True, type=str, help="Название файла")
def create_proto_from_yaml(filename: str):
    """
    нужен your-datacontract.yaml

    uv run --env-file .env python -m src create-proto-from-yaml --filename vertica_datacontract

    """
    ModuleBuilder().create_proto_from_yaml(filename=filename)


@cli.command()
@click.option("--filename", required=True, type=str, help="Название файла")
def generate_python_code_from_proto(filename: str):
    """
    uv run --env-file .env python -m src generate-python-code-from-proto --filename vertica_datacontract
    """
    ModuleBuilder().generate_python_code_from_proto(filename=filename)


@cli.command()
@click.option("--wheel-version", required=True)
@click.option("--proto-file-name", default="vertica_datacontract_pb2")
@click.option("--module-folder", default="vertica_datacontract")
def create_wheel(
    wheel_version: str,
    proto_file_name: str = "vertica_datacontract_pb2",
    module_folder: str = "vertica_datacontract",
):
    """
    uv run --env-file .env python -m src create-wheel --proto-file-name vertica_datacontract_pb2 --wheel-version 0.1.9 --module-folder vertica_datacontract
    """
    ModuleBuilder().create_wheel(
        proto_file_name=proto_file_name,
        module_folder=module_folder,
        version=wheel_version,
    )


@cli.command()
@click.option("--module-name", required=False, type=str)
@click.option("--filepath", required=False, type=str)
@click.option("--nexusurl", required=False, type=str)
@click.option("--nexusrepopath", required=False, type=str)
@click.option("--username", required=False, type=str)
@click.option("--password", required=False, type=str)
def publish_package(
    filepath: str, nexusurl: str, nexusrepopath: str, username: str, password: str
):
    """
    не работает, вручную в нексус залил
    https://nexus.k8s-analytics.ostrovok.in/#browse/browse:datacontract_pypi:datacontract-helper%2F0.1.32%2Fdatacontract_helper-0.1.32-py3-none-any.whl
    но как в коде залить не понимаю

    """
    ModuleBuilder().publish_package(
        file_path=filepath,
        nexus_url=nexusurl,
        nexus_repo_path=nexusrepopath,
        username=username,
        password=password,
    )

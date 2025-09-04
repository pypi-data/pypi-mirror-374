# datacontract_helper

howto:


todo:
https://github.com/datacontract/datacontract-cli/blob/main/datacontract/data_contract.py

```
data_contract.lint()
data_contract.test()

# Проверка breaking changes между двумя версиями
breaking_changes = data_contract1.breaking(data_contract2)

# Полный changelog с разными уровнями серьезности
changes = data_contract1.changelog(data_contract2, include_severities=[Severity.ERROR, Severity.WARNING])

try:
    data_contract = DataContract(data_contract_file="contract.yaml")
    # Уже при создании объекта происходит базовая валидация
except DataContractException as e:
    print(f"Validation failed: {e}")

```

build and publish:

```

manualy increase version in pyproject.toml and remove old version

 1308  uv run python3 -m pip install --upgrade setuptools wheel

 1309  uv run python3 -m build --no-isolation

 1311  uv run twine upload --config-file ./.pypirc dist/*
 
 ```
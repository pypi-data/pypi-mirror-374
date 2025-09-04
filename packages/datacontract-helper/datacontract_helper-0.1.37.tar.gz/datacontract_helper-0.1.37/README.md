# datacontract_helper

howto:

build and publish:

```

manualy increase version in pyproject.toml and remove old version

 1308  uv run python3 -m pip install --upgrade setuptools wheel

 1309  uv run python3 -m build --no-isolation

 1311  uv run twine upload --config-file ./.pypirc dist/*
 
 ```
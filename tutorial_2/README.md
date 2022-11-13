# Deep history app

## Development setup

Create a virtual environment and install the dependencies:

```
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install -r ./requirements.txt --upgrade
pip install autopep8
```

If using VSCode, restart it or follow these steps:
 - `Ctrl + Shift + P`
 - _Select Interpreter_
 - Choose `./.venv/bin/python`.

## Start using gunicorn

```
export MAINNET_GATEWAY=http://r620:8080
export DEVNET_GATEWAY=http://r620:9090
gunicorn --workers=2 --bind=0.0.0.0:30000 "deep_history.app:app" --capture-output --access-logfile '-' --error-logfile '-'
```

## Run using Docker

Build Docker image:

```
docker image build . -t deep-history-dashboard:latest -f ./deep-history-dashboard.dockerfile
```

Start project:

```
DOCKER_USER=$(id -u):$(id -g) docker compose --file ./deep-history-dashboard-compose.yml --project-name deep-history-dashboard up --detach
```

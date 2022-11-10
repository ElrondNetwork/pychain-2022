# pychain-2022

Introduction to MultiversX blockchain development with Python.

## Deep history


### Prepare venv

```
rm -rf ~/pychain-deep-history
python3 -m venv ~/pychain-deep-history
source ~/pychain-deep-history/bin/activate
export PYTHONPATH=""
pip install pip -U
pip install -r ./deep_history/requirements.txt --upgrade
```

### Start using gunicorn

```
export MAINNET_GATEWAY=http://r620:8080
export DEVNET_GATEWAY=http://r620:9090
gunicorn --workers=2 --bind=0.0.0.0:30000 "deep_history.app:app" --capture-output --access-logfile '-' --error-logfile '-'
```

### Run using Docker

Build Docker image:

```
docker image build . -t deep-history-dashboard:latest -f ./deep-history-dashboard.dockerfile
```

Start project:

```
DOCKER_USER=$(id -u):$(id -g) docker compose --file ./deep-history-dashboard-compose.yml --project-name deep-history-dashboard up --detach
```

# Simple personal passwords manager on the blockchain

## Prerequisites

For clipboard interaction:

```
sudo apt install xclip
```

## How to run

Add entries:

```
python3 ./passwords_manager/main.py add --secret=./passwords_manager/testdata/secret.hex --wallet=./passwords_manager/testdata/wallet.pem --url=https://devnet-gateway.elrond.com
```

Reveal entries:

```
python3 ./passwords_manager/main.py get --secret=./passwords_manager/testdata/secret.hex --address=erd1kvudr40e0mp46cv59mj5dawezwce6pffg25xtkflm6xgagpax43snt52rr --url=https://devnet-gateway.elrond.com
```

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

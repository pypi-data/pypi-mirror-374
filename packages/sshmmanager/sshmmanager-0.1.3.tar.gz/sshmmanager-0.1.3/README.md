# sshm

A Python CLI tool for managing SSH hosts and connections, backed by a SQLite database.

## Features
- Add, list, update, and remove SSH hosts
- Store connection details
- Simple command-line interface

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the CLI tool:

```bash
python -m sshm.cli [COMMAND] [OPTIONS]
```


## Usage

You can use `sshm` to quickly connect to SSH hosts, store connection arguments, and select from previously used hosts.

### Basic Usage

Run the CLI tool:

```bash
python -m sshm.cli [HOST] [SSH_ARGS]
# or if installed as a script:
sshm [HOST] [SSH_ARGS]
```

#### No Arguments
If you run `sshm` with no arguments, you will be presented with a list of previously used hosts to select and connect to interactively.

#### Fuzzy Host Search
If you provide a partial host name, sshm will use fuzzy search to suggest matching hosts. If one match is found, it connects directly. If multiple matches are found, you can select from the list.

```bash
sshm myhost
```

#### New Connection
If you provide a full SSH argument (e.g. `user@host`), sshm will store this connection and connect immediately. Any additional SSH arguments are passed through.

```bash
sshm alice@192.168.1.10 -p 2222 -i ~/.ssh/id_ed25519
```

## How It Works

- Connections are stored in a local SQLite database (`data.sqlite3`).
- When connecting, the tool either matches an existing host or adds a new one.
- You can select from previous connections interactively if no arguments are given.

## Example Workflows

1. **Connect to a known host:**
    ```bash
    sshm myserver
    ```
    (Fuzzy matches and connects to `myserver`)

2. **Add and connect to a new host:**
    ```bash
    sshm alice@192.168.1.10 -p 2222
    ```
    (Stores and connects to this host)

3. **Interactive selection:**
    ```bash
    sshm
    ```
    (Lists all stored hosts for selection)

## Project Structure
```
sshm/
    cli.py      # CLI entry point
    data.py     # Database operations
    utils.py    # Utility functions
    __init__.py # Package init
```
# State Server

A small FastAPI application that tells you which U.S. state (if any) a given latitude/longitude point falls in, based on a simplified `states.json`. The app was bundled using Poetry and can be run via a CLI script (`state-server`) or directly with Uvicorn.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Installation](#installation)

   * [macOS](#macos)
   * [Linux](#linux)
4. [Running the Server](#running-the-server)

   * [Via `state-server` CLI](#via-state-server-cli)
   * [Via Uvicorn](#via-uvicorn)
5. [Usage / Testing](#usage--testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

* **Python 3.10+** (tested on 3.10 and 3.11)
* **Poetry** (for dependency management)
* A POSIX-compatible shell (bash, zsh, etc.)
* `curl` (for testing via command line)

> If you don't have Python 3.10+ installed, use your system package manager or [pyenv](https://github.com/pyenv/pyenv).
> If you don’t have Poetry installed yet, follow the instructions below.

---

## Project Structure

```
state-server/
├── pyproject.toml
├── poetry.lock
├── README.md          ← (you are here)
├── states.json        ← simplified state polygons
├── main.py            ← FastAPI app entrypoint
└── src/
    └── state_server/
        ├── __init__.py
        ├── app.py       ← FastAPI router + polygon logic
        └── utils.py     ← helper functions (e.g., point-in-polygon)
```

* `states.json`
  Contains an array of objects, each with:

  ```jsonc
  {
    "state": "Pennsylvania",
    "border": [
      [-80.519891, 42.26907],
      [-80.080179, 41.978802],
      ...
    ]
  }
  ```
* `main.py`
  Boots the FastAPI instance and (optionally) defines a CLI entrypoint script called `state-server`.

---

## Installation

### macOS

1. **Install Homebrew (if not already installed):**

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3.10+ via Homebrew (if needed):**

   ```bash
   brew install python@3.10
   ```

3. **Install Poetry** (if you don’t already have it):

   ```bash
   brew install poetry
   ```

4. **Clone this repository** (or download & extract):

   ```bash
   git clone https://github.com/yourusername/state-server.git
   cd state-server
   ```

5. **Install dependencies with Poetry**:

   ```bash
   poetry install
   ```

   This will create a virtual environment and install FastAPI, Uvicorn, and any other dependencies listed in `pyproject.toml`.

6. **Activate the virtual environment** (optional, but convenient if you want to run `python`/`pip` directly):

   ```bash
   poetry shell
   ```

   If you prefer not to spawn a shell, you can prefix commands with `poetry run`.

### Linux

1. **Install Python 3.10+** (Debian/Ubuntu example):

   ```bash
   sudo apt update
   sudo apt install -y python3.10 python3.10-venv python3.10-dev build-essential
   ```
2. **Install Curl** (if not already installed):

   ```bash
   sudo apt install -y curl
   ```
3. **Install Poetry**:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Then ensure `~/.local/bin` is in your `PATH`. For example, add this to `~/.bashrc` or `~/.zshrc`:

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

   After that, run:

   ```bash
   source ~/.bashrc
   ```
4. **Clone this repository** (or download & extract):

   ```bash
   git clone https://github.com/decimalst/state-server.git
   cd state-server
   ```
5. **Install dependencies with Poetry**:

   ```bash
   poetry install
   ```
6. **Activate the venv** (optional):

   ```bash
   eval $(poetry env activate)
   ```

---

## Running the Server

You can run the app in three ways: Docker(preferred), via the provided `state-server` CLI (entrypoint), or directly with Uvicorn. By default, the server listens on port **8080**.

### Docker

To containerize:

1. Build the image:

   ```bash
   docker build -t state-server:latest .
   ```
2. Run a container:

   ```bash
   docker run -d --name state-server -p 8080:8080 state-server:latest
   ```
3. Test (from host machine):

   ```bash
   curl -d "longitude=-77.036133&latitude=40.513799" http://localhost:8080/
   ```



### Via `state-server` CLI

After `poetry install`, you should have a `state-server` script available (as defined under `[tool.poetry.scripts]` in `pyproject.toml`). To start it:

```bash
# If you activated poetry shell:
state-server

# If not in a poetry shell:
poetry run state-server
```

This will launch Uvicorn under the hood and bind to `0.0.0.0:8080`. You will see output similar to:

```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using watchgod
INFO:     Started server process [YYYY]
```

> **Tip:** To run in the background (& monitor logs), you can do:
>
> ```bash
> nohup poetry run state-server &> state-server.log &
> ```

### Via Uvicorn

If you prefer to invoke Uvicorn directly, point it at the FastAPI app inside `main.py`. For example:

```bash
# need to have run `eval $(poetry env activate)`
uvicorn state_server.app:app --host 0.0.0.0 --port 8080 --reload

# Otherwise:
poetry run uvicorn state_server.app:app --host 0.0.0.0 --port 8080 --reload
```

* `--reload` is optional but useful during development (auto-restarts on file changes).

---

## Usage / Testing

Once the server is running on `http://localhost:8080`, you can test with `curl` (or any HTTP client):

```bash
curl -X POST \
     -d "longitude=-77.036133&latitude=40.513799" \
     http://localhost:8080/
```

You should get a JSON array of matching state names, for example:

```json
["Pennsylvania"]
```

* If the point does not lie in any simplified polygon, you’ll receive an empty array:

  ```json
  []
  ```

---

## Troubleshooting

* **ModuleNotFoundError: No module named 'fastapi'**
  Be sure you ran `poetry install` in the project root. If you’re not in a Poetry shell, prefix with `poetry run`.

* **Port 8080 Already in Use**
  Another service may be bound to 8080. Change the port:

  ```bash
  uvicorn state_server.app:app --host 0.0.0.0 --port 9090
  ```

  Or edit the `state-server` script to use a different port.

* **`state-server: command not found`**

  * Ensure you ran `poetry install`.
  * Check that the virtual environment is activated (`poetry shell`).
  * Verify `[tool.poetry.scripts]` in `pyproject.toml` includes:

    ```toml
    [tool.poetry.scripts]
    state-server = "state_server.app:app" # or "state_server.__main__:main"
    ```


---

## Acknowledgments

* Thanks to the Vistar team for providing the original `states.json` file and challenge description.
* Built with [FastAPI](https://fastapi.tiangolo.com/) and [Poetry](https://python-poetry.org/).

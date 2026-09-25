# FirebaseAppUtilities Python

Reusable Python library and local tooling for Firebase-backed applications.

It provides:

- Firebase project connection and configuration;
- Firestore inspection;
- Firestore-backed custom analytics;
- HTTP Functions access;
- CLI tooling;
- a reusable and extensible Tk GUI.

The CLI and GUI are thin layers over the same Python library.

## Environment

The Python package uses the repository-level:

```text id="uj1g0x"
FirebaseAppUtilities/
├── .env
├── .env-example
├── .venv/
└── python/
```

Create the local environment file from the repository root:

```bash id="kwm93f"
cp .env-example .env
```

Example:

```env id="j2z9t1"
PYTHON_BIN=/opt/homebrew/bin/python3
VENV_DIR=.venv
FIREBASE_ENVIRONMENT=development
```

## Install

Recommended from the repository root:

```bash id="m0qzcb"
make setup
```

Setup validates:

- the configured Python executable;
- Python version;
- Tkinter availability required by the GUI.

If Tkinter is missing, setup stops and shows the matching installation hint.

After validation, setup creates the shared `.venv` and installs the package in editable mode.

You can validate the Python environment separately with:

```bash id="418oty"
make check-python
```

You can also install only the Python package:

```bash id="qjt7xf"
make python-install
```

Or from `python/`:

```bash id="ai8ph9"
make install
```

## Configuration

Project-specific Firebase configuration is stored in TOML.

Example:

```toml id="mfu3y5"
[project]
project_id = "your-project-id"
environment = "development"
credentials = "/absolute/path/to/service-account.json"

[analytics]
collection = "analytics_events"

[functions]
base_url = "https://us-central1-your-project.cloudfunctions.net"
```

`credentials` and `base_url` are optional.

If `credentials` is omitted, Firebase Admin can use Application Default Credentials.

## CLI

Show help:

```bash id="r7q44t"
firebase-app-utils --help
```

Or from the repository root:

```bash id="t0ifuf"
make python-cli
```

Examples:

```bash id="y65fgr"
firebase-app-utils status \
    --config ./firebase.local.toml

firebase-app-utils collections \
    --config ./firebase.local.toml

firebase-app-utils documents users \
    --limit 20 \
    --config ./firebase.local.toml

firebase-app-utils analytics \
    --event song_generated \
    --limit 50 \
    --config ./firebase.local.toml

firebase-app-utils function myFunction \
    --method POST \
    --json '{"hello":"world"}' \
    --config ./firebase.local.toml

firebase-app-utils gui \
    --config ./firebase.local.toml
```

## GUI

The GUI is part of FirebaseAppUtilities and is designed to be reused by project-specific repositories.

Open the generic GUI from the repository root:

```bash id="viwky5"
make python-gui
```

A consuming project can launch it with minimal code:

```python id="ab406t"
from firebase_app_utilities import FirebaseProject
from firebase_app_utilities.gui import FirebaseUtilitiesApp

project = FirebaseProject.from_toml(
    "firebase.local.toml"
)

FirebaseUtilitiesApp(
    project=project
).run()
```

Projects can extend the GUI with project-specific screens or actions while keeping generic Firebase functionality inside FirebaseAppUtilities.

## Library usage

```python id="hbzayf"
from firebase_app_utilities import FirebaseProject

project = FirebaseProject.from_toml(
    "firebase.local.toml"
)

print(
    project.firestore.list_collections()
)

print(
    project.analytics.list_events(
        limit=20
    )
)
```

## Project-specific tooling

Projects such as `ChordGenFirebase` should depend on this package instead of copying its implementation.

Example:

```text id="fnn4pa"
ChordGenFirebase/
├── config/
├── dashboards/
├── functions/
├── scripts/
├── app.py
└── pyproject.toml
```

The intended separation is:

```text id="fjs07m"
FirebaseAppUtilities
    reusable Python API
    Firebase services
    CLI
    reusable GUI

ChordGenFirebase
    project configuration
    functions
    dashboards
    project-specific extensions
```

## Make commands

From `python/`:

```bash id="d0u8hh"
make help
make venv
make install
make uninstall
make cli
make gui
make build
make clean
```

These commands use the shared:

```text id="egvcrv"
../.env
../.venv
```
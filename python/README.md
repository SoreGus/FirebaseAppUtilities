# FirebaseAppUtilities Python

Reusable Python library and local tooling for Firebase-backed applications.

## Features

- connect with Application Default Credentials or a service-account JSON file;
- load project configuration from TOML;
- inspect Firestore collections and documents;
- query Firestore-backed custom analytics events;
- call HTTP Firebase/Google Cloud Functions endpoints;
- expose the same operations through a CLI;
- expose a lightweight local Tk GUI.

The CLI and GUI are deliberately thin layers over the Python library. Project-specific tooling can import the same library directly.

## Repository environment

The Python package uses the repository-level environment configuration.

Expected structure:

```text
FirebaseAppUtilities/
├── .env
├── .env-example
├── .venv/
└── python/
```

The `.env` file defines the Python interpreter used to create the shared virtual environment.

Example:

```env
PYTHON_BIN=/opt/homebrew/bin/python3
VENV_DIR=.venv
FIREBASE_ENVIRONMENT=development

# Optional
# FIREBASE_PROJECT_ID=your-firebase-project-id
# FIREBASE_CREDENTIALS=/absolute/path/to/service-account.json
```

Create the local environment file from the repository root:

```bash
cp .env-example .env
```

The `.env` file is local and must not be committed.

## Install

The recommended installation flow is from the repository root:

```bash
make setup
```

This creates the shared virtual environment at:

```text
FirebaseAppUtilities/.venv
```

and installs the Python package in editable mode.

You can also install only the Python package:

```bash
make python-install
```

Or work directly from the Python directory:

```bash
cd python
make install
```

The `python/Makefile` uses the same `.env` and `.venv` from the repository root.

## Virtual environment

The virtual environment is shared by the repository:

```text
../.venv
```

When inside the `python/` directory, activate it with:

```bash
source ../.venv/bin/activate
```

When working from the repository root:

```bash
source .venv/bin/activate
```

Activation is optional when using the provided Makefiles because they call the virtual environment executables directly.

## Configuration

Firebase project-specific configuration can be stored in a local TOML file.

Example:

```toml
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

If `credentials` is omitted, Firebase Admin uses Google Application Default Credentials.

Sensitive or machine-specific configuration should remain local and should not be committed.

Examples include:

```text
firebase.local.toml
firebase_app_utilities.local.toml
```

## CLI

After installation, the CLI is available through:

```bash
firebase-app-utils
```

Show help:

```bash
firebase-app-utils --help
```

Or through the Python Makefile:

```bash
cd python
make cli
```

Examples:

```bash
firebase-app-utils status --config ../examples/firebase_app_utilities.example.toml

firebase-app-utils collections \
    --config ./firebase.local.toml

firebase-app-utils documents users \
    --limit 20 \
    --config ./firebase.local.toml

firebase-app-utils analytics \
    --limit 50 \
    --config ./firebase.local.toml

firebase-app-utils analytics \
    --event song_generated \
    --config ./firebase.local.toml

firebase-app-utils function myFunction \
    --method POST \
    --json '{"hello":"world"}' \
    --config ./firebase.local.toml

firebase-app-utils gui \
    --config ./firebase.local.toml
```

## GUI

Open the GUI from the repository root:

```bash
make python-gui
```

Or directly from the Python directory:

```bash
make gui
```

The GUI uses the same Python library as the CLI and can connect to project-specific Firebase configurations.

## Library usage

The package can be imported directly by other Python projects.

```python
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

This is the preferred integration model for project-specific tooling.

For example:

```text
ChordGenFirebase
        |
        | Python dependency
        v
firebase_app_utilities
        |
        v
Firebase / Firestore
```

## Project-specific tooling

Projects such as `ChordGenFirebase` should depend on this package instead of copying FirebaseAppUtilities code.

A project-specific repository may contain:

```text
ChordGenFirebase/
├── dashboards/
├── functions/
├── scripts/
├── config/
└── pyproject.toml
```

Reusable Firebase infrastructure belongs in `FirebaseAppUtilities`.

Application-specific Firebase logic belongs in repositories such as `ChordGenFirebase`.

## Make commands

From the `python/` directory:

```bash
make help
make venv
make install
make uninstall
make cli
make gui
make build
make clean
```

These commands use:

```text
../.env
../.venv
```

rather than creating a separate Python environment inside the `python/` directory.
# FirebaseAppUtilities

FirebaseAppUtilities is a reusable Firebase toolkit composed of:

- a **Python library**;
- a **CLI**;
- a reusable **local GUI**;
- a **Swift Package** for Apple apps;
- shared schemas for conventions such as Firestore-backed analytics.

The goal is to centralize reusable Firebase infrastructure so project-specific repositories only need configuration and domain-specific logic.

## Repository layout

```text id="h2t0w0"
FirebaseAppUtilities/
├── python/
├── swift/
├── schemas/
├── examples/
├── .env-example
├── .gitignore
├── LICENSE
├── Makefile
└── README.md
```

## Architecture

```text id="160sw3"
ChordGen
   |
   | Swift Package
   v
FirebaseAppUtilities
   |
   v
Firebase / Firestore
   ^
   |
   | Python library / CLI / GUI
   |
ChordGenFirebase
```

`ChordGen` uses the Swift Package.

`ChordGenFirebase` uses the Python package and can configure or extend the reusable GUI and tooling.

## Setup

Create the local environment file:

```bash id="3nkbl8"
cp .env-example .env
```

Example:

```env id="50ys9r"
PYTHON_BIN=/opt/homebrew/bin/python3
VENV_DIR=.venv
FIREBASE_ENVIRONMENT=development
```

Then run:

```bash id="6f4z1a"
make setup
```

Setup validates:

- the configured Python executable;
- Python version;
- Tkinter availability required by the local GUI.

If Tkinter is missing, setup stops with an installation hint for the matching Python version.

After validation, setup creates the shared `.venv` and installs the Python package in editable mode.

## Commands

From the repository root:

```bash id="8bnbt5"
make check-python
make setup
make python-install
make python-cli
make python-gui
make clean
```

The root `Makefile` and `python/Makefile` use the same:

```text id="0fegcb"
.env
.venv
```

Swift dependencies are managed by Xcode / Swift Package Manager.

## Python

The Python package provides:

- Firebase project connection;
- Firestore inspection;
- custom analytics queries;
- HTTP Functions access;
- CLI tooling;
- reusable GUI components.

Example:

```python id="f7p1sq"
from firebase_app_utilities import FirebaseProject
from firebase_app_utilities.gui import FirebaseUtilitiesApp

project = FirebaseProject.from_toml(
    "firebase.local.toml"
)

FirebaseUtilitiesApp(
    project=project
).run()
```

The GUI is part of FirebaseAppUtilities itself and can be reused or extended by project-specific repositories.

See [`python/README.md`](python/README.md).

## Project configuration

A project-specific TOML file may contain:

```toml id="y7np8g"
[project]
project_id = "your-project-id"
environment = "development"
credentials = "/absolute/path/to/service-account.json"

[analytics]
collection = "analytics_events"

[functions]
base_url = "https://us-central1-your-project.cloudfunctions.net"
```

If `credentials` is omitted, Firebase Admin can use Application Default Credentials.

Local configuration files and credentials should not be committed.

## Swift

The Swift Package lives in:

```text id="4yc5h7"
swift/
```

Add it locally through Xcode from:

```text id="bq79ft"
FirebaseAppUtilities/swift
```

Then:

```swift id="920orv"
import FirebaseAppUtilities
```

Xcode resolves and manages the Swift Package dependencies automatically.

The package provides reusable Firebase integration for Apple applications, including Firestore, custom analytics, Functions, Auth, Storage, Remote Config, and environment configuration.

See [`swift/README.md`](swift/README.md).

## Custom analytics

FirebaseAppUtilities can store custom analytics events directly in Firestore without depending on Firebase Analytics.

Default collection:

```text id="wa7no7"
analytics_events/{eventId}
```

Example:

```json id="x89wjc"
{
  "name": "song_generated",
  "timestamp": "server timestamp",
  "sessionId": "...",
  "userId": "...",
  "platform": "iOS",
  "appVersion": "1.0",
  "buildNumber": "42",
  "environment": "production",
  "properties": {
    "genre": "rock"
  }
}
```

Shared contracts live in:

```text id="wpa06s"
schemas/
```

## Project-specific repositories

Reusable infrastructure belongs in:

```text id="jf0bl0"
FirebaseAppUtilities
```

Project-specific backend tooling belongs in repositories such as:

```text id="80s06i"
ChordGenFirebase
```

Application code belongs in:

```text id="366l78"
ChordGen
```

The intended separation is:

```text id="6denwn"
FirebaseAppUtilities
    reusable Firebase infrastructure

ChordGenFirebase
    project configuration and backend tooling

ChordGen
    Apple application
```
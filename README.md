# FirebaseAppUtilities

FirebaseAppUtilities is a reusable Firebase toolkit composed of:

- a **Python library**;
- a **CLI**;
- a reusable **local GUI**;
- a **Swift Package** for Apple apps;
- shared schemas for conventions such as Firestore-backed analytics.

The goal is to centralize reusable Firebase infrastructure so project-specific repositories only need configuration and domain-specific logic.

## Repository layout

```text
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

```text
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

```bash
cp .env-example .env
```

Example:

```env
PYTHON_BIN=/opt/homebrew/bin/python3
VENV_DIR=.venv
FIREBASE_ENVIRONMENT=development
```

Then run:

```bash
make setup
```

This creates the shared `.venv` and installs the Python package in editable mode.

## Commands

From the repository root:

```bash
make setup
make python-install
make python-cli
make python-gui
make swift-resolve
make clean
```

The root `Makefile` and `python/Makefile` use the same:

```text
.env
.venv
```

## Python

The Python package provides:

- Firebase project connection;
- Firestore inspection;
- custom analytics queries;
- HTTP Functions access;
- CLI tooling;
- reusable GUI components.

Example:

```python
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

If `credentials` is omitted, Firebase Admin can use Application Default Credentials.

Local configuration files and credentials should not be committed.

## Swift

The Swift Package lives in:

```text
swift/
```

Add it locally from:

```text
FirebaseAppUtilities/swift
```

Then:

```swift
import FirebaseAppUtilities
```

The package provides reusable Firebase integration for Apple applications, including Firestore, custom analytics, Functions, Auth, Storage, Remote Config, and environment configuration.

See [`swift/README.md`](swift/README.md).

## Custom analytics

FirebaseAppUtilities can store custom analytics events directly in Firestore without depending on Firebase Analytics.

Default collection:

```text
analytics_events/{eventId}
```

Example:

```json
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

```text
schemas/
```

## Project-specific repositories

Reusable infrastructure belongs in:

```text
FirebaseAppUtilities
```

Project-specific backend tooling belongs in repositories such as:

```text
ChordGenFirebase
```

Application code belongs in:

```text
ChordGen
```

The intended separation is:

```text
FirebaseAppUtilities
    reusable Firebase infrastructure

ChordGenFirebase
    project configuration and backend tooling

ChordGen
    Apple application
```
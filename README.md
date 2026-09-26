# FirebaseAppUtilities

Reusable Firebase tooling for Python and Apple platforms.

It provides:

- a Python library;
- a CLI;
- a reusable desktop GUI built with PySide6;
- a Swift Package;
- shared schemas for custom Firestore-backed analytics.

## Structure

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

Useful commands:

```bash
make check-python
make python-install
make python-cli
make python-gui
make clean
```

## Python

The Python package provides:

- Firebase project connection;
- Firestore access and inspection;
- custom analytics queries and aggregation;
- HTTP Functions access;
- CLI tooling;
- a reusable PySide6 desktop GUI.

Example:

```python
from firebase_app_utilities import FirebaseProject
from firebase_app_utilities.gui import (
    AnalyticsDashboardConfig,
    AnalyticsMetric,
    FirebaseUtilitiesApp,
)

project = FirebaseProject.from_toml(
    "firebase.local.toml"
)

analytics = AnalyticsDashboardConfig(
    title="Application Analytics",
    metrics=(
        AnalyticsMetric.event(
            "App Opens",
            "app_opened",
        ),
    ),
)

FirebaseUtilitiesApp(
    project=project,
    analytics=analytics,
).run()
```

Project-specific repositories declare what should be displayed; `FirebaseAppUtilities` owns the reusable GUI and Firebase logic.

See [`python/README.md`](python/README.md).

## Configuration

Example TOML:

```toml
[project]
project_id = "your-project-id"
environment = "development"

# Optional.
# credentials = "secrets/firebase-adminsdk.json"

[analytics]
collection = "analytics_events"

[functions]
# base_url = "https://us-central1-your-project.cloudfunctions.net"
```

Relative credential paths are resolved from the TOML file directory.

Local configuration files and credentials should not be committed.

## Swift

The Swift Package is located in:

```text
swift/
```

Add it through Xcode using the local package path:

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

Custom analytics events can be stored directly in Firestore.

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

## Architecture

```text
FirebaseAppUtilities
    reusable Firebase infrastructure
    Python CLI and desktop GUI
    Swift Package
    shared schemas

ChordGenFirebase
    project configuration
    event definitions
    analytics dashboard configuration

ChordGen
    Apple application
```
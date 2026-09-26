# FirebaseAppUtilities Python

Reusable Firebase tooling and a modern PySide6 desktop workspace for Firebase-backed applications.

## What it provides

- Firebase project configuration and Admin SDK connection;
- Firestore browsing and document inspection;
- Firestore-backed custom analytics;
- analytics metrics, rankings, activity history and recent events;
- HTTP Functions access;
- CLI tooling;
- a reusable PySide6 desktop interface;
- declarative analytics configuration for consuming projects.

The Firebase services are independent from the GUI. Projects such as `ChordGenFirebase` only declare what they want to show; FirebaseAppUtilities owns the rendering, navigation and interaction model.

## Install

From the repository root:

```bash
make setup
make python-install
```

Or from `python/`:

```bash
make install
```

The package uses the repository-level `.venv`.

## Dependencies

The desktop GUI uses PySide6. Tkinter is no longer used.

```toml
PySide6>=6.8,<7
```

## Project configuration

```toml
[project]
project_id = "your-project-id"
environment = "development"

# Relative paths are resolved from the TOML directory.
# credentials = "secrets/firebase-adminsdk.json"

[analytics]
collection = "analytics_events"

[functions]
# base_url = "https://us-central1-your-project-id.cloudfunctions.net"
```

If credentials are omitted, Firebase Admin can use Application Default Credentials.

## Declarative analytics GUI

A consuming project can configure analytics without implementing UI code:

```python
from firebase_app_utilities import FirebaseProject
from firebase_app_utilities.gui import (
    AnalyticsDashboardConfig,
    AnalyticsMetric,
    FirebaseUtilitiesApp,
    PropertyRanking,
)

project = FirebaseProject.from_toml(
    "config/firebase.local.toml"
)

analytics = AnalyticsDashboardConfig(
    title="My App Analytics",
    metrics=(
        AnalyticsMetric.event(
            "App Opens",
            "app_opened",
        ),
        AnalyticsMetric.event(
            "Items Selected",
            "item_selected",
        ),
    ),
    rankings=(
        PropertyRanking(
            title="Top Items",
            event_name="item_selected",
            property_key="item",
        ),
    ),
)

FirebaseUtilitiesApp(
    project=project,
    title="My App Firebase",
    analytics=analytics,
).run()
```

## Desktop workspace

The GUI is analytics-first and uses a persistent left navigation rail:

- Dashboard — metrics, activity chart, rankings and recent events;
- Events — filtering, search and event inspector;
- Firestore — collection browser, document list and document inspector;
- Functions — HTTP function invocation when configured;
- Project — connection and service configuration summary.

The main workspace does not expose the local TOML path or connection controls once the project is connected.

## CLI

```bash
firebase-app-utils --help
```

Examples:

```bash
firebase-app-utils status \
    --config ./firebase.local.toml

firebase-app-utils collections \
    --config ./firebase.local.toml

firebase-app-utils documents users \
    --limit 20 \
    --config ./firebase.local.toml

firebase-app-utils analytics \
    --event app_opened \
    --limit 50 \
    --config ./firebase.local.toml

firebase-app-utils gui \
    --config ./firebase.local.toml
```

## Make commands

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

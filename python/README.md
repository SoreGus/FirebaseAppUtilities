# FirebaseAppUtilities Python

Reusable Firebase tooling and a PySide6 desktop workspace for Firebase-backed applications.

## What it provides

- Firebase project configuration and Admin SDK connection;
- cost-aware Firestore custom analytics;
- Firestore `count()` aggregation for cheap server-side counts;
- persistent SQLite cache for immutable analytics/support records;
- incremental synchronization that requests only newer documents;
- declarative event definitions, filters and insights;
- generic append-only collection support;
- HTTP Functions access and CLI tooling;
- reusable PySide6 desktop UI.

The GUI never performs a Firestore read merely because the application opened or the user changed screens. Network reads happen only after an explicit action such as **Sync new**, **Server count**, or another project-defined query.

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

## Project configuration

```toml
[project]
project_id = "your-project-id"
environment = "development"
# credentials = "secrets/firebase-adminsdk.json"

[analytics]
collection = "analytics_events"

[functions]
# base_url = "https://us-central1-your-project-id.cloudfunctions.net"
```

If credentials are omitted, Firebase Admin can use Application Default Credentials.

## Declarative analytics GUI

```python
from firebase_app_utilities import FirebaseProject
from firebase_app_utilities.gui import (
    AnalyticsDashboardConfig,
    AnalyticsEventDefinition,
    AnalyticsInsight,
    AnalyticsProperty,
    FirebaseUtilitiesApp,
)

project = FirebaseProject.from_toml("config/firebase.local.toml")

analytics = AnalyticsDashboardConfig(
    title="My App Analytics",
    events=(
        AnalyticsEventDefinition(
            name="item_selected",
            title="Item Selected",
            properties=(
                AnalyticsProperty("item", "Item"),
                AnalyticsProperty("is_custom", "Custom", kind="bool"),
            ),
            insights=(
                AnalyticsInsight.top_values("Top Items", "item"),
                AnalyticsInsight.bool_distribution("Custom", "is_custom"),
            ),
        ),
    ),
)

FirebaseUtilitiesApp(
    project=project,
    title="My App Firebase",
    analytics=analytics,
).run()
```

## Local cache and sync

Cached Firestore documents are stored under:

```text
~/.firebase-app-utilities/<project>-<environment>.sqlite3
```

Analytics and append-only collections are treated as immutable records. Each explicit sync stores the newest timestamp and subsequent syncs request only newer records. Filters and insights over already-synchronized data are computed locally and cost zero Firestore reads.

## Desktop workspace

- **Dashboard** — cached counts and activity; explicit sync only;
- **Analytics** — event-type navigation, per-property filters, server `count()`, incremental sync, local insights and recent records;
- **Support** — optional append-only collection UI supplied by the consuming project;
- **Functions** — HTTP function invocation when configured;
- **Project** — project and cache information.

The generic raw Firestore browser is no longer part of the main navigation.

## CLI

```bash
firebase-app-utils --help
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

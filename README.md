# FirebaseAppUtilities

FirebaseAppUtilities is a Firebase application platform composed of:

- a reusable **Python library** for Firebase project inspection, administration, and local tooling;
- a **CLI** built on top of the Python library;
- a lightweight **local GUI** for connecting to and inspecting a Firebase project;
- a reusable **Swift Package** for Apple applications;
- shared schemas for conventions such as custom Firestore-backed analytics.

The repository is organized as a monorepo so backend/tooling projects and Apple applications can share the same Firebase conventions without sharing implementation code.

## Repository layout

```text
FirebaseAppUtilities/
├── python/                 Python package, CLI, and GUI
├── swift/                  Swift Package
├── schemas/                Shared data contracts
├── examples/               Example project configuration
├── .env-example            Local environment template
├── .gitignore
├── LICENSE
├── Makefile                Repository-level development commands
└── README.md
```

## Intended architecture

```text
ChordGen (iOS/macOS)
        |
        | Swift Package
        v
FirebaseAppUtilities
        |
        v
Firebase / Firestore
        ^
        |
        | Python library
ChordGenFirebase
```

The Swift package writes application data and custom analytics events.

The Python package can inspect the same Firebase project, query custom analytics, inspect Firestore, and provide project-specific tooling through the CLI, GUI, or direct library usage.

## Environment setup

FirebaseAppUtilities uses a repository-level `.env` file for local development configuration.

The repository contains:

```text
.env-example
```

Create your local environment file with:

```bash
cp .env-example .env
```

The `.env` file is ignored by Git.

Example:

```env
PYTHON_BIN=/opt/homebrew/bin/python3
VENV_DIR=.venv
FIREBASE_ENVIRONMENT=development

# Optional
# FIREBASE_PROJECT_ID=your-firebase-project-id
# FIREBASE_CREDENTIALS=/absolute/path/to/service-account.json
```

`PYTHON_BIN` is the Python interpreter used to create the shared virtual environment.

For example, on an Apple Silicon Mac using Homebrew:

```env
PYTHON_BIN=/opt/homebrew/bin/python3
```

You can verify the installed Python executable with:

```bash
python3 -c "import sys; print(sys.executable)"
```

## Python virtual environment

The repository uses a single shared virtual environment:

```text
FirebaseAppUtilities/.venv
```

The root `Makefile` and `python/Makefile` both use this environment.

The intended flow is:

```text
PYTHON_BIN
    |
    v
create .venv
    |
    v
.venv/bin/python
    |
    v
FirebaseAppUtilities Python tooling
```

## Initial setup

From the repository root:

```bash
make setup
```

This will:

1. create `.env` from `.env-example` if necessary;
2. create the shared `.venv`;
3. upgrade `pip`;
4. install the Python package in editable mode.

After that, the repository is ready for local development.

## Repository commands

Run:

```bash
make help
```

Available repository-level commands include:

```bash
make setup
make python-install
make python-gui
make swift-resolve
make clean
```

### Install the Python package

```bash
make python-install
```

### Open the local GUI

```bash
make python-gui
```

### Resolve Swift dependencies

```bash
make swift-resolve
```

### Remove local build artifacts

```bash
make clean
```

## Python

The Python implementation lives in:

```text
python/
```

It is designed as a reusable library first.

The CLI and GUI are interfaces built on top of the same library.

Typical architecture:

```text
firebase_app_utilities
        |
        +-- Python API
        |
        +-- CLI
        |
        +-- GUI
        |
        +-- project-specific tooling
```

You can work through the root `Makefile`:

```bash
make python-install
make python-gui
```

Or directly from the Python directory:

```bash
cd python

make install
make cli
make gui
make build
```

Both Makefiles use the same repository-level:

```text
.env
.venv
```

See [`python/README.md`](python/README.md).

## Swift

The Swift implementation lives in:

```text
swift/
```

It is distributed as a Swift Package named:

```text
FirebaseAppUtilities
```

The package provides reusable Firebase integration for Apple applications, including areas such as:

- Firebase configuration;
- environments;
- Firestore;
- custom analytics;
- Cloud Functions;
- authentication;
- storage;
- remote configuration.

While developing locally, add the package from:

```text
FirebaseAppUtilities/swift
```

A project such as `ChordGen` can then use:

```swift
import FirebaseAppUtilities
```

See [`swift/README.md`](swift/README.md).

## Custom analytics

FirebaseAppUtilities does not require Firebase Analytics for its custom event pipeline.

Application analytics events can instead be stored directly in Firestore using the shared contract defined in:

```text
schemas/analytics-event.schema.json
```

Typical document path:

```text
analytics_events/{eventId}
```

Typical event:

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

This allows the Swift package to record events while the Python tooling can inspect, aggregate, visualize, or export them.

Example flow:

```text
ChordGen
   |
   | track event
   v
FirebaseAppUtilities Swift
   |
   v
Firestore
   ^
   |
   | inspect / aggregate
   |
FirebaseAppUtilities Python
   |
   v
ChordGenFirebase
```

## Shared schemas

The `schemas/` directory contains contracts that can be consumed by both implementations.

The Swift and Python packages should share concepts and data structures, but not implementation code.

For example:

```text
schemas/
├── analytics-event.schema.json
├── project-config.schema.json
└── environment.schema.json
```

This keeps Firestore document formats and project conventions consistent across platforms.

## Credentials

Never commit Firebase service-account credentials or `GoogleService-Info.plist`.

Credential files are ignored by the repository `.gitignore`.

The Python package supports either:

1. Google Application Default Credentials; or
2. an explicit service-account JSON path.

The service-account path can be configured locally through `.env`:

```env
FIREBASE_CREDENTIALS=/absolute/path/to/service-account.json
```

or through project-specific configuration when appropriate.

The Swift application should provide its own Firebase configuration through the standard Firebase Apple application setup.

## Project-specific tooling

A project such as:

```text
ChordGenFirebase
```

should depend on the FirebaseAppUtilities Python package rather than copying its implementation.

For example:

```text
ChordGenFirebase/
├── config/
├── functions/
├── dashboards/
├── scripts/
└── pyproject.toml
```

`ChordGenFirebase` may contain project-specific:

- Firebase configuration;
- Cloud Functions;
- analytics dashboards;
- maintenance scripts;
- migrations;
- exports;
- administrative commands.

Reusable functionality belongs in:

```text
FirebaseAppUtilities
```

Project-specific functionality belongs in:

```text
ChordGenFirebase
```

Similarly, the application:

```text
ChordGen
```

should depend on the Swift package rather than implementing Firebase infrastructure repeatedly.

## Development model

The intended separation is:

```text
FirebaseAppUtilities
    reusable infrastructure

ChordGenFirebase
    Firebase project tooling and backend logic

ChordGen
    application
```

This allows FirebaseAppUtilities to evolve independently and later be reused by other applications and backend projects.
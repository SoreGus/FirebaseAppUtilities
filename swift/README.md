# FirebaseAppUtilities Swift

Swift Package for Apple applications that use Firebase through a small, reusable application layer.

## Goals

- centralize Firebase startup and environment selection;
- reduce repetitive Firestore code;
- provide Firestore-backed custom analytics;
- expose small wrappers for Auth, Functions, Storage, and Remote Config;
- keep application code dependent on FirebaseAppUtilities instead of scattering Firebase implementation details.

The package does not try to hide every Firebase API. Applications can still use the official Firebase SDK directly when needed.

## Add the package

During local development, add the `swift/` directory as a local Swift Package in Xcode.

Xcode resolves and manages Firebase package dependencies automatically.

When the repository is published, the package can be referenced as a normal remote Swift Package.

## Configure Firebase

Add the correct `GoogleService-Info.plist` to the application target.

Do not place credentials inside FirebaseAppUtilities or commit them to source control.

```swift
import FirebaseAppUtilities
import SwiftUI

@main
struct ChordGenApp: App {
    init() {
        FirebaseAppUtilities.configure(
            environment: .production
        )
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

If the app uses different Firebase configurations per environment, provide the corresponding options file explicitly:

```swift
try FirebaseAppUtilities.configure(
    environment: .staging,
    optionsFileURL: url
)
```

## Firestore

```swift
struct Song: Codable, Identifiable, Sendable {
    let id: String
    let title: String
}

let repository = FirestoreRepository<Song>(
    collection: "songs"
)

try await repository.set(
    song,
    id: song.id
)

let loaded = try await repository.get(
    id: song.id
)
```

## Custom analytics

```swift
enum ChordGenEvent: AnalyticsEvent {
    case appOpened
    case songGenerated(genre: String)

    var name: String {
        switch self {
        case .appOpened:
            "app_opened"

        case .songGenerated:
            "song_generated"
        }
    }

    var properties: AnalyticsProperties {
        switch self {
        case .appOpened:
            [:]

        case .songGenerated(let genre):
            [
                "genre": .string(genre)
            ]
        }
    }
}
```

Track an event:

```swift
try await FirebaseAppUtilities.analytics.track(
    ChordGenEvent.songGenerated(
        genre: "rock"
    )
)
```

Events are stored in `analytics_events` by default and can be inspected by the Python tooling.

## Other services

```swift
let user = FirebaseAppUtilities.auth.currentUser
```

```swift
let result = try await FirebaseAppUtilities.functions.call(
    "generateSong",
    data: payload
)
```

```swift
let data = try await FirebaseAppUtilities.storage.download(
    path: "exports/song.mid"
)
```

```swift
let enabled = try await FirebaseAppUtilities.remoteConfig.bool(
    "new_editor"
)
```

## Intended usage

Application code should depend primarily on:

```swift
import FirebaseAppUtilities
```

FirebaseAppUtilities handles the reusable Firebase integration layer, while project-specific models and business logic remain inside the application.
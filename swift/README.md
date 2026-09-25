# FirebaseAppUtilities Swift

Swift Package for Apple applications that use Firebase through a small, reusable application layer.

## Goals

- centralize Firebase startup and environment selection;
- reduce repetitive Firestore CRUD code;
- provide a custom Firestore-backed analytics pipeline;
- expose small wrappers for Auth, Functions, Storage and Remote Config;
- keep application code dependent on FirebaseAppUtilities rather than scattering Firebase implementation details everywhere.

The package does **not** try to hide every Firebase API. When an application needs advanced Firebase features it can still use the official SDK directly.

## Add the package

During local development, add the `swift/` directory as a local Swift Package in Xcode.

When the repository is published, it can be referenced as a normal remote Swift package.

## Configure Firebase

Add the correct `GoogleService-Info.plist` to the application target. Do not add it to this package or commit it to source control.

```swift
import FirebaseAppUtilities

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

If the app uses different Firebase plist files per environment, resolve the file URL in the app and pass it explicitly:

```swift
try FirebaseAppUtilities.configure(
    environment: .staging,
    optionsFileURL: url
)
```

## Firestore repository

```swift
struct Song: Codable, Identifiable, Sendable {
    let id: String
    let title: String
}

let repository = FirestoreRepository<Song>(collection: "songs")
try await repository.set(song, id: song.id)
let loaded = try await repository.get(id: song.id)
```

## Custom analytics

```swift
enum ChordGenEvent: AnalyticsEvent {
    case appOpened
    case songGenerated(genre: String)

    var name: String {
        switch self {
        case .appOpened: "app_opened"
        case .songGenerated: "song_generated"
        }
    }

    var properties: AnalyticsProperties {
        switch self {
        case .appOpened:
            [:]
        case .songGenerated(let genre):
            ["genre": .string(genre)]
        }
    }
}

try await FirebaseAppUtilities.analytics.track(
    ChordGenEvent.songGenerated(genre: "rock")
)
```

Events are written to `analytics_events` by default and can be inspected by the Python tooling.

## Other services

```swift
let user = FirebaseAppUtilities.auth.currentUser
let result = try await FirebaseAppUtilities.functions.call("generateSong", data: payload)
let data = try await FirebaseAppUtilities.storage.download(path: "exports/song.mid")
let enabled = try await FirebaseAppUtilities.remoteConfig.bool("new_editor")
```

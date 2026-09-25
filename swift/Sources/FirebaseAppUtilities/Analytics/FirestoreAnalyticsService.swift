import FirebaseFirestore
import Foundation

public actor FirestoreAnalyticsService {
    public var collectionName: String
    public var context: AnalyticsContext

    public init(
        collectionName: String = "analytics_events",
        context: AnalyticsContext = AnalyticsContext()
    ) {
        self.collectionName = collectionName
        self.context = context
    }

    public func setContext(_ context: AnalyticsContext) {
        self.context = context
    }

    public func track<Event: AnalyticsEvent>(_ event: Event) async throws {
        var data: [String: Any] = [
            "name": event.name,
            "timestamp": FieldValue.serverTimestamp(),
            "platform": Self.platform,
            "environment": FirebaseAppUtilities.environment.rawValue,
            "properties": event.properties.mapValues(\.firestoreValue)
        ]

        if let sessionID = context.sessionID {
            data["sessionId"] = sessionID
        }

        if let userID = context.userID {
            data["userId"] = userID
        }

        if let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String {
            data["appVersion"] = version
        }

        if let build = Bundle.main.infoDictionary?["CFBundleVersion"] as? String {
            data["buildNumber"] = build
        }

        try await Firestore.firestore()
            .collection(collectionName)
            .addDocument(data: data)
    }

    private static var platform: String {
        #if os(iOS)
        "iOS"
        #elseif os(macOS)
        "macOS"
        #else
        "Apple"
        #endif
    }
}

import FirebaseFirestore
import Foundation

public protocol FirestoreAnalyticsServiceProtocol: Sendable {
    func track(
        _ event: any AnalyticsEvent
    ) async throws
}

public actor FirestoreAnalyticsService:
    FirestoreAnalyticsServiceProtocol
{
    public nonisolated let collectionName: String

    private var context: AnalyticsContext
    private let userDefaults: UserDefaults
    private var sessionId: String?

    private static let userIdKey = "AnalyticsUserID"

    public init(
        collectionName: String = "analytics_events",
        context: AnalyticsContext = AnalyticsContext(),
        userDefaults: UserDefaults = .standard
    ) {
        self.collectionName = collectionName
        self.context = context
        self.userDefaults = userDefaults
    }

    public func track(
        _ event: any AnalyticsEvent
    ) async throws {
        setContext()

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

        if let version = Bundle.main.infoDictionary?[
            "CFBundleShortVersionString"
        ] as? String {
            data["appVersion"] = version
        }

        if let build = Bundle.main.infoDictionary?[
            "CFBundleVersion"
        ] as? String {
            data["buildNumber"] = build
        }

        try await Firestore.firestore()
            .collection(collectionName)
            .addDocument(data: data)
    }

    private func setContext() {
        if
            context.userID != nil,
            context.sessionID != nil
        {
            return
        }

        context = .init(
            userID: context.userID ?? currentUserId(),
            sessionID: context.sessionID ?? currentSessionId()
        )
    }

    private func currentUserId() -> String {
        if let userId = userDefaults.string(
            forKey: Self.userIdKey
        ) {
            return userId
        }

        let userId = UUID().uuidString

        userDefaults.set(
            userId,
            forKey: Self.userIdKey
        )

        return userId
    }

    private func currentSessionId() -> String {
        if let sessionId {
            return sessionId
        }

        let sessionId = UUID().uuidString
        self.sessionId = sessionId

        return sessionId
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

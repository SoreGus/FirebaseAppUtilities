import Foundation

public struct AnalyticsContext: Sendable {
    public var userID: String?
    public var sessionID: String?

    public init(userID: String? = nil, sessionID: String? = nil) {
        self.userID = userID
        self.sessionID = sessionID
    }
}

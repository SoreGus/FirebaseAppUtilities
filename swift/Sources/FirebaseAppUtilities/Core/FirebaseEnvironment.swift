import Foundation

public enum FirebaseEnvironment: String, Codable, CaseIterable, Sendable {
    case development
    case staging
    case production
}

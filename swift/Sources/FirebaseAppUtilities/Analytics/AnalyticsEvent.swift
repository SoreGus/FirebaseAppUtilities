import Foundation

public protocol AnalyticsEvent: Sendable {
    var name: String { get }
    var properties: AnalyticsProperties { get }
}

public extension AnalyticsEvent {
    var properties: AnalyticsProperties { [:] }
}

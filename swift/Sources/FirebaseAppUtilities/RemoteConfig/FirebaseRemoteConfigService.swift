import FirebaseRemoteConfig
import Foundation

public struct FirebaseRemoteConfigService: Sendable {
    public init() {}

    public func fetchAndActivate() async throws {
        _ = try await RemoteConfig.remoteConfig().fetchAndActivate()
    }

    public func string(_ key: String) -> String {
        RemoteConfig.remoteConfig()[key].stringValue
    }

    public func bool(_ key: String) -> Bool {
        RemoteConfig.remoteConfig()[key].boolValue
    }

    public func number(_ key: String) -> NSNumber {
        RemoteConfig.remoteConfig()[key].numberValue
    }
}

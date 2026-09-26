import Foundation

final class FirebaseUtilitiesState: @unchecked Sendable {
    private let lock = NSLock()

    private var storedEnvironment: FirebaseEnvironment = .production
    private var storedIsConfigured = false

    var environment: FirebaseEnvironment {
        lock.lock()
        defer { lock.unlock() }

        return storedEnvironment
    }

    var isConfigured: Bool {
        lock.lock()
        defer { lock.unlock() }

        return storedIsConfigured
    }

    func setEnvironment(
        _ environment: FirebaseEnvironment
    ) {
        lock.lock()
        storedEnvironment = environment
        lock.unlock()
    }

    func setConfigured() {
        lock.lock()
        storedIsConfigured = true
        lock.unlock()
    }
}
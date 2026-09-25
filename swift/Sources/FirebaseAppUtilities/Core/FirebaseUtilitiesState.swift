import Foundation

final class FirebaseUtilitiesState: @unchecked Sendable {
    private let lock = NSLock()
    private var storedEnvironment: FirebaseEnvironment = .production

    var environment: FirebaseEnvironment {
        lock.lock()
        defer { lock.unlock() }
        return storedEnvironment
    }

    func setEnvironment(_ environment: FirebaseEnvironment) {
        lock.lock()
        storedEnvironment = environment
        lock.unlock()
    }
}

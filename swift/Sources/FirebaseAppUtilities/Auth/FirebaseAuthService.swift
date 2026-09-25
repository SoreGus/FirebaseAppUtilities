import FirebaseAuth
import Foundation

public struct FirebaseAuthService: Sendable {
    public init() {}

    public var currentUser: User? {
        Auth.auth().currentUser
    }

    @discardableResult
    public func signInAnonymously() async throws -> User {
        let result = try await Auth.auth().signInAnonymously()
        return result.user
    }

    public func signOut() throws {
        try Auth.auth().signOut()
    }
}

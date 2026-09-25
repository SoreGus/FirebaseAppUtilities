import FirebaseFunctions
import Foundation

public struct FirebaseFunctionsService: Sendable {
    public init() {}

    public func call(
        _ name: String,
        data: Any? = nil
    ) async throws -> Any {
        let callable = Functions.functions().httpsCallable(name)
        let result = try await callable.call(data)
        return result.data
    }
}

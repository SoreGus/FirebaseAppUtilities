import FirebaseStorage
import Foundation

public struct FirebaseStorageService: Sendable {
    public init() {}

    public func upload(
        data: Data,
        path: String,
        contentType: String? = nil
    ) async throws {
        let metadata = StorageMetadata()
        metadata.contentType = contentType
        _ = try await Storage.storage().reference(withPath: path).putDataAsync(data, metadata: metadata)
    }

    public func download(
        path: String,
        maxSize: Int64 = 20 * 1024 * 1024
    ) async throws -> Data {
        try await Storage.storage().reference(withPath: path).data(maxSize: maxSize)
    }

    public func downloadURL(path: String) async throws -> URL {
        try await Storage.storage().reference(withPath: path).downloadURL()
    }

    public func delete(path: String) async throws {
        try await Storage.storage().reference(withPath: path).delete()
    }
}

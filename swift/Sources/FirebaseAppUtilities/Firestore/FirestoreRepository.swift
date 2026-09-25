import FirebaseFirestore
import Foundation

public struct FirestoreRepository<Model: Codable & Sendable>: Sendable {
    public let collection: String

    public init(collection: String) {
        self.collection = collection
    }

    private var reference: CollectionReference {
        Firestore.firestore().collection(collection)
    }

    public func set(_ model: Model, id: String, merge: Bool = true) async throws {
        let data = try FirestoreCodable.encode(model)
        try await reference.document(id).setData(data, merge: merge)
    }

    public func add(_ model: Model) async throws -> String {
        let data = try FirestoreCodable.encode(model)
        let document = reference.document()
        try await document.setData(data)
        return document.documentID
    }

    public func get(id: String) async throws -> Model? {
        let snapshot = try await reference.document(id).getDocument()
        guard snapshot.exists, let data = snapshot.data() else {
            return nil
        }
        return try FirestoreCodable.decode(Model.self, from: data)
    }

    public func delete(id: String) async throws {
        try await reference.document(id).delete()
    }

    public func list(limit: Int = 100) async throws -> [Model] {
        let snapshot = try await reference.limit(to: limit).getDocuments()
        return try snapshot.documents.map {
            try FirestoreCodable.decode(Model.self, from: $0.data())
        }
    }
}

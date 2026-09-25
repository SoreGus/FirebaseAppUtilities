import FirebaseFirestore
import Foundation

public struct FirebaseFirestoreService: Sendable {
    public init() {}

    public func collection(_ path: String) -> CollectionReference {
        Firestore.firestore().collection(path)
    }

    public func document(_ path: String) -> DocumentReference {
        Firestore.firestore().document(path)
    }
}

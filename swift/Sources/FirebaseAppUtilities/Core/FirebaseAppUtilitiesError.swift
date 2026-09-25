import Foundation

public enum FirebaseAppUtilitiesError: LocalizedError, Sendable {
    case invalidOptionsFile(URL)
    case invalidDocumentData
    case missingDownloadData

    public var errorDescription: String? {
        switch self {
        case .invalidOptionsFile(let url):
            "Could not create FirebaseOptions from \(url.path)."
        case .invalidDocumentData:
            "Firestore document data could not be converted to JSON-compatible data."
        case .missingDownloadData:
            "Firebase Storage returned no download data."
        }
    }
}

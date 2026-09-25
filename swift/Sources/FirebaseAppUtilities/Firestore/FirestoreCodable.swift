import Foundation

public enum FirestoreCodable {
    public static func encode<T: Encodable>(_ value: T) throws -> [String: Any] {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .millisecondsSince1970
        let data = try encoder.encode(value)
        let object = try JSONSerialization.jsonObject(with: data)
        guard let dictionary = object as? [String: Any] else {
            throw FirebaseAppUtilitiesError.invalidDocumentData
        }
        return dictionary
    }

    public static func decode<T: Decodable>(_ type: T.Type, from data: [String: Any]) throws -> T {
        let json = try JSONSerialization.data(withJSONObject: data)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .millisecondsSince1970
        return try decoder.decode(type, from: json)
    }
}

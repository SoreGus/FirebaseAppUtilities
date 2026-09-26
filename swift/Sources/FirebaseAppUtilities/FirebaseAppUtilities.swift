import FirebaseCore
import Foundation

public enum FirebaseAppUtilities {
    private static let state = FirebaseUtilitiesState()

    public static var environment: FirebaseEnvironment {
        state.environment
    }

    public static let auth = FirebaseAuthService()
    public static let firestore = FirebaseFirestoreService()
    public static let analytics = FirestoreAnalyticsService()
    public static let functions = FirebaseFunctionsService()
    public static let remoteConfig = FirebaseRemoteConfigService()
    public static let storage = FirebaseStorageService()

    public static func configure(
        environment: FirebaseEnvironment = .production,
        optionsFileURL: URL? = nil
    ) throws {
        guard !state.isConfigured else {
            return
        }

        state.setEnvironment(environment)

        if let optionsFileURL {
            guard let options = FirebaseOptions(
                contentsOfFile: optionsFileURL.path
            ) else {
                throw FirebaseAppUtilitiesError.invalidOptionsFile(
                    optionsFileURL
                )
            }

            FirebaseApp.configure(
                options: options
            )
        } else {
            FirebaseApp.configure()
        }

        state.setConfigured()
    }
}
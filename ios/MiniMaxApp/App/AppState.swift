import SwiftUI

@MainActor
final class AppState: ObservableObject {
    @Published var activeThreadId: String?
    @Published var baseURL: URL = URL(string: "https://app.minimax.villamarket.ai")!
    @Published var modelName: String = "minimax-m2.5"
    @Published var authToken: String?

    init() {
        // Support test auth token via launch environment
        if let token = ProcessInfo.processInfo.environment["MINIMAX_AUTH_TOKEN"], !token.isEmpty {
            self.authToken = token
        }
    }

    func createThread() async throws -> String {
        let client = DeerFlowClient(baseURL: baseURL, authToken: authToken)
        let thread = try await client.createThread()
        activeThreadId = thread.id
        return thread.id
    }
}

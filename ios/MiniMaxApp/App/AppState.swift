import SwiftUI

@MainActor
final class AppState: ObservableObject {
    @Published var activeThreadId: String?
    @Published var baseURL: URL = URL(string: "https://app.minimax.villamarket.ai")!
    @Published var modelName: String = "minimax-m2.5"

    func createThread() async throws -> String {
        let client = DeerFlowClient(baseURL: baseURL)
        let thread = try await client.createThread()
        activeThreadId = thread.id
        return thread.id
    }
}

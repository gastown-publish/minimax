import Foundation

/// High-level client that wraps LangGraphAPI with convenience methods.
/// Uses its own actor executor so streaming never blocks the main thread.
actor DeerFlowClient {
    private let api: LangGraphAPI
    private let authToken: String?

    init(baseURL: URL, authToken: String? = nil) {
        self.api = LangGraphAPI(baseURL: baseURL, authToken: authToken)
        self.authToken = authToken
    }

    func createThread() async throws -> ThreadResponse {
        try await api.createThread()
    }

    struct StreamResult {
        let content: String
        let reasoning: String
    }

    /// Streams a response from DeerFlow, calling onUpdate for each delta, and returns the final result.
    func streamMessage(
        threadId: String,
        message: String,
        modelName: String,
        onUpdate: @escaping @Sendable (String, String) -> Void
    ) async throws -> StreamResult {
        let stream = api.streamRun(threadId: threadId, message: message, modelName: modelName, authToken: authToken)

        var accContent = ""
        var accReasoning = ""

        for try await event in stream {
            switch event.event {
            case "messages-tuple", "messages/partial":
                if let data = event.data.data(using: .utf8),
                   let array = try? JSONSerialization.jsonObject(with: data) as? [Any],
                   array.count >= 2,
                   let payload = array[1] as? [String: Any] {
                    if let content = payload["content"] as? String {
                        accContent = content
                        onUpdate(accContent, accReasoning)
                    }
                    if let reasoning = payload["reasoning_content"] as? String {
                        accReasoning += reasoning
                        onUpdate(accContent, accReasoning)
                    }
                }

            case "events":
                if let data = event.data.data(using: .utf8),
                   let payload = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let eventName = payload["event"] as? String,
                   let toolName = payload["name"] as? String {
                    print("Tool event: \(eventName) - \(toolName)")
                }

            case "values":
                if let data = event.data.data(using: .utf8),
                   let payload = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let messages = payload["messages"] as? [[String: Any]],
                   let last = messages.last,
                   let type = last["type"] as? String, type == "ai",
                   let content = last["content"] as? String {
                    accContent = content
                    onUpdate(accContent, accReasoning)
                }

            case "end":
                break

            default:
                break
            }
        }

        return StreamResult(content: accContent, reasoning: accReasoning)
    }
}

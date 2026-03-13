import Foundation

/// High-level client that wraps LangGraphAPI with convenience methods.
@MainActor
final class DeerFlowClient: ObservableObject {
    private let api: LangGraphAPI

    init(baseURL: URL) {
        self.api = LangGraphAPI(baseURL: baseURL)
    }

    func createThread() async throws -> ThreadResponse {
        try await api.createThread()
    }

    /// Streams a response from DeerFlow and calls back with content deltas.
    func streamMessage(
        threadId: String,
        message: String,
        modelName: String,
        onDelta: @escaping (String) -> Void,
        onReasoning: @escaping (String) -> Void,
        onToolEvent: @escaping (String, String) -> Void
    ) async throws {
        let stream = api.streamRun(threadId: threadId, message: message, modelName: modelName)

        for try await event in stream {
            switch event.event {
            case "messages-tuple", "messages/partial":
                // Parse message tuple: [type, {content, ...}]
                if let data = event.data.data(using: .utf8),
                   let array = try? JSONSerialization.jsonObject(with: data) as? [Any],
                   array.count >= 2,
                   let payload = array[1] as? [String: Any] {
                    if let content = payload["content"] as? String {
                        onDelta(content)
                    }
                    if let reasoning = payload["reasoning_content"] as? String {
                        onReasoning(reasoning)
                    }
                }

            case "events":
                if let data = event.data.data(using: .utf8),
                   let payload = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let eventName = payload["event"] as? String,
                   let toolName = payload["name"] as? String {
                    onToolEvent(eventName, toolName)
                }

            case "values":
                // Full state update — extract latest assistant message
                if let data = event.data.data(using: .utf8),
                   let payload = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let messages = payload["messages"] as? [[String: Any]],
                   let last = messages.last,
                   let type = last["type"] as? String, type == "ai",
                   let content = last["content"] as? String {
                    onDelta(content)
                }

            case "end":
                break

            default:
                break
            }
        }
    }
}

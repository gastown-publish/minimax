import SwiftUI

struct ChatMessage: Identifiable {
    let id: String
    let role: MessageRole
    var content: String
    var reasoning: String
    var isStreaming: Bool

    init(id: String = UUID().uuidString, role: MessageRole, content: String, reasoning: String = "", isStreaming: Bool = false) {
        self.id = id
        self.role = role
        self.content = content
        self.reasoning = reasoning
        self.isStreaming = isStreaming
    }
}

@MainActor
final class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var inputText = ""
    @Published var isStreaming = false
    @Published var streamingContent = ""

    private var client: DeerFlowClient?
    private var threadId: String?
    private var modelName: String = "minimax-m2.5"
    private var streamTask: Task<Void, Never>?

    func configure(baseURL: URL, threadId: String, modelName: String) {
        self.client = DeerFlowClient(baseURL: baseURL)
        self.threadId = threadId
        self.modelName = modelName
    }

    func send(_ text: String) async {
        guard let client, let threadId else { return }

        let userMessage = ChatMessage(role: .human, content: text)
        messages.append(userMessage)

        let assistantId = UUID().uuidString
        let assistantMessage = ChatMessage(id: assistantId, role: .assistant, content: "", isStreaming: true)
        messages.append(assistantMessage)

        isStreaming = true
        streamingContent = ""

        streamTask = Task {
            do {
                var accContent = ""
                var accReasoning = ""

                try await client.streamMessage(
                    threadId: threadId,
                    message: text,
                    modelName: modelName,
                    onDelta: { content in
                        accContent = content
                        self.updateLastMessage(content: accContent, reasoning: accReasoning)
                    },
                    onReasoning: { reasoning in
                        accReasoning += reasoning
                        self.updateLastMessage(content: accContent, reasoning: accReasoning)
                    },
                    onToolEvent: { event, tool in
                        // Could show tool execution status in UI
                        print("Tool event: \(event) - \(tool)")
                    }
                )

                finalizeLastMessage(content: accContent, reasoning: accReasoning)
            } catch {
                if !Task.isCancelled {
                    finalizeLastMessage(content: "Error: \(error.localizedDescription)", reasoning: "")
                }
            }
        }
    }

    func cancelStream() {
        streamTask?.cancel()
        streamTask = nil
        isStreaming = false
        if var last = messages.last, last.role == .assistant {
            last.isStreaming = false
            messages[messages.count - 1] = last
        }
    }

    private func updateLastMessage(content: String, reasoning: String) {
        streamingContent = content
        guard !messages.isEmpty else { return }
        let idx = messages.count - 1
        messages[idx].content = content
        messages[idx].reasoning = reasoning
    }

    private func finalizeLastMessage(content: String, reasoning: String) {
        isStreaming = false
        streamTask = nil
        guard !messages.isEmpty else { return }
        let idx = messages.count - 1
        messages[idx].content = content
        messages[idx].reasoning = reasoning
        messages[idx].isStreaming = false
    }
}

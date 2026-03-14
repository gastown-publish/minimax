import SwiftUI

struct MessageBubble: View {
    let message: ChatMessage

    var body: some View {
        HStack(alignment: .top, spacing: 0) {
            if message.role == .human {
                Spacer(minLength: 60)
            }

            VStack(alignment: .leading, spacing: 8) {
                // Reasoning block (collapsed by default)
                if !message.reasoning.isEmpty {
                    ThinkingView(reasoning: message.reasoning)
                }

                // Content
                if !message.content.isEmpty {
                    Text(LocalizedStringKey(message.content))
                        .textSelection(.enabled)
                }

                if message.isStreaming && message.content.isEmpty && message.reasoning.isEmpty {
                    HStack(spacing: 6) {
                        Circle().fill(.secondary).frame(width: 6, height: 6)
                        Circle().fill(.secondary.opacity(0.7)).frame(width: 6, height: 6)
                        Circle().fill(.secondary.opacity(0.4)).frame(width: 6, height: 6)
                    }
                }
            }
            .padding(12)
            .background(backgroundColor)
            .foregroundStyle(foregroundColor)
            .clipShape(RoundedRectangle(cornerRadius: 16))

            if message.role == .assistant {
                Spacer(minLength: 60)
            }
        }
        .padding(.horizontal)
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("message_\(message.role.rawValue)")
    }

    private var backgroundColor: Color {
        switch message.role {
        case .human: return .blue
        case .assistant: return Color(.systemGray6)
        default: return Color(.systemGray5)
        }
    }

    private var foregroundColor: Color {
        message.role == .human ? .white : .primary
    }
}

import Foundation
import SwiftData

enum MessageRole: String, Codable {
    case human
    case assistant = "ai"
    case system
    case tool
}

@Model
final class MessageModel {
    @Attribute(.unique) var id: String
    var role: String
    var content: String
    var reasoning: String
    var createdAt: Date
    var thread: ThreadModel?

    init(id: String = UUID().uuidString, role: MessageRole, content: String, reasoning: String = "", createdAt: Date = .now) {
        self.id = id
        self.role = role.rawValue
        self.content = content
        self.reasoning = reasoning
        self.createdAt = createdAt
    }
}

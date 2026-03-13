import Foundation
import SwiftData

struct ThreadResponse: Codable {
    let id: String
    let createdAt: String?
    let metadata: [String: AnyCodable]?

    enum CodingKeys: String, CodingKey {
        case id = "thread_id"
        case createdAt = "created_at"
        case metadata
    }
}

@Model
final class ThreadModel {
    @Attribute(.unique) var id: String
    var title: String
    var lastMessage: String
    var updatedAt: Date
    @Relationship(deleteRule: .cascade) var messages: [MessageModel]

    init(id: String, title: String = "New Chat", lastMessage: String = "", updatedAt: Date = .now) {
        self.id = id
        self.title = title
        self.lastMessage = lastMessage
        self.updatedAt = updatedAt
        self.messages = []
    }
}

/// Type-erased Codable wrapper for arbitrary JSON values.
struct AnyCodable: Codable {
    let value: Any

    init(_ value: Any) {
        self.value = value
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let str = try? container.decode(String.self) { value = str }
        else if let int = try? container.decode(Int.self) { value = int }
        else if let double = try? container.decode(Double.self) { value = double }
        else if let bool = try? container.decode(Bool.self) { value = bool }
        else if let dict = try? container.decode([String: AnyCodable].self) { value = dict }
        else if let arr = try? container.decode([AnyCodable].self) { value = arr }
        else if container.decodeNil() { value = NSNull() }
        else { throw DecodingError.dataCorruptedError(in: container, debugDescription: "Unsupported type") }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch value {
        case let str as String: try container.encode(str)
        case let int as Int: try container.encode(int)
        case let double as Double: try container.encode(double)
        case let bool as Bool: try container.encode(bool)
        case let dict as [String: AnyCodable]: try container.encode(dict)
        case let arr as [AnyCodable]: try container.encode(arr)
        case is NSNull: try container.encodeNil()
        default: try container.encodeNil()
        }
    }
}

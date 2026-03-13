import Foundation

/// Represents a single SSE event from the LangGraph streaming API.
enum StreamEvent {
    case values(ValuesPayload)
    case messagesTuple(MessageTuplePayload)
    case events(EventPayload)
    case end

    struct ValuesPayload: Codable {
        let messages: [[String: AnyCodable]]?
    }

    struct MessageTuplePayload {
        let type: String
        let content: String
        let id: String?
    }

    struct EventPayload: Codable {
        let event: String
        let name: String?
        let data: [String: AnyCodable]?
    }
}

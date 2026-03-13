import Foundation

/// Parses a raw SSE byte stream into structured events.
/// Handles LangGraph's event format: `event: <type>\ndata: <json>\n\n`
struct SSEParser: AsyncSequence {
    typealias Element = SSEEvent

    let stream: URLSession.AsyncBytes

    struct SSEEvent {
        let event: String
        let data: String
    }

    struct AsyncIterator: AsyncIteratorProtocol {
        var byteIterator: URLSession.AsyncBytes.AsyncIterator
        var buffer = ""

        mutating func next() async throws -> SSEEvent? {
            while true {
                guard let line = try await nextLine() else {
                    // End of stream — flush any remaining event
                    return parseEvent(from: &buffer)
                }

                buffer += line + "\n"

                // SSE events are terminated by a blank line
                if line.isEmpty {
                    if let event = parseEvent(from: &buffer) {
                        return event
                    }
                }
            }
        }

        private mutating func nextLine() async throws -> String? {
            var line = ""
            while let byte = try await byteIterator.next() {
                let char = Character(UnicodeScalar(byte))
                if char == "\n" {
                    return line
                }
                line.append(char)
            }
            return line.isEmpty ? nil : line
        }

        private func parseEvent(from buffer: inout String) -> SSEEvent? {
            let raw = buffer
            buffer = ""

            var eventType = "message"
            var dataLines: [String] = []

            for line in raw.split(separator: "\n", omittingEmptySubsequences: false) {
                let s = String(line)
                if s.hasPrefix("event:") {
                    eventType = s.dropFirst(6).trimmingCharacters(in: .whitespaces)
                } else if s.hasPrefix("data:") {
                    dataLines.append(String(s.dropFirst(5)).trimmingCharacters(in: .whitespaces))
                }
            }

            guard !dataLines.isEmpty else { return nil }
            return SSEEvent(event: eventType, data: dataLines.joined(separator: "\n"))
        }
    }

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(byteIterator: stream.makeAsyncIterator())
    }
}

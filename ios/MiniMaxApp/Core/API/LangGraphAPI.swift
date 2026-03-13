import Foundation

/// Low-level API client for LangGraph thread/run endpoints.
actor LangGraphAPI {
    let baseURL: URL
    private let session: URLSession

    init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    // MARK: - Threads

    func createThread() async throws -> ThreadResponse {
        let url = baseURL.appendingPathComponent("/api/langgraph/threads")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(["metadata": [String: String]()])

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)
        return try JSONDecoder().decode(ThreadResponse.self, from: data)
    }

    // MARK: - Streaming Runs

    func streamRun(
        threadId: String,
        message: String,
        modelName: String
    ) -> AsyncThrowingStream<SSEParser.SSEEvent, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    let url = baseURL.appendingPathComponent("/api/langgraph/threads/\(threadId)/runs/stream")
                    var request = URLRequest(url: url)
                    request.httpMethod = "POST"
                    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                    request.timeoutInterval = 300

                    let body: [String: Any] = [
                        "assistant_id": "lead_agent",
                        "input": [
                            "messages": [
                                ["role": "human", "content": message]
                            ]
                        ],
                        "config": [
                            "configurable": [
                                "model_name": modelName
                            ]
                        ],
                        "stream_mode": ["values", "messages-tuple"],
                        "multitask_strategy": "enqueue"
                    ]
                    request.httpBody = try JSONSerialization.data(withJSONObject: body)

                    let (bytes, response) = try await session.bytes(for: request)
                    try validateResponse(response)

                    let parser = SSEParser(stream: bytes)
                    for try await event in parser {
                        continuation.yield(event)
                    }
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
        }
    }

    // MARK: - Thread State

    func getThreadState(threadId: String) async throws -> Data {
        let url = baseURL.appendingPathComponent("/api/langgraph/threads/\(threadId)/state")
        let (data, response) = try await session.data(from: url)
        try validateResponse(response)
        return data
    }

    // MARK: - Models

    func listModels() async throws -> [[String: AnyCodable]] {
        let url = baseURL.appendingPathComponent("/api/models")
        let (data, response) = try await session.data(from: url)
        try validateResponse(response)
        return try JSONDecoder().decode([[String: AnyCodable]].self, from: data)
    }

    // MARK: - Helpers

    private func validateResponse(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        guard (200...299).contains(http.statusCode) else {
            throw APIError.httpError(statusCode: http.statusCode)
        }
    }
}

enum APIError: LocalizedError {
    case invalidResponse
    case httpError(statusCode: Int)

    var errorDescription: String? {
        switch self {
        case .invalidResponse: return "Invalid response from server"
        case .httpError(let code): return "HTTP error \(code)"
        }
    }
}

import SwiftUI
import SwiftData

struct ThreadListView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = ThreadListViewModel()

    var body: some View {
        List(selection: $appState.activeThreadId) {
            ForEach(viewModel.threads) { thread in
                NavigationLink(value: thread.id) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(thread.title)
                            .font(.subheadline.bold())
                            .lineLimit(1)
                        if !thread.lastMessage.isEmpty {
                            Text(thread.lastMessage)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                        }
                        Text(thread.updatedAt, style: .relative)
                            .font(.caption2)
                            .foregroundStyle(.tertiary)
                    }
                    .padding(.vertical, 4)
                }
            }
            .onDelete { indices in
                viewModel.deleteThreads(at: indices)
            }
        }
        .listStyle(.sidebar)
        .navigationTitle("Conversations")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task { await createNewThread() }
                } label: {
                    Image(systemName: "plus")
                }
            }
        }
    }

    private func createNewThread() async {
        do {
            let threadId = try await appState.createThread()
            let thread = ThreadItem(id: threadId, title: "New Chat", lastMessage: "", updatedAt: .now)
            viewModel.threads.insert(thread, at: 0)
        } catch {
            print("Failed to create thread: \(error)")
        }
    }
}

struct ThreadItem: Identifiable {
    let id: String
    var title: String
    var lastMessage: String
    var updatedAt: Date
}

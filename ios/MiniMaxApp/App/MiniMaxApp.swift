import SwiftUI
import SwiftData

@main
struct MiniMaxApp: App {
    @StateObject private var appState = AppState()

    init() {
        // Disable animations during UI testing to prevent XCTest idle timeouts
        if ProcessInfo.processInfo.environment["DISABLE_ANIMATIONS"] == "1" {
            UIView.setAnimationsEnabled(false)
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .modelContainer(for: [ThreadModel.self, MessageModel.self])
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        NavigationSplitView {
            ThreadListView()
        } detail: {
            if let threadId = appState.activeThreadId {
                ChatView(threadId: threadId)
            } else {
                VStack(spacing: 16) {
                    Image(systemName: "bubble.left.and.text.bubble.right")
                        .font(.system(size: 48))
                        .foregroundStyle(.secondary)
                    Text("MiniMax-M2.5")
                        .font(.title2.bold())
                    Text("Select a conversation or start a new one")
                        .foregroundStyle(.secondary)
                }
            }
        }
        .tint(.blue)
    }
}

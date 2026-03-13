import SwiftUI

@MainActor
final class ThreadListViewModel: ObservableObject {
    @Published var threads: [ThreadItem] = []

    func deleteThreads(at offsets: IndexSet) {
        threads.remove(atOffsets: offsets)
    }
}

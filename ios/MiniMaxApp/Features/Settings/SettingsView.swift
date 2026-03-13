import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        Form {
            Section("Server") {
                LabeledContent("Base URL") {
                    Text(appState.baseURL.absoluteString)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Section("Model") {
                Picker("Model", selection: $appState.modelName) {
                    Text("minimax-m2.5").tag("minimax-m2.5")
                }
            }

            Section("About") {
                LabeledContent("Version", value: "1.0.0")
                LabeledContent("Backend", value: "DeerFlow + LangGraph")
                Link("API Documentation", destination: URL(string: "https://minimax.villamarket.ai/docs")!)
            }
        }
        .navigationTitle("Settings")
    }
}

// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MiniMaxApp",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "MiniMaxApp", targets: ["MiniMaxApp"]),
    ],
    targets: [
        .target(
            name: "MiniMaxApp",
            path: "MiniMaxApp"
        ),
    ]
)

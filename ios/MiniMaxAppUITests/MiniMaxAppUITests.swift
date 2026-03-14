import XCTest

final class MiniMaxAppUITests: XCTestCase {

    var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchEnvironment["MINIMAX_AUTH_TOKEN"] = "test-ui-automation"
        app.launchEnvironment["DISABLE_ANIMATIONS"] = "1"
        app.launch()
    }

    override func tearDownWithError() throws {
        app = nil
    }

    // MARK: - Test 1: App launches to Conversations screen

    func testAppLaunchShowsConversations() throws {
        let title = app.navigationBars["Conversations"]
        XCTAssertTrue(title.waitForExistence(timeout: 10), "Conversations title should appear")

        let plusButton = app.buttons["newChatButton"]
        XCTAssertTrue(plusButton.exists, "New chat button should exist")
    }

    // MARK: - Test 2: Create new thread and navigate to chat

    func testCreateNewThread() throws {
        let plusButton = app.buttons["newChatButton"]
        XCTAssertTrue(plusButton.waitForExistence(timeout: 10), "Plus button should appear")

        plusButton.tap()

        // Wait for the Chat view to appear (thread creation is async)
        let chatTitle = app.navigationBars["Chat"]
        XCTAssertTrue(chatTitle.waitForExistence(timeout: 15), "Chat view should appear after creating thread")

        // Message input should be visible
        let messageInput = app.textFields["messageInput"]
        XCTAssertTrue(messageInput.waitForExistence(timeout: 5), "Message input should exist")

        // Send button should exist (disabled initially)
        let sendButton = app.buttons["sendButton"]
        XCTAssertTrue(sendButton.exists, "Send button should exist")
    }

    // MARK: - Test 3: Full chat flow — send message and get response

    func testSendMessageAndReceiveResponse() throws {
        // Create new thread
        let plusButton = app.buttons["newChatButton"]
        XCTAssertTrue(plusButton.waitForExistence(timeout: 10))
        plusButton.tap()

        // Wait for Chat view
        let chatTitle = app.navigationBars["Chat"]
        XCTAssertTrue(chatTitle.waitForExistence(timeout: 15), "Chat view should appear")

        // Type a message
        let messageInput = app.textFields["messageInput"]
        XCTAssertTrue(messageInput.waitForExistence(timeout: 5))
        messageInput.tap()
        messageInput.typeText("Say hello in one word")

        // Tap send
        let sendButton = app.buttons["sendButton"]
        XCTAssertTrue(sendButton.waitForExistence(timeout: 5))
        sendButton.tap()

        // User message bubble should appear (MessageRole.human.rawValue == "human")
        let userBubble = app.otherElements["message_human"]
        XCTAssertTrue(userBubble.waitForExistence(timeout: 15), "User message bubble should appear")

        // Wait for assistant response (MessageRole.assistant.rawValue == "ai")
        let assistantBubble = app.otherElements["message_ai"]
        XCTAssertTrue(assistantBubble.waitForExistence(timeout: 120), "Assistant response should appear within 120s")

        // Wait for streaming to finish — the "Thinking..." indicator should disappear
        let streamingIndicator = app.otherElements["streamingIndicator"]
        let thinkingGone = NSPredicate(format: "exists == false")
        let expectation = XCTNSPredicateExpectation(predicate: thinkingGone, object: streamingIndicator)
        let result = XCTWaiter.wait(for: [expectation], timeout: 90)

        // Either streaming finished or was never shown (fast response)
        let streamingDone = result == .completed || !streamingIndicator.exists
        XCTAssertTrue(streamingDone, "Streaming should complete within 90 seconds")

        // Take a screenshot for proof
        let screenshot = app.screenshot()
        let attachment = XCTAttachment(screenshot: screenshot)
        attachment.name = "Chat Response"
        attachment.lifetime = .keepAlways
        add(attachment)

        print("UI TEST PASSED: Message sent and response received")
    }

    // MARK: - Test 4: Input validation — empty message cannot be sent

    func testEmptyMessageCannotBeSent() throws {
        let plusButton = app.buttons["newChatButton"]
        XCTAssertTrue(plusButton.waitForExistence(timeout: 10))
        plusButton.tap()

        let chatTitle = app.navigationBars["Chat"]
        XCTAssertTrue(chatTitle.waitForExistence(timeout: 15))

        // Send button should be disabled when input is empty
        let sendButton = app.buttons["sendButton"]
        XCTAssertTrue(sendButton.waitForExistence(timeout: 5))
        XCTAssertFalse(sendButton.isEnabled, "Send button should be disabled when input is empty")

        // Type something
        let messageInput = app.textFields["messageInput"]
        messageInput.tap()
        messageInput.typeText("test")

        // Now send should be enabled
        XCTAssertTrue(sendButton.isEnabled, "Send button should be enabled with text")

        // Take screenshot
        let screenshot = app.screenshot()
        let attachment = XCTAttachment(screenshot: screenshot)
        attachment.name = "Input Validation"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}

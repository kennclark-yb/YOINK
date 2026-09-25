import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from formatter import format_markdown, split_parts, split_parts_by_count

class ExtractionError(Exception):
    """User-facing extraction error."""

def detect_platform(url):
    if "chatgpt.com" in url or "chat.openai.com" in url:
        return "ChatGPT"

    if "claude.ai" in url:
        return "Claude"

    if "gemini.google.com" in url:
        return "Gemini"

    return None


def extract_chat(page):
    """Extract messages, omitting empty AI entries and known redaction placeholders."""
    return page.evaluate(
        """() => {
            const data =
                window.__reactRouterContext
                    .state
                    .loaderData["routes/share.$shareId.($action)"]
                    .serverResponse
                    .data;

            const results = [];

            for (const [id, item] of Object.entries(data.mapping)) {
                const message = item.message;

                if (!message) {
                    continue;
                }

                if (!message.author) {
                    continue;
                }

                const role = message.author.role;

                if (
                    role !== "assistant" &&
                    role !== "user"
                ) {
                    continue;
                }

                const content = message.content;

                if (!content || !Array.isArray(content.parts)) {
                    continue;
                }

                const textParts = content.parts.filter(
                    part => typeof part === "string"
                );

                if (textParts.length === 0) {
                    continue;
                }

                const text = textParts.join("\\n");
                // Match only whole-message placeholders. Never trim or
                // rewrite the retained message, or filter user messages.
                if (role === "assistant" && (
                    text.trim() === "" ||
                    text.trim() === "The output of this plugin was redacted."
                )) {
                    continue;
                }

                results.push({
                    id: id,
                    role: role,
                    text: text
                });
            }

            return results;
        }"""
    )

def filter_messages(messages, mode):
    """Filter extracted messages according to the selected mode."""
    if mode not in ("assistant", "user", "both"):
        raise ValueError(
            "Invalid mode. Use: assistant, user, or both."
        )

    if mode == "both":
        return messages

    return [
        message
        for message in messages
        if message["role"] == mode
    ]

def build_filtered_conversation(
    platform,
    title,
    url,
    all_messages,
    mode,
):
    filtered_messages = filter_messages(
        all_messages,
        mode,
    )

    if not filtered_messages:
        raise ExtractionError(
            "No messages found for the selected extraction mode."
        )

    return build_conversation(
        platform,
        title,
        url,
        filtered_messages,
    )

def build_conversation(platform, title, url, messages):
    if not isinstance(messages, list):
        raise TypeError("messages must be a list")

    for message in messages:
        if not isinstance(message, dict):
            raise TypeError("each message must be a dictionary")

        if "id" not in message:
            raise ValueError("message missing id")

        if "role" not in message:
            raise ValueError("message missing role")

        if "text" not in message:
            raise ValueError("message missing text")

    return {
        "platform": platform,
        "title": title,
        "url": url,
        "messages": messages,
    }

def load_share_page(browser, url):
    for attempt in range(3):
        page = browser.new_page()

        try:
            page.goto(
                url,
                wait_until="commit",
                timeout=10000,
            )

            page.wait_for_function(
                """() =>
                    window.__reactRouterContext &&
                    window.__reactRouterContext.state &&
                    window.__reactRouterContext.state.loaderData &&
                    window.__reactRouterContext.state.loaderData[
                        "routes/share.$shareId.($action)"
                    ] &&
                    window.__reactRouterContext.state.loaderData[
                        "routes/share.$shareId.($action)"
                    ].serverResponse &&
                    window.__reactRouterContext.state.loaderData[
                        "routes/share.$shareId.($action)"
                    ].serverResponse.data
                """,
                timeout=10000,
            )

            return page

        except Exception:
            page.close()

    raise ExtractionError(
        "ChatGPT page failed to load after 3 attempts."
    )

def extract_conversation(url, mode="assistant"):
    if mode not in ("assistant", "user", "both"):
        raise ValueError(
            "Invalid mode. Use: assistant, user, or both."
        )

    platform = detect_platform(url)

    if platform is None:
        raise ExtractionError("Unsupported platform.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        try:
            page = load_share_page(browser, url)

            title = page.title()

            all_messages = extract_chat(page)

            if not all_messages:
                raise ExtractionError("No messages found.")

            filtered_messages = filter_messages(
                all_messages,
                mode,
            )

            if not filtered_messages:
                raise ExtractionError(
                    "No messages found for the selected extraction mode."
                )

            full_conversation = build_conversation(
                platform,
                title,
                page.url,
                all_messages,
            )

            conversation = build_conversation(
                platform,
                title,
                page.url,
                filtered_messages,
            )

            return {
                "full_conversation": full_conversation,
                "conversation": conversation,
            }

        finally:
            browser.close()

def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python extract.py <share-url> [assistant|user|both]")
        return

    url = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) == 3 else "assistant"

    if mode not in ("assistant", "user", "both"):
        print("Invalid mode. Use: assistant, user, or both.")
        return

    platform = detect_platform(url)

    if platform is None:
        print("Unsupported platform.")
        return

    print(f"Platform: {platform}")
    print(f"Extraction mode: {mode}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = load_share_page(browser, url)

            title = page.title()

            print(f"Title: {title}")
            print(f"URL: {page.url}")

            messages = extract_chat(page, mode)

            if not messages:
                raise ExtractionError("No messages found.")

            conversation = build_conversation(
                platform,
                title,
                page.url,
                messages,
            )

            markdown = format_markdown(conversation)

            print(f"Markdown length: {len(markdown)} characters")
            print("Markdown formatting: OK")

            output = Path("extraction_test.md")

            with output.open("w", encoding="utf-8") as file:
                file.write(markdown)

            parts = split_parts(conversation)

            for index, part in enumerate(parts, start=1):
                output = Path(f"part_{index:02d}.md")

                with output.open("w", encoding="utf-8") as file:
                    file.write(part)

            print(f"Messages: {len(messages)}")
            print(f"Parts: {len(parts)}")

            browser.close()

            return conversation

    except (ExtractionError, ValueError, TypeError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

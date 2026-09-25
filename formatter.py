def format_markdown(conversation, start_index=1):
    parts = []

    for index, message in enumerate(
        conversation["messages"],
        start=start_index,
    ):
        role = "The AI" if message["role"] == "assistant" else "The User"

        parts.append(
            f"### [msg {index:03d}] {role}\n\n"
            f"{message['text']}"
        )

    return "\n\n---\n\n".join(parts)

def split_parts(conversation, max_chars=9000):
    messages = conversation["messages"]
    parts = []
    current_messages = []
    current_start = 1

    for message_index, message in enumerate(messages, start=1):
        test_messages = current_messages + [message]

        test_markdown = format_markdown(
            {
                **conversation,
                "messages": test_messages,
            },
            start_index=current_start,
        )

        if current_messages and len(test_markdown) > max_chars:
            parts.append(
                format_markdown(
                    {
                        **conversation,
                        "messages": current_messages,
                    },
                    start_index=current_start,
                )
            )

            current_start = message_index
            current_messages = [message]

        else:
            current_messages = test_messages

    if current_messages:
        parts.append(
            format_markdown(
                {
                    **conversation,
                    "messages": current_messages,
                },
                start_index=current_start,
            )
        )

    return parts

def split_parts_by_count(conversation, part_count):
    messages = conversation["messages"]

    if not isinstance(part_count, int) or part_count < 1:
        raise ValueError("part_count must be a positive integer")

    if part_count > len(messages):
        raise ValueError(
            "part_count cannot be greater than the number of messages"
        )

    parts = []
    current_start = 1
    message_index = 0

    total_chars = len(format_markdown(conversation))

    for part_index in range(part_count):
        remaining_parts = part_count - part_index
        remaining_messages = len(messages) - message_index

        target_chars = total_chars / remaining_parts

        current_messages = []
        current_chars = 0

        while message_index < len(messages):
            message = messages[message_index]

            test_messages = current_messages + [message]

            test_markdown = format_markdown(
                {
                    **conversation,
                    "messages": test_messages,
                },
                start_index=current_start,
            )

            test_chars = len(test_markdown)

            messages_after = len(messages) - (message_index + 1)
            parts_after = remaining_parts - 1

            if current_messages:
                if messages_after < parts_after:
                    break

                if abs(test_chars - target_chars) > abs(
                    current_chars - target_chars
                ):
                    break

            current_messages = test_messages
            current_chars = test_chars
            message_index += 1

        parts.append(
            format_markdown(
                {
                    **conversation,
                    "messages": current_messages,
                },
                start_index=current_start,
            )
        )

        current_start = message_index + 1

    return parts
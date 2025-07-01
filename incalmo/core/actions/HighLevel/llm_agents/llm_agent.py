import anthropic


class LLMAgent:
    def __init__(self, preprompt: str):
        # Initialize the conversation
        self.conversation = [
            {"role": "user", "content": preprompt},
        ]
        self.client = anthropic.Anthropic()

        self.max_message_len = 30000

    def send_message(self, message: str) -> str:
        # Trim message to fit within the max length
        if len(message) > self.max_message_len:
            message = message[: self.max_message_len]
            message += "\n[Message truncated to fit within the max length]"

        self.conversation.append({"role": "user", "content": message})

        # Get Claude's response
        response = self.client.messages.create(
            # model="claude-3-5-haiku-20241022",
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.7,
            messages=self.conversation,  # type: ignore
        )

        # Extract Claude's response
        claude_response = response.content[0].text  # type: ignore

        # Add Claude's response to the conversation
        self.conversation.append({"role": "assistant", "content": claude_response})

        return claude_response

    def get_last_message(self) -> str:
        return self.conversation[-1]["content"]

    def extract_tag(self, message: str, tag: str) -> str | None:
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"

        start = message.find(start_tag)
        end = message.find(end_tag)

        if start == -1 or end == -1:
            return None

        return message[start + len(start_tag) : end]

    def save_conversation(self, filename: str):
        with open(filename, "w") as file:
            file.write(self.conversation_to_string())

    def conversation_to_string(self):
        conversation = ""
        for message in self.conversation:
            conversation += f"{message['role']}: {message['content']}\n\n"
        return conversation

    def get_preprompt(self) -> str:
        """
        Returns the preprompt string.
        """
        return self.conversation[0]["content"]

    def set_preprompt(self, preprompt: str):
        """
        Sets the preprompt string.
        """
        self.conversation[0]["content"] = preprompt

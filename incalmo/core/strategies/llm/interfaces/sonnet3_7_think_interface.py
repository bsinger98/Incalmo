import anthropic

from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface

# Set up the Anthropic client
client = anthropic.Anthropic()


class Sonnet3_7_ThinkingInterface(LLMInterface):
    def __init__(self, logger, environment_state_service, config):
        super().__init__(logger, environment_state_service, config)

        # Initialize the conversation
        self.conversation = [
            {"role": "user", "content": self.pre_prompt},
        ]

    def get_response(self, perry_response: str | None = None) -> str:
        if perry_response:
            self.conversation.append({"role": "user", "content": perry_response})
            self.logger.info(f"Perry's response: \n{perry_response}")

        # Get Claude's response
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=8192,
            messages=self.conversation,
            thinking={"type": "enabled", "budget_tokens": 4096},
        )

        # Extract Claude's response
        claude_response = None
        for msg in response.content:
            if msg.type == "text":
                claude_response = msg.text

        if claude_response == None:
            raise Exception("No response from Claude")

        self.logger.info(f"Claude's response: \n{claude_response}")

        # Add Claude's response to the conversation
        self.conversation.append({"role": "assistant", "content": claude_response})

        return claude_response

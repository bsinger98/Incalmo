import anthropic

from plugins.deception.app.strategies.llm.interfaces.llm_interface import LLMInterface

# Set up the Anthropic client
client = anthropic.Anthropic()


class Sonnet3Interface(LLMInterface):
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
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            temperature=0.7,
            messages=self.conversation,
        )

        # Extract Claude's response
        claude_response = response.content[0].text
        self.logger.info(f"Claude's response: \n{claude_response}")

        # Add Claude's response to the conversation
        self.conversation.append({"role": "assistant", "content": claude_response})

        return claude_response

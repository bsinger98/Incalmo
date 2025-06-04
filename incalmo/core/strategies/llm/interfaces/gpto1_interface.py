from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from openai import OpenAI


client = OpenAI()


class GPTo1Interface(LLMInterface):
    def __init__(self, logger, environment_state_service, config):
        super().__init__(logger, environment_state_service, config)

        self.model = "o1-preview"
        # Initialize the conversation
        self.conversation = [{"role": "user", "content": self.pre_prompt}]

    def get_response(self, incalmo_response: str | None = None) -> str:
        if incalmo_response:
            self.conversation.append({"role": "user", "content": incalmo_response})
            self.logger.info(f"Incalmo's response: \n{incalmo_response}")

        # Get Claude's response
        response = client.chat.completions.create(
            model=self.model,
            messages=self.conversation,
        )

        # Extract Claude's response
        gpt_response = response.choices[0].message.content
        self.logger.info(f"GPTs response: \n{gpt_response}")

        # Add Claude's response to the conversation
        self.conversation.append({"role": "assistant", "content": gpt_response})

        return gpt_response

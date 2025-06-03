import requests
import json
from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface

OLLAMA_URL = "http://tiger2.lan.local.cmu.edu:11434/api/generate"


def convert_conversation_to_prompt(conversation):
    prompt = ""
    for message in conversation:
        if message["role"] == "user":
            prompt += f"User: {message['content']}\n"
        elif message["role"] == "assistant":
            prompt += f"Assistant: {message['content']}\n"
    return prompt


class DeepSeek7bInterface(LLMInterface):
    def __init__(self, logger, environment_state_service, config):
        super().__init__(logger, environment_state_service, config)

        # Initialize the conversation and Ollama settings
        self.conversation = [
            {"role": "user", "content": self.pre_prompt},
        ]
        self.ollama_url = OLLAMA_URL
        self.model = "deepseek-r1:70b"

    def get_response(self, incalmo_response: str | None = None) -> str:
        if incalmo_response:
            self.conversation.append({"role": "user", "content": incalmo_response})
            self.logger.info(f"Incalmo's response: \n{incalmo_response}")

        # Prepare the request for Ollama
        prompt = convert_conversation_to_prompt(self.conversation)
        payload = {"model": self.model, "prompt": prompt, "stream": False}

        try:
            # Send request to Ollama
            response = requests.post(self.ollama_url, json=payload, stream=True)
            response.raise_for_status()

            print(response.json())
            llm_response = response.json()["response"]

            # Extract the response
            self.logger.info(f"DeepSeek's response: \n{llm_response}")

            # Add the response to conversation history
            self.conversation.append({"role": "assistant", "content": llm_response})

            return llm_response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error communicating with Ollama server: {e}")
            raise

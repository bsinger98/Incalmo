from plugins.deception.app.strategies.llm.interfaces.llm_interface import LLMInterface
import google.generativeai as genai
import os

from google.generativeai.types import HarmCategory, HarmBlockThreshold


genai.configure(api_key=os.environ["API_KEY"])


class Gemini15FlashInterface(LLMInterface):
    def __init__(self, logger, environment_state_service, config):
        super().__init__(logger, environment_state_service, config)

        self.model_name = "gemini-1.5-flash"
        self.model = genai.GenerativeModel(self.model_name)

        self.saftey_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        # Initialize the conversation
        self.conversation = [{"role": "user", "parts": self.pre_prompt}]
        self.chat = self.model.start_chat(history=self.conversation)  # type: ignore

    def get_response(self, perry_response: str | None = None) -> str:
        if perry_response is None:
            perry_response = "Please provide a response."

        self.logger.info(f"Perry's response: \n{perry_response}")

        gemini_response = self.chat.send_message(
            perry_response, safety_settings=self.saftey_settings
        )

        # Extract response
        gemini_response = gemini_response.text
        self.logger.info(f"Gemini's response: \n{gemini_response}")

        return gemini_response

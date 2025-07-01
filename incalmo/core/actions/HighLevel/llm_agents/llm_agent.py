from incalmo.core.strategies.llm.langchain_registry import LangChainRegistry
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from incalmo.core.services.config_service import ConfigService


class LLMAgent:
    def __init__(self, preprompt: str):
        # Initialize the conversation
        self.conversation = [
            {"role": "system", "content": preprompt},
        ]
        self._registry = LangChainRegistry()
        self.execution_llm = ConfigService().get_config().execution_llm

        self.max_message_len = 30000

    def send_message(self, message: str) -> str:
        # Trim message to fit within the max length
        if len(message) > self.max_message_len:
            message = message[: self.max_message_len]
            message += "\n[Message truncated to fit within the max length]"

        # Prepare the messages for the LLM
        self.conversation.append({"role": "user", "content": message})

        # Get the response from the LLM
        response = self.get_response_from_model(
            model_name=self.execution_llm,
            messages=self.conversation,
        )

        # Add Claude's response to the conversation
        self.conversation.append({"role": "assistant", "content": response})

        return response

    def get_response_from_model(self, model_name: str, messages: list[dict]) -> str:
        langchain_messages = []

        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
        model = self._registry.get_model(model_name)
        response = model.invoke(langchain_messages)

        return response.content

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

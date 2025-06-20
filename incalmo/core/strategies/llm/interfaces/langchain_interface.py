from incalmo.core.strategies.llm.interfaces.llm_interface import LLMInterface
from incalmo.core.strategies.llm.langchain_registry import LangChainRegistry
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class LangChainInterface(LLMInterface):
    def __init__(
        self,
        logger,
        environment_state_service,
        config,
        model_name,
    ):
        super().__init__(logger, environment_state_service, config)

        self.model_name = model_name
        self._registry = LangChainRegistry()
        self.conversation = [
            {"role": "system", "content": self.pre_prompt},
        ]

    def get_response(self, incalmo_response: str | None = None) -> str:
        if not incalmo_response and len(self.conversation) <= 1:
            # Non empty stating message required for certain LLMs
            starter_message = (
                "Hello, I need your assistance with a cybersecurity assessment."
            )
            self.conversation.append({"role": "user", "content": starter_message})
        elif incalmo_response:
            self.conversation.append({"role": "user", "content": incalmo_response})
            self.logger.info(f"Incalmo's response: \n{incalmo_response}")

        messages_to_send = self.conversation

        llm_response = self.get_response_from_model(
            model_name=self.model_name,
            messages=messages_to_send,
        )

        self.logger.info(f"{self.model_name} response: \n{llm_response}")
        self.conversation.append({"role": "assistant", "content": llm_response})

        return llm_response

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

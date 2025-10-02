from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from typing import Dict, Any


class LangChainRegistry:
    def __init__(self):
        # Store factory functions, not instances
        self._model_factories = {
            # OpenAI models
            "gpt-5": lambda: ChatOpenAI(model="gpt-5"),
            "gpt-4": lambda: ChatOpenAI(model="gpt-4"),
            "gpt-4o": lambda: ChatOpenAI(model="gpt-4o"),
            "gpt-4o-mini": lambda: ChatOpenAI(model="gpt-4o-mini"),
            "gpt-3.5-turbo": lambda: ChatOpenAI(model="gpt-3.5-turbo"),
            "gpt-o1": lambda: ChatOpenAI(model="o1-preview"),
            # Anthropic models
            "claude-3-opus": lambda: ChatAnthropic(
                model_name="claude-3-opus-latest",
                temperature=0.7,
                timeout=None,
                stop=None,
            ),
            "claude-3-sonnet": lambda: ChatAnthropic(
                model_name="claude-3-sonnet-latest",
                temperature=0.7,
                timeout=None,
                stop=None,
            ),
            "claude-3-haiku": lambda: ChatAnthropic(
                model_name="claude-3-haiku-latest",
                temperature=0.7,
                timeout=None,
                stop=None,
            ),
            "claude-3.5-sonnet": lambda: ChatAnthropic(
                model_name="claude-3-5-sonnet-latest",
                temperature=0.7,
                timeout=None,
                stop=None,
            ),
            "claude-3.5-haiku": lambda: ChatAnthropic(
                model_name="claude-3-5-haiku-latest",
                temperature=0.7,
                timeout=None,
                stop=None,
            ),
            "claude-3.7-sonnet": lambda: ChatAnthropic(
                model_name="claude-3-7-sonnet-latest",
                temperature=0.7,
                timeout=None,
                stop=None,
            ),
            "claude-opus-4-1": lambda: ChatAnthropic(
                model_name="claude-opus-4-1",
                temperature=0.7,
                timeout=None,
                stop=None,
            ),
            # Google Gemini models
            "gemini-1.5-pro": lambda: ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", temperature=0.7
            ),
            "gemini-1.5-flash": lambda: ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", temperature=0.7
            ),
            "gemini-2.5-pro": lambda: ChatGoogleGenerativeAI(
                model="gemini-2.5-pro", temperature=0.7
            ),
            "gemini-2-flash": lambda: ChatGoogleGenerativeAI(
                model="gemini-2-flash", temperature=0.7
            ),
            # Other models
            "deepseek-7b": lambda: ChatDeepSeek(
                model="deepseek-ai/deepseek-coder-7b-instruct", temperature=0.7
            ),
        }

        # Cache for instantiated models
        self._models: Dict[str, Any] = {}

    def get_model(self, model_name: str):
        """Get or create a model instance by name"""
        if model_name not in self._model_factories:
            raise ValueError(
                f"Model {model_name} not found. Available models: {', '.join(self._model_factories.keys())}"
            )

        # Return cached instance if it exists
        if model_name in self._models:
            return self._models[model_name]

        # Create new instance
        model = self._model_factories[model_name]()
        self._models[model_name] = model
        return model

    def list_models(self) -> list[str]:
        return list(self._model_factories.keys())

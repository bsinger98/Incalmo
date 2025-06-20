from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepseek


class LangChainRegistry:
    def __init__(self):
        self._models = {
            # OpenAI models
            "gpt-4": ChatOpenAI(model="gpt-4", temperature=0.7),
            "gpt-4o-mini": ChatOpenAI(model="gpt-4o-mini", temperature=0.7),
            "gpt-3.5-turbo": ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7),
            "gpt-o1": ChatOpenAI(model="o1-preview", temperature=0.7),
            # Anthropic models
            "claude-3-opus": ChatAnthropic(
                model="claude-3-opus-20240229", temperature=0.7
            ),
            "claude-3-sonnet": ChatAnthropic(
                model="claude-3-sonnet-20240229", temperature=0.7
            ),
            "claude-3-haiku": ChatAnthropic(
                model="claude-3-haiku-20240307", temperature=0.7
            ),
            "claude-3.5-sonnet": ChatAnthropic(
                model="claude-3-5-sonnet-20240620", temperature=0.7
            ),
            "claude-3.5-haiku": ChatAnthropic(
                model="claude-3-5-haiku-20240307", temperature=0.7
            ),
            "claude-3.7-sonnet": ChatAnthropic(
                model="claude-3-7-sonnet-20240307", temperature=0.7
            ),
            "claude-3.7-thinking": ChatAnthropic(
                model="claude-3-7-thinking-20240603", temperature=0.7
            ),
            # Google Gemini models
            "gemini-1.5-pro": ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", temperature=0.7
            ),
            "gemini-1.5-flash": ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", temperature=0.7
            ),
            "gemini-2.5-pro": ChatGoogleGenerativeAI(
                model="gemini-2.5-pro", temperature=0.7
            ),
            "gemini-2-flash": ChatGoogleGenerativeAI(
                model="gemini-2-flash", temperature=0.7
            ),
            # Other models
            "deepseek-7b": ChatDeepseek(
                model="deepseek-ai/deepseek-coder-7b-instruct", temperature=0.7
            ),
        }

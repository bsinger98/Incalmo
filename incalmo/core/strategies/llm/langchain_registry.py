import os

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from typing import Any, Callable, Dict, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Named-deployment registry
#
# Each entry is a *deployment*: an explicit binding of
#   logical name  →  { provider adapter, endpoint, credential, upstream model }
#
# The credential is referenced by the *name* of an environment variable
# (`credential_ref`), never the secret value, and it is resolved fail-fast at
# get_model() time. This guarantees the intended key is used for the intended
# deployment — no reliance on a provider SDK silently reading an ambient env var.
#
# `base_url` may be a literal URL, None (use the provider default), or an
# "env/VAR" reference resolved at build time (used for the LiteLLM proxy, whose
# URL lives in the environment rather than in code).
#
# To route a model through the vendor's own API vs a LiteLLM proxy, pick the
# corresponding named deployment (e.g. "claude-opus-5" vs "claude-opus-5-litellm").
# ─────────────────────────────────────────────────────────────────────────────


def _resolve(value: Optional[str]) -> Optional[str]:
    """Resolve an 'env/VAR' indirection to its environment value; pass through otherwise."""
    if value and value.startswith("env/"):
        var = value[len("env/") :]
        resolved = os.environ.get(var)
        if not resolved:
            raise RuntimeError(
                f"Deployment references base_url '{value}', but env var '{var}' is unset."
            )
        return resolved
    return value


# ── Provider adapters: how to build each client and WHERE the key is injected ──
def _build_openai(d: dict, key: str):
    kwargs: Dict[str, Any] = dict(model=d["model"], api_key=key, **d.get("params", {}))
    base_url = _resolve(d.get("base_url"))
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)


def _build_anthropic(d: dict, key: str):
    kwargs: Dict[str, Any] = dict(
        model_name=d["model"], api_key=key, **d.get("params", {})
    )
    base_url = _resolve(d.get("base_url"))
    if base_url:
        kwargs["base_url"] = base_url
    return ChatAnthropic(**kwargs)


def _build_google(d: dict, key: str):
    return ChatGoogleGenerativeAI(
        model=d["model"], google_api_key=key, **d.get("params", {})
    )


def _build_deepseek(d: dict, key: str):
    kwargs: Dict[str, Any] = dict(model=d["model"], api_key=key, **d.get("params", {}))
    base_url = _resolve(d.get("base_url"))
    if base_url:
        kwargs["api_base"] = base_url
    return ChatDeepSeek(**kwargs)


_ADAPTERS: Dict[str, Callable[[dict, str], Any]] = {
    "openai": _build_openai,
    # OpenAI-compatible surface: OpenAI direct, Azure, GLM/z.ai, and LiteLLM all land here.
    "openai_compatible": _build_openai,
    "anthropic": _build_anthropic,
    "google": _build_google,
    "deepseek": _build_deepseek,
}


# ── Compact tables of direct (vendor-native) deployments ─────────────────────
_ANTHROPIC_STD = {"temperature": 0.7, "timeout": None, "stop": None}
_ANTHROPIC_C5 = {"temperature": 1, "timeout": None, "stop": None}  # Claude 5 requires temp=1

# name -> upstream OpenAI model id
_OPENAI_DIRECT = {
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4": "gpt-4",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt-4.1": "gpt-4.1",
    "gpt-4.1-mini": "gpt-4.1-mini",
    "gpt-4.1-nano": "gpt-4.1-nano",
    "gpt-o1": "o1-preview",  # LEGACY alias
    "o1": "o1",
    "o1-mini": "o1-mini",
    "o1-pro": "o1-pro",
    "o3-mini": "o3-mini",
    "o3": "o3",
    "o3-pro": "o3-pro",
    "o4-mini": "o4-mini",
    "gpt-5": "gpt-5",
    "gpt-5-mini": "gpt-5-mini",
    "gpt-5-nano": "gpt-5-nano",
    "gpt-5.2": "gpt-5.2",
    "gpt-5.2-pro": "gpt-5.2-pro",
    "gpt-5.4-mini": "gpt-5.4-mini",
    "gpt-5.4": "gpt-5.4",
    "gpt-5.4-pro": "gpt-5.4-pro-2026-03-05",
    "gpt-5.5": "gpt-5.5",
    "gpt-5.6-luna": "gpt-5.6-luna",
    "gpt-5.6-sol": "gpt-5.6-sol",
    "gpt-5.6-terra": "gpt-5.6-terra",
}

# name -> (upstream anthropic model id, params)
_ANTHROPIC_DIRECT = {
    "claude-3-opus": ("claude-3-opus-latest", _ANTHROPIC_STD),
    "claude-3-sonnet": ("claude-3-sonnet-20240229", _ANTHROPIC_STD),
    "claude-3-haiku": ("claude-3-haiku-20240307", _ANTHROPIC_STD),
    "claude-3.5-sonnet": ("claude-3-5-sonnet-latest", _ANTHROPIC_STD),
    "claude-3.5-haiku": ("claude-3-5-haiku-latest", _ANTHROPIC_STD),
    "claude-3.7-sonnet": ("claude-3-7-sonnet-latest", _ANTHROPIC_STD),
    "claude-4.0-sonnet": ("claude-sonnet-4-0", _ANTHROPIC_STD),
    "claude-4.5-sonnet": ("claude-sonnet-4-5-20250929", _ANTHROPIC_STD),
    "claude-sonnet-4-6": ("claude-sonnet-4-6", _ANTHROPIC_STD),
    "claude-haiku-4-5": ("claude-haiku-4-5-20251001", _ANTHROPIC_STD),
    "claude-opus-4-1": ("claude-opus-4-1-20250805", _ANTHROPIC_STD),
    "claude-opus-4-6": ("claude-opus-4-6", _ANTHROPIC_STD),
    "claude-opus-5": ("claude-opus-5", _ANTHROPIC_C5),
    "claude-sonnet-5": ("claude-sonnet-5", _ANTHROPIC_C5),
    "claude-fable-5": ("claude-fable-5", _ANTHROPIC_C5),
    "claude-mythos-5": ("claude-mythos-5", _ANTHROPIC_C5),
}

# name -> upstream gemini model id
_GOOGLE_DIRECT = {
    "gemini-1.5-pro": "gemini-1.5-pro",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-2.0-flash": "gemini-2.0-flash",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview": "gemini-3.1-flash-lite-preview",
    "gemini-3.1-pro-preview": "gemini-3.1-pro-preview",
}

# name -> upstream deepseek model id
_DEEPSEEK_DIRECT = {
    "deepseek-7b": "deepseek-ai/deepseek-coder-7b-instruct",
    "deepseek-v3": "deepseek-chat",
    "deepseek-r1": "deepseek-reasoner",
}


def _build_deployments() -> Dict[str, dict]:
    d: Dict[str, dict] = {}

    for name, model in _OPENAI_DIRECT.items():
        d[name] = {
            "provider": "openai",
            "model": model,
            "base_url": None,
            "credential_ref": "OPENAI_API_KEY",
            "params": {},
        }

    for name, (model, params) in _ANTHROPIC_DIRECT.items():
        d[name] = {
            "provider": "anthropic",
            "model": model,
            "base_url": None,
            "credential_ref": "ANTHROPIC_API_KEY",
            "params": dict(params),
        }

    for name, model in _GOOGLE_DIRECT.items():
        d[name] = {
            "provider": "google",
            "model": model,
            "base_url": None,
            "credential_ref": "GOOGLE_API_KEY",
            "params": {"temperature": 0.7},
        }

    for name, model in _DEEPSEEK_DIRECT.items():
        d[name] = {
            "provider": "deepseek",
            "model": model,
            "base_url": None,
            "credential_ref": "DEEPSEEK_API_KEY",
            "params": {"temperature": 0.7},
        }

    # GLM via z.ai's OpenAI-compatible endpoint
    d["glm-5.2"] = {
        "provider": "openai_compatible",
        "model": "glm-5.2",
        "base_url": "https://api.z.ai/api/paas/v4/",
        "credential_ref": "ZAI_API_KEY",
        "params": {"temperature": 0.7},
    }

    # Kimi (Moonshot) via OpenRouter's OpenAI-compatible endpoint. The CMU
    # gateway does not carry a Kimi model, so this routes through OpenRouter,
    # which namespaces models as `vendor/model`. `model` must match OpenRouter's
    # catalog; base_url is overridable via OPENROUTER_BASE_URL.
    d["kimi-k3"] = {
        "provider": "openai_compatible",
        "model": "moonshotai/kimi-k3",
        "base_url": os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        "credential_ref": "OPENROUTER_API_KEY",
        "params": {},
    }

    # ── LiteLLM-proxied named deployments ────────────────────────────────────
    # Same models, routed through a single OpenAI-compatible LiteLLM endpoint
    # with a single key. The `model` string here must match a `model_name`
    # served by the proxy's /v1/models list. base_url + key come from the
    # environment (LITELLM_BASE_URL / LITELLM_API_KEY).
    #
    # These IDs are the ones exposed by the CMU AI gateway
    # (https://ai-gateway.andrew.cmu.edu/v1) as of setup; re-check /v1/models
    # if the gateway's catalog changes. No sampling params are set here — each
    # model uses its own default — matching the OpenAI direct deployments.
    _LITELLM_MODELS = [
        # (deployment name, gateway model id)
        # ── Anthropic (Bedrock-hosted) ──
        ("claude-sonnet-5-litellm", "us.anthropic.claude-sonnet-5"),
        ("claude-opus-4-8-litellm", "us.anthropic.claude-opus-4-8"),
        ("claude-opus-4-7-litellm", "us.anthropic.claude-opus-4-7"),
        ("claude-opus-4-6-litellm", "us.anthropic.claude-opus-4-6-v1"),
        ("claude-sonnet-4-6-litellm", "us.anthropic.claude-sonnet-4-6"),
        ("claude-haiku-4-5-litellm", "us.anthropic.claude-haiku-4-5-20251001-v1:0"),
        # ── OpenAI ──
        ("gpt-5-mini-litellm", "gpt-5-mini"),
        ("gpt-5-nano-litellm", "gpt-5-nano"),
        ("gpt-5.4-mini-litellm", "gpt-5.4-mini"),
        ("gpt-4.1-mini-litellm", "gpt-4.1-mini"),
        ("gpt-5.6-sol-litellm", "gpt-5.6-sol"),
        ("gpt-5.6-terra-litellm", "gpt-5.6-terra"),
        ("gpt-5.6-luna-litellm", "gpt-5.6-luna"),
        ("gpt-5.5-litellm", "gpt-5.5"),
        ("gpt-5.4-litellm", "gpt-5.4"),
        ("gpt-5.4-pro-litellm", "gpt-5.4-pro"),
        # ── Google Gemini ──
        ("gemini-3.1-pro-litellm", "gemini/gemini-3.1-pro-preview"),
        ("gemini-3.5-flash-litellm", "gemini/gemini-3.5-flash"),
        ("gemini-2.5-pro-litellm", "gemini/gemini-2.5-pro"),
    ]
    for name, model in _LITELLM_MODELS:
        d[name] = {
            "provider": "openai_compatible",
            "model": model,
            "base_url": "env/LITELLM_BASE_URL",
            "credential_ref": "LITELLM_API_KEY",
            "params": {},
        }

    return d


class LangChainRegistry:
    def __init__(self):
        self._deployments: Dict[str, dict] = _build_deployments()
        # Cache for instantiated models
        self._models: Dict[str, Any] = {}

    def get_model(self, model_name: str):
        """Resolve a named deployment to a client, binding its intended credential."""
        if model_name not in self._deployments:
            raise ValueError(
                f"Model {model_name} not found. Available models: "
                f"{', '.join(self._deployments.keys())}"
            )

        if model_name in self._models:
            return self._models[model_name]

        d = self._deployments[model_name]

        # Explicit, fail-fast credential resolution: the deployment names the one
        # env var it is allowed to use; no ambient/implicit SDK key fallback.
        api_key = os.environ.get(d["credential_ref"])
        if not api_key:
            raise RuntimeError(
                f"Deployment '{model_name}' requires credential '{d['credential_ref']}', "
                f"but that environment variable is unset."
            )

        adapter = _ADAPTERS[d["provider"]]
        model = adapter(d, api_key)
        self._models[model_name] = model
        return model

    def list_models(self) -> list[str]:
        return list(self._deployments.keys())

import functools
import sys
from importlib import import_module
from importlib.metadata import version

from packaging.version import Version, parse

from .log_config import logger

# from .cohere import CohereProvider
# from .groq import GroqProvider
from .litellm import LiteLLMProvider
# from .ollama import OllamaProvider
# from .openai import OpenAiProvider
# from .anthropic import AnthropicProvider
# from .mistral import MistralProvider
# from .ai21 import AI21Provider

original_func = {}
original_create = None
original_create_async = None


class LlmTracker:
    SUPPORTED_APIS = {
        "litellm": {"1.3.1": ("openai_chat_completions.completion",)},
        "openai": {
            "1.0.0": ("chat.completions.create",),
            "0.0.0": (
                "ChatCompletion.create",
                "ChatCompletion.acreate",
            ),
        }
    }

    def __init__(self, client = "0001"):
        self.client = client
        print(f"Default client {self.client}")

    def override_api(self):
        """
        Overrides key methods of the specified API to record events.
        """

        for api in self.SUPPORTED_APIS:
            if api in sys.modules:
                module = import_module(api)
                if api == "litellm":
                    module_version = version(api)
                    if module_version is None:
                        logger.warning("Cannot determine LiteLLM version. Only LiteLLM>=1.3.1 supported.")

                    if Version(module_version) >= parse("1.3.1"):
                        provider = LiteLLMProvider()
                        provider.override()
                    else:
                        logger.warning(f"Only LiteLLM>=1.3.1 supported. v{module_version} found.")
                    return  # If using an abstraction like litellm, do not patch the underlying LLM APIs

        else:
            logger.warning(f"Only LiteLLM>=1.3.1 supported. Module not found.")

    def stop_instrumenting(self):
        LiteLLMProvider().undo_override()
        
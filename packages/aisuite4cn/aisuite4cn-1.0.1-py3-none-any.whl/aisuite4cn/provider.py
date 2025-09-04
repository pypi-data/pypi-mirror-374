import functools
import importlib
from abc import ABC, abstractmethod
from pathlib import Path


class LLMError(Exception):
    """Custom exception for LLM errors."""

    def __init__(self, message):
        super().__init__(message)


class Provider(ABC):
    @abstractmethod
    def chat_completions_create(self, model, messages):
        """Abstract method for chat completion calls, to be implemented by each provider."""
        pass

    @abstractmethod
    async def async_chat_completions_create(self, model, messages, **kwargs):
        """Abstract method for chat completion calls, to be implemented by each provider."""
        pass


class ProviderFactory:
    """Factory to dynamically load provider instances based on naming conventions."""

    PROVIDERS_DIR = Path(__file__).parent / "providers"

    @classmethod
    def create_provider(cls, provider_key, config):
        """Dynamically load and create an instance of a provider based on the naming convention."""
        # Convert provider_key to the expected module and class names
        provider_class_name = f"{provider_key.capitalize()}Provider"
        provider_module_name = f"{provider_key}_provider"

        module_path = f"aisuite4cn.providers.{provider_module_name}"

        # Lazily load the module
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(
                f"Could not import module {module_path}: {str(e)}. Please ensure the provider is supported by doing ProviderFactory.get_supported_providers()"
            )

        # Instantiate the provider class
        provider_class = getattr(module, provider_class_name)
        return provider_class(**config)

    @classmethod
    @functools.cache
    def get_supported_providers(cls):
        """List all supported provider names based on files present in the providers directory."""
        provider_files = Path(cls.PROVIDERS_DIR).glob("*_provider.py")
        return {file.stem.replace("_provider", "") for file in provider_files}


import openai


class BaseProvider(Provider):
    """Base class for all openai compatible providers."""

    def __init__(self, base_url, **config):
        self.base_url = base_url
        self.config = dict(config)
        self._client = None
        self._async_client = None

    @property
    def client(self):
        """Getter for the OpenAI client."""
        if not self._client:
            self._client = openai.OpenAI(base_url=self.base_url, **self.config)
        return self._client

    @client.setter
    def client(self, value):
        """Setter for the OpenAI client."""
        self._client = value

    @property
    def async_client(self):
        """Getter for the OpenAI client."""
        if not self._async_client:
            self._async_client = openai.AsyncOpenAI(base_url=self.base_url, **self.config)
        return self._async_client

    @async_client.setter
    def async_client(self, value):
        """Setter for the OpenAI client."""
        self._async_client = value

    def chat_completions_create(self, model, messages, **kwargs):
        """Create a chat completion using the OpenAI API."""

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

    async def async_chat_completions_create(self, model, messages, **kwargs):
        """Create a chat completion using the OpenAI API."""
        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

"""LLM provider abstractions for different LLM services."""

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI

from ..core.config import get_app_config
from ..core.models import LLMProvider, ReviewConfig


class LLMProviderBase(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: ReviewConfig):
        """Initialize the LLM provider.

        Args:
            config: Review configuration
        """
        self.config = config
        self.app_config = get_app_config()

    @abstractmethod
    def get_language_model(self) -> BaseLanguageModel:
        """Get the LangChain language model instance.

        Returns:
            Configured language model
        """
        pass

    @abstractmethod
    def validate_config(self) -> None:
        """Validate that the provider configuration is correct.

        Raises:
            ValueError: If configuration is invalid
        """
        pass


class OpenAIProvider(LLMProviderBase):
    """OpenAI LLM provider."""

    def validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.app_config.openai_api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
            )

        # Validate model name
        from ..core.config import LLMProvider, get_available_models

        available_models = get_available_models(LLMProvider.OPENAI)
        if self.config.model_name not in available_models:
            raise ValueError(
                f"Invalid OpenAI model: {self.config.model_name}. "
                f"Available models: {', '.join(available_models)}"
            )

    def get_language_model(self) -> BaseLanguageModel:
        """Get OpenAI language model instance.

        Returns:
            ChatOpenAI instance
        """
        return ChatOpenAI(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            openai_api_key=self.app_config.openai_api_key,
        )


class GrokProvider(LLMProviderBase):
    """Grok LLM provider."""

    def validate_config(self) -> None:
        """Validate Grok configuration."""
        if not self.app_config.grok_api_key:
            raise ValueError(
                "Grok API key is required. Set GROK_API_KEY environment variable."
            )

        if self.config.model_name not in ["grok-beta", "grok-vision-beta"]:
            raise ValueError(f"Invalid Grok model: {self.config.model_name}")

    def get_language_model(self) -> BaseLanguageModel:
        """Get Grok language model instance.

        Returns:
            ChatOpenAI instance (Grok uses OpenAI-compatible API)
        """
        # Grok uses OpenAI-compatible API format
        return ChatOpenAI(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            openai_api_key=self.app_config.grok_api_key,
            openai_api_base="https://api.x.ai/v1",  # Grok API endpoint
        )


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def create_provider(config: ReviewConfig) -> LLMProviderBase:
        """Create an LLM provider instance.

        Args:
            config: Review configuration

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider is not supported
        """
        if config.llm_provider == LLMProvider.OPENAI:
            provider = OpenAIProvider(config)
        elif config.llm_provider == LLMProvider.GROK:
            provider = GrokProvider(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")

        provider.validate_config()
        return provider


def get_language_model(config: ReviewConfig) -> BaseLanguageModel:
    """Get a configured language model instance.

    Args:
        config: Review configuration

    Returns:
        Configured language model
    """
    provider = LLMProviderFactory.create_provider(config)
    return provider.get_language_model()

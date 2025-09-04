import os
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Callable, Dict

from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
from langchain_core.language_models.chat_models import BaseChatModel


@dataclass
class LLMConfig:
    model_name: str
    provider: str


class LLMProvider(StrEnum):
    OPENAI = "openai"
    BEDROCK = "bedrock"


class OpenAIModels(StrEnum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"


class BedrockModels(StrEnum):
    MISTRAL_SMALL = "mistral.mistral-small-2402-v1:0"
    MISTRAL_LARGE = "mistral.mistral-large-2402-v1:0"

    LLAMA_4_Maverick_17B_Instruct = "us.meta.llama4-maverick-17b-instruct-v1:0"
    LLAMA_4_Scout_17B_Instruct = "us.meta.llama4-scout-17b-instruct-v1:0"
    LLAMA3_3_70B_Instruct = "us.meta.llama3-3-70b-instruct-v1:0"
    LLAMA_3_2_1B_Instruct = "us.meta.llama3-2-1b-instruct-v1:0"
    LLAMA_3_2_3B_Instruct = "us.meta.llama3-2-3b-instruct-v1:0"
    LLAMA_3_1_8B_Instruct = "meta.llama3-1-8b-instruct-v1:0"

    AMAZON_Nova_Premier = "us.amazon.nova-premier-v1:0"
    AMAZON_Nova_Pro = "us.amazon.nova-pro-v1:0"
    AMAZON_Nova_Lite = "us.amazon.nova-lite-v1:0"
    AMAZON_Nova_Micro = "us.amazon.nova-micro-v1:0"

    CLAUDE_3_5_Haiku = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    CLAUDE_3_Haiku = "us.anthropic.claude-3-haiku-20240307-v1:0"


class AvailableLLMs(Enum):
    GPT_4O = LLMConfig(model_name=OpenAIModels.GPT_4O, provider=LLMProvider.OPENAI)
    GPT_4O_MINI = LLMConfig(
        model_name=OpenAIModels.GPT_4O_MINI, provider=LLMProvider.OPENAI
    )
    GPT_4 = LLMConfig(model_name=OpenAIModels.GPT_4, provider=LLMProvider.OPENAI)
    GPT_3_5_TURBO = LLMConfig(
        model_name=OpenAIModels.GPT_3_5_TURBO, provider=LLMProvider.OPENAI
    )
    GPT_4_1 = LLMConfig(model_name=OpenAIModels.GPT_4_1, provider=LLMProvider.OPENAI)
    GPT_4_1_MINI = LLMConfig(
        model_name=OpenAIModels.GPT_4_1_MINI, provider=LLMProvider.OPENAI
    )
    GPT_4_1_NANO = LLMConfig(
        model_name=OpenAIModels.GPT_4_1_NANO, provider=LLMProvider.OPENAI
    )
    GPT_5_MINI = LLMConfig(
        model_name=OpenAIModels.GPT_5_MINI, provider=LLMProvider.OPENAI
    )
    GPT_5_NANO = LLMConfig(
        model_name=OpenAIModels.GPT_5_NANO, provider=LLMProvider.OPENAI
    )

    BEDROCK_MISTRAL_SMALL = LLMConfig(
        model_name=BedrockModels.MISTRAL_SMALL, provider=LLMProvider.BEDROCK
    )
    BEDROCK_MISTRAL_LARGE = LLMConfig(
        model_name=BedrockModels.MISTRAL_LARGE, provider=LLMProvider.BEDROCK
    )

    BEDROCK_LLAMA_4_Maverick_17B_Instruct = LLMConfig(
        model_name=BedrockModels.LLAMA_4_Maverick_17B_Instruct,
        provider=LLMProvider.BEDROCK,
    )
    BEDROCK_LLAMA_4_Scout_17B_Instruct = LLMConfig(
        model_name=BedrockModels.LLAMA_4_Scout_17B_Instruct,
        provider=LLMProvider.BEDROCK,
    )
    BEDROCK_LLAMA3_3_70B_Instruct = LLMConfig(
        model_name=BedrockModels.LLAMA3_3_70B_Instruct, provider=LLMProvider.BEDROCK
    )
    BEDROCK_LLAMA_3_2_1B_Instruct = LLMConfig(
        model_name=BedrockModels.LLAMA_3_2_1B_Instruct, provider=LLMProvider.BEDROCK
    )
    BEDROCK_LLAMA_3_2_3B_Instruct = LLMConfig(
        model_name=BedrockModels.LLAMA_3_2_3B_Instruct, provider=LLMProvider.BEDROCK
    )
    BEDROCK_LLAMA_3_1_8B_Instruct = LLMConfig(
        model_name=BedrockModels.LLAMA_3_1_8B_Instruct, provider=LLMProvider.BEDROCK
    )

    BEDROCK_AMAZON_Nova_Premier = LLMConfig(
        model_name=BedrockModels.AMAZON_Nova_Premier, provider=LLMProvider.BEDROCK
    )
    BEDROCK_AMAZON_Nova_Pro = LLMConfig(
        model_name=BedrockModels.AMAZON_Nova_Pro, provider=LLMProvider.BEDROCK
    )
    BEDROCK_AMAZON_Nova_Lite = LLMConfig(
        model_name=BedrockModels.AMAZON_Nova_Lite, provider=LLMProvider.BEDROCK
    )
    BEDROCK_AMAZON_Nova_Micro = LLMConfig(
        model_name=BedrockModels.AMAZON_Nova_Micro, provider=LLMProvider.BEDROCK
    )

    BEDROCK_CLAUDE_3_5_Haiku = LLMConfig(
        model_name=BedrockModels.CLAUDE_3_5_Haiku, provider=LLMProvider.BEDROCK
    )
    BEDROCK_CLAUDE_3_Haiku = LLMConfig(
        model_name=BedrockModels.CLAUDE_3_Haiku, provider=LLMProvider.BEDROCK
    )


def _create_openai_client(model: OpenAIModels, **kwargs) -> BaseChatModel:
    return ChatOpenAI(
        model=model,
        api_key=os.environ.get("OPENAI_API_KEY"),
        **kwargs,
    )


def _create_bedrock_client(model: BedrockModels, **kwargs) -> BaseChatModel:
    return ChatBedrock(
        model_id=model,
        region_name="us-east-1",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        **kwargs,
    )


class LLMClientFactory:
    """Factory class for creating LLM clients based on model name."""

    _provider_handlers: Dict[str, Callable] = {
        LLMProvider.OPENAI: _create_openai_client,
        LLMProvider.BEDROCK: _create_bedrock_client,
    }

    @classmethod
    def register_provider(cls, provider: str, handler_func: Callable):
        cls._provider_handlers[provider] = handler_func

    @classmethod
    def create(cls, model_name: AvailableLLMs, **kwargs) -> BaseChatModel:
        model_config = model_name.value

        if model_config.provider in cls._provider_handlers:
            return cls._provider_handlers[model_config.provider](
                model_config.model_name, **kwargs
            )

        raise ValueError(f"Provider {model_config.provider} is not implemented.")

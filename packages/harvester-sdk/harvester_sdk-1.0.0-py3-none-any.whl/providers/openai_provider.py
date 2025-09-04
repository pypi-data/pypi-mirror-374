import logging
from typing import Any, Dict, List, Union
import asyncio

import openai
from openai import AsyncOpenAI

try:
    import tiktoken
except ImportError:
    tiktoken = None

from .base_provider import BaseProvider

logger = logging.getLogger(__name__)

def sanitize_openai_endpoint(endpoint: str) -> str:
    """Strip any trailing /chat/completions or subpaths from endpoint, leave at most /v1."""
    parts = endpoint.split('/v1', 1)
    sanitized = parts[0] + '/v1' if len(parts) > 1 else endpoint.rstrip('/')
    return sanitized

class OpenaiProvider(BaseProvider):
    """
    Provider for OpenAI models (chat & text) - Enhanced for harvest system compatibility
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.api_key: str = config.get("api_key") or openai.api_key
        if not self.api_key:
            raise ValueError("OpenAI API key missing. Set in config or OPENAI_API_KEY environment variable")

        raw_endpoint = config.get("endpoint", "https://api.openai.com/v1")
        self.base_url: str = sanitize_openai_endpoint(raw_endpoint)

        self.client: AsyncOpenAI = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # GPT-5 Series ONLY - All use /v1/responses endpoint
        # All models: 400K context, 128K max output tokens!
        self.model_settings: Dict[str, Dict[str, Any]] = {
            "gpt-5-2025-08-07": {
                "max_tokens": 128_000,  # 128K output!
                "cost_per_million_input": 1.25,
                "cost_per_million_output": 10.00,
                "context_window": 400_000,  # 400K context!
                "uses_responses_endpoint": True
            },
            "gpt-5-mini-2025-08-07": {
                "max_tokens": 128_000,  # 128K output!
                "cost_per_million_input": 0.30,
                "cost_per_million_output": 2.50,
                "context_window": 400_000,  # 400K context!
                "uses_responses_endpoint": True
            },
            "gpt-5-nano-2025-08-07": {
                "max_tokens": 128_000,  # 128K output!
                "cost_per_million_input": 0.08,
                "cost_per_million_output": 0.60,
                "context_window": 400_000,  # 400K context!
                "uses_responses_endpoint": True
            }
        }
        self.aliases: Dict[str, str] = config.get("aliases", {})
        self.default_model = config.get("default_model", "gpt-5-mini-2025-08-07")  # Default to GPT-5 mini
        
        logger.info(f"OpenAI provider initialized with {len(self.model_settings)} models")

    async def complete(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        model: str,
        **kwargs,
    ) -> str:
        """
        Ask a model for a completion.

        Args:
            prompt: Either a plain string (treated as a single user message) or
                   an already-formatted chat message list.
            model: Logical model name or alias.
            **kwargs: Optional overrides (temperature, top_p, max_tokens, etc.).

        Returns:
            The completion text from the model.
        """
        actual_model = self.resolve_model_alias(model)
        if actual_model not in self.model_settings:
            logger.warning(f"Unknown model '{actual_model}', falling back to {self.default_model}")
            actual_model = self.default_model

        estimated_tokens = self.estimate_tokens(
            prompt if isinstance(prompt, str) else self._messages_to_text(prompt),
            "",
            actual_model
        )
        await self._apply_rate_limit(estimated_tokens)

        # Prepare input according to API
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt

        settings = self.model_settings[actual_model]
        temperature = kwargs.get("temperature", 0.7)
        top_p = kwargs.get("top_p", 1.0)
        max_tokens = min(
            kwargs.get("max_tokens", settings["max_tokens"]),
            settings["max_tokens"]
        )

        # Remove kwargs only meant for chat endpoints
        openai_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in {"temperature", "top_p", "max_tokens"}
        }

        try:
            logger.debug(f"Making OpenAI request to {actual_model} with messages: {messages}")

            # ALL models use /v1/responses endpoint - NO chat/completions
            # Format messages for GPT-5 API (uses 'input' parameter)
            if isinstance(messages, list) and len(messages) > 0:
                # Extract the content from the message list
                input_text = messages[0].get('content', '') if len(messages) == 1 else \
                           '\n'.join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
            else:
                input_text = str(messages)
            
            # GPT-5 uses different parameter names and supports reasoning/verbosity
            request_params = {
                "model": actual_model,
                "input": input_text,  # GPT-5 uses 'input' not 'messages'
                "max_output_tokens": max_tokens
            }
            
            # Add reasoning effort if specified (minimal, low, medium, high)
            reasoning_effort = kwargs.get("reasoning_effort", "medium")
            if reasoning_effort:
                request_params["reasoning"] = {"effort": reasoning_effort}
            
            # Add verbosity if specified (low, medium, high)  
            verbosity = kwargs.get("verbosity", "medium")
            if verbosity:
                request_params["text"] = {"verbosity": verbosity}
            
            response = await self.client.responses.create(**request_params)
            
            # Extract content from GPT-5 response structure
            # According to OpenAI docs, GPT-5 responses have output_text field
            content = ""
            
            if hasattr(response, 'output_text'):
                # Official GPT-5 API response format
                content = response.output_text
            elif hasattr(response, 'output'):
                if hasattr(response.output, 'text'):
                    # Alternative format: response.output.text
                    content = response.output.text
                else:
                    content = str(response.output)
            elif hasattr(response, 'text'):
                # Direct text attribute
                content = response.text
            else:
                # Fallback: log the response type for debugging
                logger.warning(f"GPT-5 response type: {type(response)}, attributes: {dir(response)}")
                content = str(response)

            if not content:
                raise RuntimeError("Empty content returned from OpenAI API")

            logger.debug(f"OpenAI completion successful: {len(content)} characters")
            return content

        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit hit: {e}")
            await asyncio.sleep(60)
            raise RuntimeError(f"OpenAI rate limit exceeded: {e}") from e

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API error: {e}") from e

        except Exception as e:
            logger.error(f"OpenAI completion error: {e}")
            raise RuntimeError(f"OpenAI completion error: {e}") from e

    def resolve_model_alias(self, alias: str) -> str:
        return self.aliases.get(alias, alias)

    def estimate_tokens(self, prompt: str, response: str = "", model: str = None) -> int:
        if tiktoken and model:
            try:
                enc = tiktoken.encoding_for_model(model)
            except KeyError:
                enc = tiktoken.get_encoding("cl100k_base")
            prompt_tokens = len(enc.encode(prompt)) if prompt else 0
            response_tokens = len(enc.encode(response)) if response else 0
            return prompt_tokens + response_tokens
        total_chars = len(prompt) + len(response)
        return int(total_chars / 4)

    def estimate_cost(self, tokens: int, model: str) -> float:
        actual_model = self.resolve_model_alias(model)
        settings = self.model_settings.get(
            actual_model, 
            self.model_settings[self.default_model]
        )
        input_tokens = int(tokens * 0.7)
        output_tokens = tokens - input_tokens
        input_cost = (input_tokens / 1_000_000) * settings["cost_per_million_input"]
        output_cost = (output_tokens / 1_000_000) * settings["cost_per_million_output"]
        return input_cost + output_cost

    def _messages_to_text(self, messages: List[Dict[str, str]]) -> str:
        return " ".join(msg.get("content", "") for msg in messages)

    def get_model_info(self, model: str) -> Dict[str, Any]:
        actual_model = self.resolve_model_alias(model)
        return self.model_settings.get(actual_model, self.model_settings[self.default_model])

    def list_available_models(self) -> List[str]:
        return list(self.model_settings.keys())

    def list_aliases(self) -> Dict[str, str]:
        return self.aliases.copy()

    async def cleanup(self):
        if hasattr(self, 'client'):
            await self.client.close()
        await super().cleanup()

    def __repr__(self) -> str:
        return f"OpenaiProvider(models={len(self.model_settings)}, aliases={len(self.aliases)})"

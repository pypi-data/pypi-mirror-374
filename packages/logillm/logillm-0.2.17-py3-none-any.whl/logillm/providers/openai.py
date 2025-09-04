"""OpenAI provider implementation."""

import json
import os
from collections.abc import AsyncIterator
from typing import Any

try:
    import openai
    from openai import AsyncOpenAI as AsyncOpenAIClient
    from openai import OpenAI as OpenAIClient
    from openai.types.chat import ChatCompletion

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAIClient = None  # type: ignore
    AsyncOpenAIClient = None  # type: ignore
    ChatCompletion = None  # type: ignore

from ..core.types import Completion, TokenUsage, Usage
from .base import Provider, ProviderError, RateLimitError, TimeoutError


class OpenAIProvider(Provider):
    """OpenAI API provider implementation.

    Supports all OpenAI models including GPT-4, GPT-3.5, and o1 series.
    Features:
    - Structured outputs with response_format
    - Function/tool calling
    - Streaming responses
    - Vision models (GPT-4V)
    - Embeddings
    """

    def __init__(
        self,
        model: str = "gpt-4.1",  # Default to gpt-4.1 as requested
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ):
        """Initialize OpenAI provider.

        Args:
            model: Model name (e.g., "gpt-4.1", "gpt-4.1-mini", "o1-preview")
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            organization: Optional organization ID
            base_url: Optional base URL for API
            **kwargs: Additional provider configuration
        """
        if not HAS_OPENAI:
            raise ImportError(
                "OpenAI provider requires the 'openai' package. "
                "Install it with: pip install logillm[openai]"
            )

        # Get API key from environment if not provided
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        super().__init__(name="openai", model=model, api_key=api_key, base_url=base_url, **kwargs)

        self.organization = organization

        # Initialize clients
        if OpenAIClient is not None:
            self.client = OpenAIClient(
                api_key=api_key,
                organization=organization,
                base_url=base_url,
                timeout=self.timeout,
                max_retries=0,  # We handle retries ourselves
            )
        else:
            self.client = None

        if AsyncOpenAIClient is not None:
            self.async_client = AsyncOpenAIClient(
                api_key=api_key,
                organization=organization,
                base_url=base_url,
                timeout=self.timeout,
                max_retries=0,
            )
        else:
            self.async_client = None

    def __getstate__(self) -> dict:
        """Get state for pickling (excludes the OpenAI clients)."""
        state = self.__dict__.copy()
        # Remove the unpicklable OpenAI clients
        state.pop("client", None)
        state.pop("async_client", None)
        return state

    def __setstate__(self, state: dict) -> None:
        """Restore state after unpickling (recreates the OpenAI clients)."""
        self.__dict__.update(state)
        # Recreate the OpenAI clients
        from openai import AsyncOpenAI as AsyncOpenAIClient
        from openai import OpenAI as OpenAIClient

        self.client = OpenAIClient(
            api_key=self.api_key,
            organization=getattr(self, "organization", None),
            base_url=getattr(self, "base_url", None),
            timeout=self.timeout,
            max_retries=0,
        )

        self.async_client = AsyncOpenAIClient(
            api_key=self.api_key,
            organization=getattr(self, "organization", None),
            base_url=getattr(self, "base_url", None),
            timeout=self.timeout,
            max_retries=0,
        )

    async def _complete_impl(self, messages: list[dict[str, Any]], **kwargs: Any) -> Completion:
        """Generate completion using OpenAI API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional OpenAI parameters (temperature, max_tokens, etc.)

        Returns:
            Completion object
        """
        # Check cache first
        cached = await self._get_cached(messages, **kwargs)
        if cached:
            return cached

        # Validate content types for the model
        self.validate_content_types(messages)

        # Prepare multimodal messages if needed
        formatted_messages = self._prepare_multimodal_messages(messages)

        # Validate and prepare parameters
        params = self._prepare_params(kwargs)

        try:
            # Make API call
            response = await self.async_client.chat.completions.create(
                model=self.model, messages=formatted_messages, **params
            )

            # Convert to our Completion type
            completion = self._parse_completion(response)

            # Cache the result
            await self._set_cache(messages, completion, **kwargs)

            # Update metrics
            self._update_metrics(completion)

            return completion

        except openai.RateLimitError as e:
            raise RateLimitError(f"OpenAI rate limit exceeded: {e}") from e
        except openai.APITimeoutError as e:
            raise TimeoutError(f"OpenAI request timed out: {e}") from e
        except openai.AuthenticationError as e:
            raise ProviderError(f"OpenAI authentication failed: {e}") from e
        except openai.PermissionDeniedError as e:
            raise ProviderError(f"OpenAI permission denied: {e}") from e
        except openai.NotFoundError as e:
            raise ProviderError(f"OpenAI model not found: {e}") from e
        except openai.BadRequestError as e:
            raise ProviderError(f"OpenAI bad request: {e}") from e
        except openai.APIError as e:
            raise ProviderError(f"OpenAI API error: {e}") from e
        except Exception as e:
            raise ProviderError(f"Unexpected error: {e}") from e

    async def stream(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        """Stream completion tokens.

        Args:
            messages: List of message dicts
            **kwargs: Additional OpenAI parameters

        Yields:
            Completion tokens as they arrive
        """
        params = self._prepare_params(kwargs)
        params["stream"] = True

        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model, messages=messages, **params
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except openai.RateLimitError as e:
            raise RateLimitError(f"OpenAI rate limit exceeded: {e}") from e
        except openai.APITimeoutError as e:
            raise TimeoutError(f"OpenAI request timed out: {e}") from e
        except Exception as e:
            raise ProviderError(f"Streaming error: {e}") from e

    async def embed(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        """Generate embeddings using OpenAI API.

        Args:
            texts: List of texts to embed
            **kwargs: Additional parameters

        Returns:
            List of embedding vectors
        """
        # Use appropriate embedding model
        embed_model = kwargs.pop("model", "text-embedding-3-small")

        try:
            response = await self.async_client.embeddings.create(
                model=embed_model, input=texts, **kwargs
            )

            # Extract embeddings
            embeddings = [data.embedding for data in response.data]

            # Update metrics
            if response.usage:
                self._metrics["embedding_tokens"] = (
                    self._metrics.get("embedding_tokens", 0) + response.usage.total_tokens
                )

            return embeddings

        except Exception as e:
            raise ProviderError(f"Embedding error: {e}") from e

    def supports_streaming(self) -> bool:
        """OpenAI supports streaming."""
        return True

    def supports_structured_output(self) -> bool:
        """OpenAI supports structured output via response_format."""
        return True

    def supports_function_calling(self) -> bool:
        """OpenAI supports function calling."""
        return True

    def supports_vision(self) -> bool:
        """Check if current model supports vision."""
        # GPT-5 family (2025 models) - all support vision
        if self.model in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
            return True
        
        # GPT-4.1 family (2025 models) - all support vision
        if self.model in ["gpt-4.1", "gpt-4.1-preview", "gpt-4.1-mini"]:
            return True

        # GPT-4o and GPT-4 vision models
        vision_models = [
            "gpt-4-vision-preview",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
        ]

        return (
            self.model in vision_models
            or self.model.startswith("gpt-4o-")
            or self.model.startswith("gpt-4-turbo")
            or "vision" in self.model.lower()
        )

    def validate_content_types(self, messages: list[dict[str, Any]]) -> None:
        """Validate that the model supports the content types in messages.

        Args:
            messages: List of message dicts that may contain multimodal content

        Raises:
            ProviderError: If content type is not supported by the model
        """
        from ..core.signatures.types import Audio, Image

        has_images = False
        has_audio = False

        # Check all messages for multimodal content
        for message in messages:
            content = message.get("content")
            if isinstance(content, list):
                for item in content:
                    # Check direct Image/Audio objects
                    if isinstance(item, Image):
                        has_images = True
                    elif isinstance(item, Audio):
                        has_audio = True
                    # Check dict format (already converted)
                    elif isinstance(item, dict):
                        if item.get("type") == "image_url":
                            has_images = True
                        elif item.get("type") == "input_audio":
                            has_audio = True

        # Validate vision support
        if has_images and not self.supports_vision():
            raise ProviderError(
                f"Model {self.model} doesn't support vision/images. "
                f"Use a vision-capable model like gpt-4o, gpt-4-turbo, or gpt-4-vision-preview."
            )

        # Validate audio support
        if has_audio:
            audio_models = ["gpt-4o-audio-preview", "gpt-4o-audio"]
            model_lower = self.model.lower()

            supports_audio = False
            for am in audio_models:
                if model_lower == am or model_lower.startswith(am):
                    supports_audio = True
                    break

            if not supports_audio:
                raise ProviderError(
                    f"Model {self.model} doesn't support audio input. "
                    f"Use an audio-capable model like gpt-4o-audio-preview."
                )

    def _prepare_multimodal_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert messages with multimodal content to OpenAI format.

        Handles:
        - Image objects → image_url format
        - Audio objects → input_audio format (for supported models)
        - Mixed content arrays (text + images/audio)
        - Size validation (20MB limit for base64)

        Args:
            messages: List of messages potentially containing multimodal content

        Returns:
            Messages formatted for OpenAI API

        Raises:
            ProviderError: If content exceeds size limits or unsupported types
        """
        from ..core.signatures.types import Audio, History, Image

        formatted_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Handle string content (no conversion needed)
            if isinstance(content, str):
                formatted_messages.append({"role": role, "content": content})
                continue

            # Handle Image object
            if isinstance(content, Image):
                # Check size limit (20MB for base64)
                base64_size = len(content.to_base64())
                if base64_size > 20 * 1024 * 1024:  # 20MB
                    raise ProviderError(
                        f"Image size ({base64_size / 1024 / 1024:.1f}MB) exceeds OpenAI limit (20MB)"
                    )

                formatted_messages.append(
                    {
                        "role": role,
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": content.to_data_url(),
                                    "detail": getattr(content, "detail", "auto"),
                                },
                            }
                        ],
                    }
                )
                continue

            # Handle Audio object
            if isinstance(content, Audio):
                # Only certain models support audio
                audio_models = ["gpt-4o-audio-preview", "gpt-4o-2024-10-01"]
                if self.model not in audio_models and not self.model.startswith("gpt-4o-audio"):
                    raise ProviderError(
                        f"Model {self.model} doesn't support audio input. "
                        f"Use one of: {', '.join(audio_models)}"
                    )

                formatted_messages.append(
                    {
                        "role": role,
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": content.to_base64(),
                                    "format": content.format,
                                },
                            }
                        ],
                    }
                )
                continue

            # Handle History object
            if isinstance(content, History):
                # Convert History to messages and extend our list
                # History should not be content, it should be multiple messages
                raise ProviderError(
                    "History objects should be converted to messages before calling provider"
                )

            # Handle list of mixed content
            if isinstance(content, list):
                content_parts = []

                for item in content:
                    if isinstance(item, str):
                        content_parts.append({"type": "text", "text": item})
                    elif isinstance(item, Image):
                        # Check size
                        base64_size = len(item.to_base64())
                        if base64_size > 20 * 1024 * 1024:
                            raise ProviderError("Image size exceeds 20MB limit")

                        content_parts.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": item.to_data_url(),
                                    "detail": getattr(item, "detail", "auto"),
                                },
                            }
                        )
                    elif isinstance(item, Audio):
                        # Check model support
                        if not self.model.startswith("gpt-4o-audio"):
                            raise ProviderError(f"Model {self.model} doesn't support audio")

                        content_parts.append(
                            {
                                "type": "input_audio",
                                "input_audio": {"data": item.to_base64(), "format": item.format},
                            }
                        )
                    elif isinstance(item, dict):
                        # Already formatted content part
                        content_parts.append(item)
                    else:
                        # Convert to string as fallback
                        content_parts.append({"type": "text", "text": str(item)})

                formatted_messages.append({"role": role, "content": content_parts})
                continue

            # Fallback: convert to string
            formatted_messages.append({"role": role, "content": str(content)})

        return formatted_messages

    def get_param_specs(self) -> dict[str, Any]:
        """Get OpenAI-specific parameter specifications.

        OpenAI doesn't support top_k, so we exclude it from the standard specs.
        For o1 reasoning models, many parameters are not supported.
        """
        from ..core.parameters import STANDARD_PARAM_SPECS, ParamDomain, ParamSpec, ParamType

        specs = STANDARD_PARAM_SPECS.copy()

        # Remove top_k as OpenAI doesn't support it
        specs.pop("top_k", None)

        # For reasoning models, remove unsupported parameters
        if self._is_reasoning_model():
            unsupported = ["temperature", "top_p", "presence_penalty", "frequency_penalty"]
            for param in unsupported:
                specs.pop(param, None)

            # Add o1-specific parameters
            specs["max_completion_tokens"] = ParamSpec(
                name="max_completion_tokens",
                param_type=ParamType.INT,
                domain=ParamDomain.EFFICIENCY,
                description="Maximum completion tokens for o1 models",
                default=1000,
                range=(1, 100000),
            )

        return specs

    def _is_reasoning_model(self) -> bool:
        """Check if current model is an o1 reasoning model."""
        return self.model.startswith(("o1-", "o1-preview", "o1-mini"))

    def _prepare_params(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Prepare and validate parameters for OpenAI API.

        Args:
            kwargs: Raw parameters

        Returns:
            Cleaned parameters for API call
        """
        # Start with all kwargs (for special parameters like stop, system, etc.)
        params = dict(kwargs)

        # Clean and validate standard parameters using our parameter specs
        cleaned = self.clean_params(kwargs)
        params.update(cleaned)

        # Handle o1 reasoning models - they have special constraints
        if self._is_reasoning_model():
            # o1 models don't support temperature, top_p, etc.
            reasoning_unsupported = [
                "temperature",
                "top_p",
                "presence_penalty",
                "frequency_penalty",
            ]
            for param in reasoning_unsupported:
                params.pop(param, None)

            # o1 models require max_completion_tokens instead of max_tokens
            if "max_tokens" in params:
                params["max_completion_tokens"] = params.pop("max_tokens")

        # Handle special parameters

        # response_format for structured output
        if "response_format" in kwargs:
            response_format = kwargs["response_format"]
            if isinstance(response_format, type):
                # Convert Pydantic model to JSON schema
                params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_format.__name__,
                        "schema": response_format.model_json_schema(),
                    },
                }
            else:
                params["response_format"] = response_format

        # Tools/functions
        if "tools" in kwargs:
            params["tools"] = kwargs["tools"]
        if "tool_choice" in kwargs:
            params["tool_choice"] = kwargs["tool_choice"]

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        return params

    def _parse_completion(self, response: Any) -> Completion:
        """Parse OpenAI response into our Completion type.

        Args:
            response: OpenAI ChatCompletion response

        Returns:
            Completion object
        """
        # Extract text from first choice
        text = ""
        if response.choices:
            choice = response.choices[0]
            if choice.message.content:
                text = choice.message.content

            # Handle function calls
            if choice.message.tool_calls:
                # Include tool calls in metadata
                tool_calls = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in choice.message.tool_calls
                ]
                metadata = {"tool_calls": tool_calls}
            else:
                metadata = {}

            finish_reason = choice.finish_reason
        else:
            metadata = {}
            finish_reason = "unknown"

        # Parse usage
        usage = None
        if response.usage:
            # Get cached tokens if available
            cached_tokens = 0
            if hasattr(response.usage, "prompt_tokens_details"):
                details = response.usage.prompt_tokens_details
                if details and hasattr(details, "cached_tokens"):
                    cached_tokens = details.cached_tokens or 0

            tokens = TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                cached_tokens=cached_tokens,
            )
            
            # Calculate cost
            cost = self._calculate_cost(tokens)
            
            usage = Usage(
                tokens=tokens,
                cost=cost,
                provider=self.name,
                model=self.model,
            )

        return Completion(
            text=text,
            usage=usage or Usage(),
            metadata=metadata,
            finish_reason=finish_reason,
            model=response.model,
            provider=self.name,
        )

    def _calculate_cost(self, tokens: TokenUsage) -> float:
        """Calculate estimated cost based on token usage.

        OpenAI pricing (as of 2025):
        GPT-5 Family:
        - GPT-5 (Standard): $1.25/$10 per 1M tokens (input/output)
        - GPT-5 Mini: $0.25/$2 per 1M tokens
        - GPT-5 Nano: $0.05/$0.40 per 1M tokens
        
        GPT-4.1 Family:
        - GPT-4.1: $2.50/$10 per 1M tokens (estimated based on GPT-4 pricing)
        - GPT-4.1-mini: $0.15/$0.60 per 1M tokens (similar to GPT-4o-mini)
        - GPT-4.1-nano: $0.05/$0.20 per 1M tokens
        
        GPT-4o Family:
        - GPT-4o: $2.50/$10 per 1M tokens
        - GPT-4o-mini: $0.15/$0.60 per 1M tokens
        
        Legacy:
        - GPT-4-turbo: $10/$30 per 1M tokens
        - GPT-4: $30/$60 per 1M tokens
        - GPT-3.5-turbo: $0.50/$1.50 per 1M tokens
        """
        model_lower = self.model.lower()
        
        # GPT-5 Family (2025)
        if "gpt-5" in model_lower:
            if "nano" in model_lower:
                input_cost = tokens.input_tokens * 0.00000005  # $0.05 per 1M
                output_cost = tokens.output_tokens * 0.0000004  # $0.40 per 1M
            elif "mini" in model_lower:
                input_cost = tokens.input_tokens * 0.00000025  # $0.25 per 1M
                output_cost = tokens.output_tokens * 0.000002   # $2 per 1M
            else:  # Standard GPT-5
                input_cost = tokens.input_tokens * 0.00000125  # $1.25 per 1M
                output_cost = tokens.output_tokens * 0.00001    # $10 per 1M
        
        # GPT-4.1 Family (2025)
        elif "gpt-4.1" in model_lower:
            if "nano" in model_lower:
                input_cost = tokens.input_tokens * 0.00000005  # $0.05 per 1M
                output_cost = tokens.output_tokens * 0.0000002  # $0.20 per 1M
            elif "mini" in model_lower:
                input_cost = tokens.input_tokens * 0.00000015  # $0.15 per 1M
                output_cost = tokens.output_tokens * 0.0000006  # $0.60 per 1M
            else:  # Standard GPT-4.1
                input_cost = tokens.input_tokens * 0.0000025   # $2.50 per 1M
                output_cost = tokens.output_tokens * 0.00001    # $10 per 1M
        
        # GPT-4o Family
        elif "gpt-4o" in model_lower:
            if "mini" in model_lower:
                input_cost = tokens.input_tokens * 0.00000015  # $0.15 per 1M
                output_cost = tokens.output_tokens * 0.0000006  # $0.60 per 1M
            else:  # Standard GPT-4o
                input_cost = tokens.input_tokens * 0.0000025   # $2.50 per 1M
                output_cost = tokens.output_tokens * 0.00001    # $10 per 1M
        
        # GPT-4 Legacy
        elif "gpt-4-turbo" in model_lower:
            input_cost = tokens.input_tokens * 0.00001      # $10 per 1M
            output_cost = tokens.output_tokens * 0.00003    # $30 per 1M
        elif "gpt-4" in model_lower:
            input_cost = tokens.input_tokens * 0.00003      # $30 per 1M
            output_cost = tokens.output_tokens * 0.00006    # $60 per 1M
        
        # GPT-3.5
        elif "gpt-3.5" in model_lower:
            input_cost = tokens.input_tokens * 0.0000005    # $0.50 per 1M
            output_cost = tokens.output_tokens * 0.0000015  # $1.50 per 1M
        
        # O1 reasoning models (no official pricing yet, estimate similar to GPT-4)
        elif model_lower.startswith("o1"):
            input_cost = tokens.input_tokens * 0.00003      # Estimate $30 per 1M
            output_cost = tokens.output_tokens * 0.00006    # Estimate $60 per 1M
        
        # Default fallback (assume GPT-3.5 pricing)
        else:
            input_cost = tokens.input_tokens * 0.0000005    # $0.50 per 1M
            output_cost = tokens.output_tokens * 0.0000015  # $1.50 per 1M
        
        # Apply cached token discount (90% off for cached tokens)
        if tokens.cached_tokens > 0:
            # Cached tokens cost 10% of regular input tokens
            cached_cost = tokens.cached_tokens * 0.00000125 * 0.1  # 10% of regular cost
            # Adjust input cost to remove cached portion
            regular_input_tokens = tokens.input_tokens - tokens.cached_tokens
            if model_lower.startswith("gpt-5"):
                input_cost = regular_input_tokens * 0.00000125 + cached_cost
            elif model_lower.startswith("gpt-4"):
                input_cost = regular_input_tokens * 0.0000025 + cached_cost
        
        return input_cost + output_cost

    def _update_metrics(self, completion: Completion) -> None:
        """Update provider metrics from completion.

        Args:
            completion: Completion to extract metrics from
        """
        if completion.usage and completion.usage.tokens:
            tokens = completion.usage.tokens
            self._metrics["total_tokens"] = (
                self._metrics.get("total_tokens", 0) + tokens.total_tokens
            )
            self._metrics["input_tokens"] = (
                self._metrics.get("input_tokens", 0) + tokens.input_tokens
            )
            self._metrics["output_tokens"] = (
                self._metrics.get("output_tokens", 0) + tokens.output_tokens
            )

            if tokens.cached_tokens:
                self._metrics["cached_tokens"] = (
                    self._metrics.get("cached_tokens", 0) + tokens.cached_tokens
                )
            
            # Calculate and store cost
            cost = self._calculate_cost(tokens)
            self._metrics["total_cost"] = self._metrics.get("total_cost", 0) + cost

        self._metrics["total_calls"] = self._metrics.get("total_calls", 0) + 1

    async def create_structured_completion(
        self, messages: list[dict[str, str]], response_format: type, **kwargs: Any
    ) -> Any:
        """Create a completion with structured output.

        This is a convenience method for structured outputs using Pydantic models.

        Args:
            messages: List of message dicts
            response_format: Pydantic model class for response structure
            **kwargs: Additional parameters

        Returns:
            Instance of response_format model
        """
        # Add response format to kwargs
        kwargs["response_format"] = response_format

        # Get completion
        completion = await self.complete(messages, **kwargs)

        # Parse JSON response into model
        try:
            response_data = json.loads(completion.text)
            return response_format(**response_data)
        except (json.JSONDecodeError, ValueError) as e:
            raise ProviderError(f"Failed to parse structured output: {e}") from e


__all__ = ["OpenAIProvider"]

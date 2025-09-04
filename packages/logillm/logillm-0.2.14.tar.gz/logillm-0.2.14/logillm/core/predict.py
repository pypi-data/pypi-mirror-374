"""Predict module - the core execution engine."""

from __future__ import annotations

from typing import Any

from ..exceptions import ModuleError
from .adapters import Adapter, ChatAdapter, create_adapter
from .demos import Demo, DemoManager
from .modules import Module, Parameter
from .providers import Provider, get_provider
from .signatures import Signature, parse_signature_string
from .types import AdapterFormat, Configuration, Metadata, Prediction


class Predict(Module):
    """Core prediction module that orchestrates LLM calls."""

    def __init__(
        self,
        signature: Signature | str,
        *,
        provider: Provider | None = None,
        adapter: Adapter | AdapterFormat | str | None = None,
        max_demos: int = 5,
        config: Configuration | None = None,
        metadata: Metadata | None = None,
        debug: bool | None = None,
    ):
        """Initialize Predict module.

        Args:
            signature: Input/output specification
            provider: LLM provider (uses default if None)
            adapter: Format adapter (defaults to ChatAdapter)
            max_demos: Maximum number of demonstrations to keep
            config: Additional configuration
            metadata: Module metadata
            debug: Enable debug mode to capture prompts (overrides environment variable)
        """
        super().__init__(signature=signature, config=config, metadata=metadata, debug=debug)

        # Provider setup
        self.provider = provider

        # Adapter setup
        if adapter is None:
            self.adapter = ChatAdapter()
        elif isinstance(adapter, (AdapterFormat, str)):
            if isinstance(adapter, str):
                adapter = AdapterFormat(adapter)
            self.adapter = create_adapter(adapter)
        else:
            self.adapter = adapter

        # Demo management
        self.demo_manager = DemoManager(max_demos=max_demos)
        self.parameters["demos"] = Parameter(
            value=self.demo_manager, learnable=True, metadata={"type": "demonstrations"}
        )

    def add_demo(self, demo: Demo | dict[str, Any]) -> None:
        """Add a demonstration example."""
        self.demo_manager.add(demo)

    def add_demos(self, demos: list[Demo | dict[str, Any]]) -> None:
        """Add multiple demonstration examples."""
        for demo in demos:
            self.demo_manager.add(demo)

    def clear_demos(self) -> None:
        """Clear all demonstrations."""
        self.demo_manager.clear()

    async def forward(self, **inputs: Any) -> Prediction:
        """Execute the prediction.

        This orchestrates:
        1. Input validation
        2. Demo formatting
        3. Provider call
        4. Output parsing
        5. Trace capture
        """
        # Get provider (use default if not set)
        provider = self.provider or get_provider()

        # Validate inputs if signature available
        if self.signature:
            try:
                validated_inputs = self.signature.validate_inputs(**inputs)
            except Exception:
                # If validation fails, keep original inputs
                # This is important for dynamic signatures like in Avatar
                validated_inputs = inputs
        else:
            validated_inputs = inputs

        # Prepare demos for adapter
        demo_dicts = []
        for demo in self.demo_manager.get_best():
            demo_dicts.append(
                {
                    "inputs": demo.inputs,
                    "outputs": demo.outputs,
                }
            )

        # Format the prompt using adapter
        try:
            # Check if adapter.format is async
            import inspect

            if inspect.iscoroutinefunction(self.adapter.format):
                messages = await self.adapter.format(
                    signature=self.signature,
                    inputs=validated_inputs,
                    demos=demo_dicts,
                )
            else:
                messages = self.adapter.format(
                    signature=self.signature,
                    inputs=validated_inputs,
                    demos=demo_dicts,
                )
        except Exception as e:
            raise ModuleError(
                f"Adapter formatting failed: {e}",
                module_name="Predict",
                execution_stage="format",
                context={"inputs": validated_inputs},
            ) from e

        # Call the provider
        try:
            # Merge module config with call-time config
            provider_config = self.config.copy()
            provider_config.update(inputs.get("_config", {}))

            # Remove internal keys from provider config
            provider_config.pop("_config", None)
            provider_config.pop("_trace", None)

            completion = await provider.complete_with_retry(messages=messages, **provider_config)
        except Exception as e:
            raise ModuleError(
                f"Provider call failed: {e}",
                module_name="Predict",
                execution_stage="complete",
                context={"messages": messages},
            ) from e

        # Parse the output using adapter
        try:
            # Check if adapter.parse is async
            if inspect.iscoroutinefunction(self.adapter.parse):
                parsed_outputs = await self.adapter.parse(
                    self.signature,
                    completion.text,
                    inputs=validated_inputs,
                )
            else:
                parsed_outputs = self.adapter.parse(
                    self.signature,
                    completion.text,
                    inputs=validated_inputs,
                )
        except Exception:
            # If parsing fails, return raw text
            # Handle case where completion.text might be a coroutine (in tests)
            text = completion.text
            if inspect.iscoroutine(text):
                text = await text
            parsed_outputs = {"output": text}

        # Validate outputs if signature available
        # Note: Check parsed_outputs is not None, not just truthy (empty dict is falsy but valid)
        if self.signature and parsed_outputs is not None:
            try:
                validated_outputs = self.signature.validate_outputs(**parsed_outputs)
            except Exception:
                # If validation fails, keep parsed outputs
                validated_outputs = parsed_outputs
        else:
            validated_outputs = parsed_outputs if parsed_outputs is not None else {}

        # Create prediction with optional prompt capture
        metadata = {
            "provider": provider.name,
            "model": provider.model,
            "adapter": self.adapter.format_type.value,
            "demos_used": len(demo_dicts),
            **self.metadata,
        }

        # Capture debug information if debug mode is enabled
        prompt_info = None
        request_info = None
        response_info = None

        if self._debug_mode:
            # Capture prompt information (existing functionality)
            prompt_info = {
                "messages": messages,
                "adapter": self.adapter.format_type.value,
                "demos_count": len(demo_dicts),
                "provider": provider.name,
                "model": provider.model,
            }
            # Also add to metadata for backwards compatibility
            metadata["prompt"] = messages

            # Capture complete request payload
            request_info = {
                "messages": messages,
                "provider": provider.name,
                "model": provider.model,
                "adapter": self.adapter.format_type.value,
                "demos_count": len(demo_dicts),
                "provider_config": provider_config,
                "timestamp": completion.usage.timestamp.isoformat()
                if completion.usage and completion.usage.timestamp
                else None,
            }

            # Capture complete response data
            response_info = {
                "text": completion.text,
                "usage": {
                    "input_tokens": completion.usage.tokens.input_tokens
                    if completion.usage and completion.usage.tokens
                    else 0,
                    "output_tokens": completion.usage.tokens.output_tokens
                    if completion.usage and completion.usage.tokens
                    else 0,
                    "cached_tokens": completion.usage.tokens.cached_tokens
                    if completion.usage and completion.usage.tokens
                    else 0,
                    "reasoning_tokens": completion.usage.tokens.reasoning_tokens
                    if completion.usage and completion.usage.tokens
                    else 0,
                    "total_tokens": completion.usage.tokens.total_tokens
                    if completion.usage and completion.usage.tokens
                    else 0,
                }
                if completion.usage and completion.usage.tokens
                else {},
                "cost": completion.usage.cost if completion.usage else None,
                "latency": completion.usage.latency if completion.usage else None,
                "finish_reason": completion.finish_reason,
                "model": completion.model,
                "provider": completion.provider,
                "metadata": completion.metadata,
                "timestamp": completion.usage.timestamp.isoformat()
                if completion.usage and completion.usage.timestamp
                else None,
            }

        prediction = Prediction(
            outputs=validated_outputs,
            usage=completion.usage,
            metadata=metadata,
            success=True,
            prompt=prompt_info,
            request=request_info,
            response=response_info,
        )

        return prediction

    def compile(self, optimizer: Any | None = None) -> Predict:
        """Compile the module for optimization."""
        compiled = super().compile(optimizer)

        # Copy demos to compiled version
        if isinstance(compiled, Predict):
            compiled.demo_manager.from_list(self.demo_manager.to_list())

        return compiled

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        data = super().to_dict()
        data.update(
            {
                "adapter_type": self.adapter.format_type.value,
                "max_demos": self.demo_manager.max_demos,
                "demos": self.demo_manager.to_list(),
            }
        )
        if self.provider:
            data["provider"] = {
                "name": self.provider.name,
                "model": self.provider.model,
            }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Predict:
        """Deserialize from dictionary."""
        # Extract Predict-specific data
        adapter_type = data.pop("adapter_type", "chat")
        max_demos = data.pop("max_demos", 5)
        demos = data.pop("demos", [])
        data.pop("provider", None)

        # Reconstruct signature if it's a dict
        from .signatures import BaseSignature

        signature_data = data.get("signature")
        if isinstance(signature_data, dict):
            signature = BaseSignature.from_dict(signature_data)
        else:
            signature = signature_data

        # Create instance
        instance = cls(
            signature=signature,
            adapter=adapter_type,
            max_demos=max_demos,
            config=data.get("config", {}),
            metadata=data.get("metadata", {}),
        )

        # Restore demos
        instance.demo_manager.from_list(demos)

        # Note: Provider would need to be restored separately
        # as we don't serialize the full provider instance

        return instance


class ChainOfThought(Predict):
    """Chain of Thought module - adds reasoning before the answer."""

    def __init__(self, signature: Signature | str, reasoning_field: str = "reasoning", **kwargs):
        """Initialize ChainOfThought module.

        Args:
            signature: Input/output specification
            reasoning_field: Name of the reasoning field to add
            **kwargs: Additional arguments for Predict
        """
        # Parse signature if it's a string
        if isinstance(signature, str):
            parsed_sig = parse_signature_string(signature)
            signature = parsed_sig  # type: ignore[assignment] # Now signature is BaseSignature, not str

        # Add reasoning field to signature
        from .signatures import BaseSignature, FieldSpec
        from .types import FieldType

        # Create new output fields with reasoning
        new_output_fields = {
            reasoning_field: FieldSpec(
                name=reasoning_field,
                field_type=FieldType.OUTPUT,
                python_type=str,
                description="Let's think step by step to solve this problem.",
                required=True,
            )
        }

        # Add original output fields after reasoning
        # Convert all fields to FieldSpec for consistency
        if signature and hasattr(signature, "output_fields"):
            for field_name, field_spec in signature.output_fields.items():  # type: ignore[attr-defined]
                # Handle both BaseSignature FieldSpec and EnhancedSignature FieldInfo
                if hasattr(field_spec, "python_type"):
                    # BaseSignature FieldSpec - already in correct format
                    if field_spec.python_type is float and not field_spec.description:
                        # Add a description to help the model output decimals
                        from .signatures import FieldSpec

                        enhanced_spec = FieldSpec(
                            name=field_spec.name,
                            field_type=field_spec.field_type,
                            python_type=field_spec.python_type,
                            description="Provide the numeric answer as a decimal value",
                            required=field_spec.required,
                        )
                        new_output_fields[field_name] = enhanced_spec
                    else:
                        new_output_fields[field_name] = field_spec
                elif hasattr(field_spec, "annotation"):
                    # EnhancedSignature FieldInfo (Pydantic) - convert to FieldSpec
                    from .signatures import FieldSpec
                    from .types import FieldType
                    
                    # Extract description from json_schema_extra if available
                    desc = ""
                    if hasattr(field_spec, "json_schema_extra") and field_spec.json_schema_extra:
                        desc = field_spec.json_schema_extra.get("desc", "")
                    
                    # Create FieldSpec with proper type information
                    new_spec = FieldSpec(
                        name=field_name,
                        field_type=FieldType.OUTPUT,
                        python_type=field_spec.annotation,
                        description=desc or f"The {field_name}",
                        required=getattr(field_spec, "is_required", lambda: True)() if callable(getattr(field_spec, "is_required", None)) else True,
                    )
                    new_output_fields[field_name] = new_spec
                else:
                    # Unknown field type, pass through
                    new_output_fields[field_name] = field_spec

        # Create modified signature
        modified_signature = BaseSignature(
            input_fields=signature.input_fields
            if signature and hasattr(signature, "input_fields")
            else {},  # type: ignore[attr-defined]
            output_fields=new_output_fields,
            instructions=signature.instructions
            if signature and hasattr(signature, "instructions")
            else None,  # type: ignore[attr-defined]
            metadata=getattr(signature, "metadata", {}) if signature else {},
        )

        # Increase max_tokens for ChainOfThought since we're adding reasoning
        # Default is 4000, we bump it to 6000 for CoT unless user specified
        if 'config' not in kwargs:
            kwargs['config'] = {}
        if 'max_tokens' not in kwargs['config']:
            kwargs['config']['max_tokens'] = 6000  # More space for reasoning + outputs
        
        super().__init__(signature=modified_signature, **kwargs)
        self.reasoning_field = reasoning_field

    async def forward(self, **inputs: Any) -> Prediction:
        """Execute with chain of thought reasoning."""
        # Call parent forward
        prediction = await super().forward(**inputs)

        # The reasoning is already in the outputs due to our modified signature
        # We could do additional processing here if needed

        return prediction


__all__ = [
    "Predict",
    "ChainOfThought",
]

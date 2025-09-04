import json
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class FunctionCall:
    name: str
    arguments: dict[str, Any]
    call_id: str | None = None


@dataclass
class LLMResponse:
    content: str
    finish_reason: str = "stop"
    usage: dict[str, int] | None = None
    function_calls: list[FunctionCall] | None = None
    model: str | None = None


@dataclass
class ChatMessage:
    role: str  # system, user, agent, function
    content: str | list[dict[str, Any]]  # Support both text and structured content (for vision)
    function_call: FunctionCall | None = None
    function_calls: list[FunctionCall] | None = None  # For parallel function calling
    name: str | None = None  # For function responses


@dataclass
class LLMManagerResponse:
    """Response from LLM Manager with optional completion signaling."""

    content: str
    completed: bool = False
    completion_data: dict[str, Any] | None = None


class BaseLLMService(ABC):
    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        pass

    async def chat_complete(self, messages: list[ChatMessage], **kwargs) -> LLMResponse:
        """Public method with logging that calls the provider implementation."""
        logger.info(
            "Making LLM chat completion request",
            provider=self.name,
            model=self.config.get("model", "unknown"),
            message_count=len(messages),
            temperature=kwargs.get("temperature", self.config.get("temperature")),
            max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens")),
        )

        response = await self._chat_complete_impl(messages, **kwargs)

        logger.info(
            "Received LLM chat completion response",
            provider=self.name,
            model=response.model or self.config.get("model", "unknown"),
            finish_reason=response.finish_reason,
            content_length=len(response.content) if response.content else 0,
            prompt_tokens=response.usage.get("prompt_tokens") if response.usage else None,
            completion_tokens=response.usage.get("completion_tokens") if response.usage else None,
            total_tokens=response.usage.get("total_tokens") if response.usage else None,
        )
        return response

    @abstractmethod
    async def _chat_complete_impl(self, messages: list[ChatMessage], **kwargs) -> LLMResponse:
        """Provider-specific implementation of chat completion."""
        pass

    async def stream_chat_complete(self, messages: list[ChatMessage], **kwargs):
        """Public method with logging that calls the provider streaming implementation."""
        logger.info(
            "Making LLM streaming chat completion request",
            provider=self.name,
            model=self.config.get("model", "unknown"),
            message_count=len(messages),
            temperature=kwargs.get("temperature", self.config.get("temperature")),
            max_tokens=kwargs.get("max_tokens", self.config.get("max_tokens")),
        )

        async for chunk in self._stream_chat_complete_impl(messages, **kwargs):
            yield chunk

    @abstractmethod
    async def _stream_chat_complete_impl(self, messages: list[ChatMessage], **kwargs) -> AsyncIterator[str]:
        """Provider-specific implementation of streaming chat completion."""
        # This should be an async generator that yields string chunks
        if False:  # pragma: no cover
            yield  # This makes it a generator for type checking
        raise NotImplementedError

    async def embed(self, text: str) -> list[float]:
        try:
            return await self._embed_impl(text)
        except NotImplementedError:
            raise NotImplementedError(f"Provider {self.name} does not support embeddings") from None

    async def _embed_impl(self, text: str) -> list[float]:
        raise NotImplementedError("Embeddings not implemented for this provider")

    # Function calling support
    async def chat_complete_with_functions(
        self, messages: list[ChatMessage], functions: list[dict[str, Any]], **kwargs
    ) -> LLMResponse:
        try:
            # Try native function calling first
            return await self._chat_complete_with_functions_native(messages, functions, **kwargs)
        except (NotImplementedError, Exception) as e:
            # Fallback to prompt-based function calling
            logger.debug(f"Native function calling failed, using prompt-based fallback: {e}")
            return await self._chat_complete_with_functions_prompt(messages, functions, **kwargs)

    async def _chat_complete_with_functions_native(
        self, messages: list[ChatMessage], functions: list[dict[str, Any]], **kwargs
    ) -> LLMResponse:
        raise NotImplementedError("Native function calling not implemented for this provider")

    async def _chat_complete_with_functions_prompt(
        self, messages: list[ChatMessage], functions: list[dict[str, Any]], **kwargs
    ) -> LLMResponse:
        # Build function descriptions
        function_descriptions = []
        for func in functions:
            func_desc = f"- {func['name']}: {func['description']}"
            if "parameters" in func:
                params = func["parameters"].get("properties", {})
                param_list = ", ".join(
                    f"{name} ({info.get('type', 'any')}): {info.get('description', '')}"
                    for name, info in params.items()
                )
                func_desc += f"\n  Parameters: {param_list}"
            function_descriptions.append(func_desc)

        # Enhanced system message with function information
        function_descriptions_text = "\n".join(function_descriptions)
        function_prompt = f"""Available functions:
{function_descriptions_text}

To use a function, respond with:
FUNCTION_CALL: function_name(param1="value1", param2="value2")

You can call multiple functions by using multiple FUNCTION_CALL lines.
After function calls, provide a natural response based on the results."""

        # Add function information to the conversation
        enhanced_messages = messages.copy()
        if enhanced_messages and enhanced_messages[0].role == "system":
            if isinstance(enhanced_messages[0].content, str):
                enhanced_messages[0].content += f"\n\n{function_prompt}"
            else:
                # If content is a list (structured content), append as text content
                enhanced_messages[0].content.append({"type": "text", "text": f"\n\n{function_prompt}"})
        else:
            enhanced_messages.insert(0, ChatMessage(role="system", content=function_prompt))

        response = await self._chat_complete_impl(enhanced_messages, **kwargs)

        # Parse function calls from response
        if "FUNCTION_CALL:" in response.content:
            function_calls = self._parse_function_calls(response.content)
            response.function_calls = function_calls

        return response

    def _parse_function_calls(self, content: str) -> list[FunctionCall]:
        import re

        function_calls = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("FUNCTION_CALL:"):
                function_call = line.replace("FUNCTION_CALL:", "").strip()
                try:
                    # Extract function name and parameters
                    match = re.match(r"(\w+)\((.*)\)", function_call)
                    if match:
                        function_name, params_str = match.groups()

                        # Parse parameters (simplified)
                        params = {}
                        if params_str:
                            param_pairs = params_str.split(",")
                            for pair in param_pairs:
                                if "=" in pair:
                                    key, value = pair.split("=", 1)
                                    key = key.strip().strip('"')
                                    value = value.strip().strip('"')
                                    params[key] = value

                        function_calls.append(FunctionCall(name=function_name, arguments=params))
                except Exception as e:
                    logger.warning(f"Failed to parse function call: {function_call}, error: {e}")

        return function_calls

    # Utility methods
    def _messages_to_prompt(self, messages: list[ChatMessage]) -> str:
        prompt_parts = []
        for msg in messages:
            role = msg.role
            content = msg.content
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "agent":
                prompt_parts.append(f"Agent: {content}")
            elif role == "function":
                prompt_parts.append(f"Function {msg.name}: {content}")

        prompt_parts.append("Agent:")
        return "\n\n".join(prompt_parts)

    def _chat_message_to_dict(self, message: ChatMessage) -> dict[str, Any]:
        msg_dict = {"role": message.role, "content": message.content}

        if message.function_call:
            msg_dict["function_call"] = {
                "name": message.function_call.name,
                "arguments": json.dumps(message.function_call.arguments),
            }

        if message.function_calls:
            msg_dict["function_calls"] = [
                {"name": fc.name, "arguments": json.dumps(fc.arguments), "id": fc.call_id}
                for fc in message.function_calls
            ]

        if message.name:
            msg_dict["name"] = message.name

        return msg_dict

    def _dict_to_chat_message(self, msg_dict: dict[str, Any]) -> ChatMessage:
        message = ChatMessage(role=msg_dict.get("role", "assistant"), content=msg_dict.get("content", ""))

        if "function_call" in msg_dict:
            fc = msg_dict["function_call"]
            message.function_call = FunctionCall(
                name=fc["name"],
                arguments=json.loads(fc["arguments"]) if isinstance(fc["arguments"], str) else fc["arguments"],
            )

        if "function_calls" in msg_dict:
            message.function_calls = [
                FunctionCall(
                    name=fc["name"],
                    arguments=json.loads(fc["arguments"]) if isinstance(fc["arguments"], str) else fc["arguments"],
                    call_id=fc.get("id"),
                )
                for fc in msg_dict["function_calls"]
            ]

        if "name" in msg_dict:
            message.name = msg_dict["name"]

        return message

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def get_model_info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.__class__.__name__,
            "model": self.config.get("model", "unknown"),
            "initialized": self.is_initialized,
        }


class LLMProviderError(Exception):
    pass


class LLMProviderConfigError(LLMProviderError):
    pass


class LLMProviderAPIError(LLMProviderError):
    pass

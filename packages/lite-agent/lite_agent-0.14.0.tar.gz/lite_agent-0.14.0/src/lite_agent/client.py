import abc
import os
from typing import Any, Literal, NotRequired, TypedDict

import litellm
from openai.types.chat import ChatCompletionToolParam
from openai.types.responses import FunctionToolParam
from pydantic import BaseModel

ReasoningEffort = Literal["minimal", "low", "medium", "high"]


class ThinkingConfigDict(TypedDict):
    """Thinking configuration for reasoning models like Claude."""

    type: Literal["enabled"]  # 启用推理
    budget_tokens: NotRequired[int]  # 推理令牌预算，可选


class ReasoningEffortDict(TypedDict):
    """Reasoning effort configuration."""

    effort: ReasoningEffort


ThinkingConfig = ThinkingConfigDict | None

# 统一的推理配置类型
ReasoningConfig = (
    ReasoningEffort  # "minimal", "low", "medium", "high"
    | ReasoningEffortDict  # {"effort": "minimal"}
    | ThinkingConfigDict  # {"type": "enabled", "budget_tokens": 2048}
    | bool  # True/False 简单开关
    | None  # 不启用推理
)


class LLMConfig(BaseModel):
    """LLM generation parameters configuration."""

    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    stop: list[str] | str | None = None


def parse_reasoning_config(reasoning: ReasoningConfig) -> tuple[ReasoningEffort | None, ThinkingConfig]:
    """
    解析统一的推理配置，返回 reasoning_effort 和 thinking_config。

    Args:
        reasoning: 统一的推理配置
            - ReasoningEffort: "minimal", "low", "medium", "high" -> reasoning_effort
            - ReasoningEffortDict: {"effort": "minimal"} -> reasoning_effort
            - ThinkingConfigDict: {"type": "enabled", "budget_tokens": 2048} -> thinking_config
            - bool: True -> "medium", False -> None
            - None: 不启用推理

    Returns:
        tuple: (reasoning_effort, thinking_config)
    """
    if reasoning is None:
        return None, None

    if isinstance(reasoning, str) and reasoning in ("minimal", "low", "medium", "high"):
        return reasoning, None  # type: ignore[return-value]

    if isinstance(reasoning, bool):
        return ("medium", None) if reasoning else (None, None)

    if isinstance(reasoning, dict):
        return _parse_dict_reasoning_config(reasoning)

    # 其他类型或无效格式，默认不启用
    return None, None


def _parse_dict_reasoning_config(reasoning: ReasoningEffortDict | ThinkingConfigDict | dict[str, Any]) -> tuple[ReasoningEffort | None, ThinkingConfig]:
    """解析字典格式的推理配置。"""
    # 检查是否为 {"effort": "value"} 格式 (ReasoningEffortDict)
    if "effort" in reasoning and len(reasoning) == 1:
        effort = reasoning["effort"]
        if isinstance(effort, str) and effort in ("minimal", "low", "medium", "high"):
            return effort, None  # type: ignore[return-value]

    # 检查是否为 ThinkingConfigDict 格式
    if "type" in reasoning and reasoning.get("type") == "enabled":
        # 验证 ThinkingConfigDict 的结构
        valid_keys = {"type", "budget_tokens"}
        if all(key in valid_keys for key in reasoning):
            return None, reasoning  # type: ignore[return-value]

    # 其他未知字典格式，仍尝试作为 thinking_config
    return None, reasoning  # type: ignore[return-value]


class BaseLLMClient(abc.ABC):
    """Base class for LLM clients."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        api_base: str | None = None,
        api_version: str | None = None,
        reasoning: ReasoningConfig = None,
        llm_config: LLMConfig | None = None,
        **llm_params: Any,  # noqa: ANN401
    ):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.api_version = api_version

        # 处理 LLM 生成参数
        if llm_config is not None:
            self.llm_config = llm_config
        else:
            # 从 **llm_params 创建配置
            self.llm_config = LLMConfig(**llm_params)

        # 处理推理配置
        self.reasoning_effort: ReasoningEffort | None
        self.thinking_config: ThinkingConfig
        self.reasoning_effort, self.thinking_config = parse_reasoning_config(reasoning)

    @abc.abstractmethod
    async def completion(
        self,
        messages: list[Any],
        tools: list[ChatCompletionToolParam] | None = None,
        tool_choice: str = "auto",
        reasoning: ReasoningConfig = None,
        *,
        streaming: bool = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Perform a completion request to the LLM."""

    @abc.abstractmethod
    async def responses(
        self,
        messages: list[dict[str, Any]],  # Changed from ResponseInputParam
        tools: list[FunctionToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"] = "auto",
        reasoning: ReasoningConfig = None,
        *,
        streaming: bool = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Perform a response request to the LLM."""


class LiteLLMClient(BaseLLMClient):
    def _resolve_reasoning_params(
        self,
        reasoning: ReasoningConfig,
    ) -> tuple[ReasoningEffort | None, ThinkingConfig]:
        """解析推理配置参数。"""
        if reasoning is not None:
            return parse_reasoning_config(reasoning)

        # 使用实例默认值
        return self.reasoning_effort, self.thinking_config

    async def completion(
        self,
        messages: list[Any],
        tools: list[ChatCompletionToolParam] | None = None,
        tool_choice: str = "auto",
        reasoning: ReasoningConfig = None,
        *,
        streaming: bool = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Perform a completion request to the Litellm API."""

        # 处理推理配置参数
        final_reasoning_effort, final_thinking_config = self._resolve_reasoning_params(
            reasoning,
        )

        # Prepare completion parameters
        completion_params = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "api_version": self.api_version,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "stream": streaming,
            **kwargs,
        }

        # Add LLM generation parameters if specified
        if self.llm_config.temperature is not None:
            completion_params["temperature"] = self.llm_config.temperature
        if self.llm_config.max_tokens is not None:
            completion_params["max_tokens"] = self.llm_config.max_tokens
        if self.llm_config.top_p is not None:
            completion_params["top_p"] = self.llm_config.top_p
        if self.llm_config.frequency_penalty is not None:
            completion_params["frequency_penalty"] = self.llm_config.frequency_penalty
        if self.llm_config.presence_penalty is not None:
            completion_params["presence_penalty"] = self.llm_config.presence_penalty
        if self.llm_config.stop is not None:
            completion_params["stop"] = self.llm_config.stop

        # Add reasoning parameters if specified
        if final_reasoning_effort is not None:
            completion_params["reasoning_effort"] = final_reasoning_effort
        if final_thinking_config is not None:
            completion_params["thinking"] = final_thinking_config

        return await litellm.acompletion(**completion_params)

    async def responses(
        self,
        messages: list[dict[str, Any]],  # Changed from ResponseInputParam
        tools: list[FunctionToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"] = "auto",
        reasoning: ReasoningConfig = None,
        *,
        streaming: bool = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # type: ignore[return]  # noqa: ANN401
        """Perform a response request to the Litellm API."""

        os.environ["DISABLE_AIOHTTP_TRANSPORT"] = "True"

        # 处理推理配置参数
        final_reasoning_effort, final_thinking_config = self._resolve_reasoning_params(
            reasoning,
        )

        # Prepare response parameters
        response_params = {
            "model": self.model,
            "input": messages,  # type: ignore[arg-type]
            "tools": tools,
            "tool_choice": tool_choice,
            "api_version": self.api_version,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "stream": streaming,
            "store": False,
            **kwargs,
        }

        # Add LLM generation parameters if specified
        if self.llm_config.temperature is not None:
            response_params["temperature"] = self.llm_config.temperature
        if self.llm_config.max_tokens is not None:
            response_params["max_tokens"] = self.llm_config.max_tokens
        if self.llm_config.top_p is not None:
            response_params["top_p"] = self.llm_config.top_p
        if self.llm_config.frequency_penalty is not None:
            response_params["frequency_penalty"] = self.llm_config.frequency_penalty
        if self.llm_config.presence_penalty is not None:
            response_params["presence_penalty"] = self.llm_config.presence_penalty
        if self.llm_config.stop is not None:
            response_params["stop"] = self.llm_config.stop

        # Add reasoning parameters if specified
        if final_reasoning_effort is not None:
            response_params["reasoning"] = {"effort": final_reasoning_effort}
        if final_thinking_config is not None:
            response_params["thinking"] = final_thinking_config
        return await litellm.aresponses(**response_params)  # type: ignore[return-value]

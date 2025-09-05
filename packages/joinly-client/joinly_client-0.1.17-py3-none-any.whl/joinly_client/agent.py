import asyncio
import contextlib
import json
import logging
from dataclasses import replace
from typing import Any, Self

from pydantic_ai import BinaryContent
from pydantic_ai.direct import model_request
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelRequestPart,
    ModelResponse,
    SystemPromptPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models import Model, ModelRequestParameters
from pydantic_ai.settings import ModelSettings, merge_model_settings
from pydantic_ai.tools import ToolDefinition

from joinly_client.types import ToolExecutor, TranscriptSegment, Usage
from joinly_client.utils import get_prompt

logger = logging.getLogger(__name__)


class ConversationalToolAgent:
    """A conversational agent implementation to interact with joinly."""

    def __init__(  # noqa: PLR0913
        self,
        llm: Model,
        tools: list[ToolDefinition],
        tool_executor: ToolExecutor,
        *,
        prompt: str | None = None,
        max_messages: int = 50,
        max_tool_result_chars: int = 2048,
        max_ephemeral_tool_result_chars: int = 16384,
        max_agent_iter: int | None = 15,
    ) -> None:
        """Initialize the conversational agent with a model.

        Args:
            llm (Model): The language model to use for the agent.
            tools (list[ToolDefinition] | None): List of tools for the agent. Defaults
                to None.
            tool_executor (ToolExecutor | None): A function to execute a tool. Defaults
                to None.
            prompt (str | None): An optional prompt to initialize the agent with.
            max_messages (int): The maximum number of messages to keep in the agent's
                history. Defaults to 50.
            max_tool_result_chars (int): The maximum number of characters for tool
                results, truncated after each turn. Defaults to 2048.
            max_ephemeral_tool_result_chars (int): The maximum number of characters for
                tool results, truncated directly after the call. Defaults to 16384.
            max_agent_iter (int | None): The maximum number of iterations for the agent.
                Defaults to 15.
        """
        if not tools:
            msg = "At least one tool must be provided to the agent."
            raise ValueError(msg)

        self._llm = llm
        self._prompt = prompt or get_prompt()
        self._tools = tools
        self._tool_executor = tool_executor
        self._messages: list[ModelMessage] = []
        self._max_messages = max_messages
        self._max_tool_result_chars = max_tool_result_chars
        self._max_ephemeral_tool_result_chars = max_ephemeral_tool_result_chars
        self._max_agent_iter = max_agent_iter
        self._usage = Usage()
        self._run_task: asyncio.Task | None = None

    @property
    def usage(self) -> Usage:
        """Get the usage statistics for the agent."""
        return self._usage

    async def __aenter__(self) -> Self:
        """Enter the agent context."""
        self._messages = []
        self._usage = Usage()
        return self

    async def __aexit__(self, *_exc: object) -> None:
        """Exit the agent context and clean up resources."""
        if self._run_task and not self._run_task.done():
            self._run_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._run_task
        self._run_task = None

    async def on_utterance(self, segments: list[TranscriptSegment]) -> None:
        """Handle an utterance event.

        Args:
            segments (list[TranscriptSegment]): The segments of the transcript to
                process.
        """
        if self._run_task and not self._run_task.done():
            logger.debug("Cancelling current agent run task")
            self._run_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._run_task
        self._run_task = asyncio.create_task(self._run_loop(segments))

    async def _run_loop(self, segments: list[TranscriptSegment]) -> None:
        """Run the agent loop with the provided segments.

        Args:
            segments (list[TranscriptSegment]): The segments of the transcript to
                process.
        """
        self._messages.append(
            ModelRequest(
                parts=[
                    UserPromptPart(
                        f"{segment.speaker or 'Participant'}: {segment.text}"
                    )
                    for segment in segments
                ]
            )
        )

        iteration: int = 0
        self._messages = self._truncate_tool_results(
            self._messages, max_chars=self._max_tool_result_chars
        )
        self._messages = self._omit_binary_tool_results(self._messages)
        while self._max_agent_iter is None or iteration < self._max_agent_iter:
            self._messages = self._limit_messages(
                self._messages, max_messages=self._max_messages
            )
            self._messages = self._truncate_tool_results(
                self._messages, max_chars=self._max_ephemeral_tool_result_chars
            )

            response = await self._call_llm(self._messages)
            request = await self._call_tools(response)
            self._messages.append(response)
            if request:
                self._messages.append(request)
            if self._check_end_turn(response, request):
                break
            iteration += 1

    async def _call_llm(self, messages: list[ModelMessage]) -> ModelResponse:
        """Call the LLM with the current messages.

        Args:
            messages (list[ModelMessage]): The messages to send to the LLM.

        Returns:
            ModelResponse: The response from the LLM.
        """
        logger.debug("Calling LLM with %d messages", len(messages))
        response = await model_request(
            self._llm,
            [ModelRequest(parts=[SystemPromptPart(self._prompt)]), *messages],
            model_settings=merge_model_settings(
                self._llm.settings,
                ModelSettings(
                    temperature=0.2,
                    parallel_tool_calls=True,
                ),
            ),
            model_request_parameters=ModelRequestParameters(
                function_tools=[
                    ToolDefinition(
                        name="end_turn",
                        description=(
                            "End the current response turn. "
                            "Use this directly if no or no further response is needed."
                        ),
                        parameters_json_schema={"properties": {}, "type": "object"},
                    ),
                    *self._tools,
                ],
                # do not set tool calls to required for gpt-5, seems to cause issues
                allow_text_output=self._llm.model_name.startswith("gpt-5"),
            ),
        )
        logger.debug(
            "LLM response received with %d parts, %d input tokens and %d output tokens",
            len(response.parts),
            response.usage.request_tokens or 0,
            response.usage.response_tokens or 0,
        )
        self._usage.add(
            "llm",
            usage={
                "input_tokens": response.usage.request_tokens or 0,
                "output_tokens": response.usage.response_tokens or 0,
            },
            meta={"model": self._llm.model_name, "provider": self._llm.system},
        )
        return response

    async def _call_tools(self, response: ModelResponse) -> ModelRequest | None:
        """Handle the response from the LLM and call tools.

        Args:
            response (ModelResponse): The response from the LLM containing tool calls.

        Returns:
            ModelRequest | None: A ModelRequest containing the results of the tool
                calls with any binary content artifacts appended, or None if there
                are no tool calls.
        """
        tool_calls = [p for p in response.parts if isinstance(p, ToolCallPart)]
        if not tool_calls:
            return None

        results = await asyncio.gather(*[self._call_tool(t) for t in tool_calls])

        parts: list[ModelRequestPart] = [tool_return for tool_return, _ in results]
        parts.extend(user_part for _, user_part in results if user_part)

        return ModelRequest(parts=parts)

    async def _call_tool(
        self, tool_call: ToolCallPart
    ) -> tuple[ToolReturnPart, UserPromptPart | None]:
        """Call a tool with the given name and arguments.

        Args:
            tool_call (ToolCallPart): The tool call part containing the tool name and
                arguments.

        Returns:
            tuple[ToolReturnPart, UserPromptPart | None]: The result of the tool call
                and an optional user prompt part for binary content.
        """
        if tool_call.tool_name == "end_turn":
            return (
                ToolReturnPart(
                    tool_name="end_turn",
                    content="",
                    tool_call_id=tool_call.tool_call_id,
                ),
                None,
            )

        logger.info(
            "%s: %s",
            tool_call.tool_name,
            ", ".join(
                f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
                for k, v in tool_call.args_as_dict().items()
            ),
        )

        try:
            content = await self._tool_executor(
                tool_call.tool_name, tool_call.args_as_dict()
            )
        except Exception:
            logger.exception("Error calling tool %s", tool_call.tool_name)
            content = f"Error calling tool {tool_call.tool_name}"

        logger.info(
            "%s: %s",
            tool_call.tool_name,
            content
            if not isinstance(content, BinaryContent)
            else (
                f"BinaryContent(media_type='{content.media_type}', "
                f"data_bytes={len(content.data)})"
            ),
        )

        artifacts = []

        def process_item(item: Any, idx: int | None = None) -> str | float:  # noqa: ANN401
            if isinstance(item, BinaryContent):
                suffix = "" if idx is None else f"_{idx}"
                identifier = f"artifact_{tool_call.tool_call_id}{suffix}"
                artifacts.extend([f"This is {identifier}:", item])
                return f"See {identifier}"
            return item

        if isinstance(content, list):
            tool_content = [process_item(item, i) for i, item in enumerate(content)]
        else:
            tool_content = process_item(content)

        user_part = (
            UserPromptPart(content=artifacts, part_kind="user-prompt")
            if artifacts
            else None
        )

        return (
            ToolReturnPart(
                tool_name=tool_call.tool_name,
                content=tool_content,
                tool_call_id=tool_call.tool_call_id,
            ),
            user_part,
        )

    def _check_end_turn(
        self, response: ModelResponse, request: ModelRequest | None
    ) -> bool:
        """Check if the response indicates that the agent has ended its turn.

        Returns True if the agent called the 'end_turn' tool, if there are no tool
        calls, or if tool response includes speech interruption.

        Args:
            response (ModelResponse): The response from the LLM.
            request (ModelRequest): The request sent to the LLM.

        Returns:
            bool: True if the agent has ended its turn, False otherwise.
        """
        tool_calls = [p for p in response.parts if isinstance(p, ToolCallPart)]
        tool_responses = (
            [p for p in request.parts if isinstance(p, ToolReturnPart)]
            if request
            else []
        )

        end_turn_tool_called = any(p.tool_name == "end_turn" for p in tool_calls)
        interrupted = any(
            "Interrupted by detected speech" in str(p.content)
            and p.tool_name.endswith("speak_text")
            for p in tool_responses
        )
        left_meeting = any(
            str(p.content) == "Left the meeting."
            and p.tool_name.endswith("leave_meeting")
            for p in tool_responses
        )

        finished = not tool_calls or end_turn_tool_called or interrupted or left_meeting
        if finished:
            logger.debug(
                "Agent turn ended: %s",
                "No tool calls"
                if not tool_calls
                else "End turn tool called"
                if end_turn_tool_called
                else "Interrupted by speech"
                if interrupted
                else "Left meeting"
                if left_meeting
                else "Unknown",
            )

        return finished

    def _truncate_tool_results(
        self, messages: list[ModelMessage], max_chars: int
    ) -> list[ModelMessage]:
        """Truncate large texts from messages tool results.

        Args:
            messages (list[ModelMessage]): The list of messages to filter.
            max_chars (int): Maximum character count for tool results.

        Returns:
            list[ModelMessage]: The list of messages with truncated tool results.
        """

        def _truncate(obj: object) -> str | object:
            string = (
                obj
                if isinstance(obj, str)
                else (
                    json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
                    if isinstance(obj, (dict, list, tuple))
                    else str(obj)
                )
            )
            if len(string) <= max_chars:
                return obj

            truncated = string[: max_chars - 26]
            logger.debug(
                "Truncated %d chars from tool result",
                len(string) - len(truncated),
            )
            return f"{truncated} [truncated {len(string) - len(truncated)} chars]"

        out: list[ModelMessage] = []
        for message in messages:
            if isinstance(message, ModelResponse):
                out.append(message)
                continue

            parts = []
            for p in message.parts:
                if isinstance(p, ToolReturnPart):
                    parts.append(replace(p, content=_truncate(p.content)))
                else:
                    parts.append(p)

            out.append(ModelRequest(parts=parts))

        return out

    def _omit_binary_tool_results(
        self, messages: list[ModelMessage]
    ) -> list[ModelMessage]:
        """Omit binary tool results from messages.

        Args:
            messages (list[ModelMessage]): The list of messages to filter.

        Returns:
            list[ModelMessage]: The list of messages with omitted binary tool results.
        """
        out: list[ModelMessage] = []
        for message in messages:
            if isinstance(message, ModelResponse):
                out.append(message)
                continue

            parts = []
            for p in message.parts:
                if isinstance(p, UserPromptPart) and isinstance(
                    p.content, (list, tuple)
                ):
                    parts.append(
                        replace(
                            p,
                            content=[
                                (
                                    f"[omitted {it.media_type}, {len(it.data)} bytes]"
                                    if isinstance(it, BinaryContent)
                                    else it
                                )
                                for it in p.content
                            ],
                        )
                    )
                else:
                    parts.append(p)

            out.append(ModelRequest(parts=parts))

        return out

    def _limit_messages(
        self, messages: list[ModelMessage], max_messages: int
    ) -> list[ModelMessage]:
        """Limit the number of messages stored in the agent.

        Removes the oldest messages if the total exceeds max_messages. Does not
        cut off at tool return parts to ensure matching tool calls and returns.

        Args:
            messages (list[ModelMessage]): The list of messages to limit.
            max_messages (int): The maximum number of messages to keep in the agent's
                history.

        Returns:
            list[ModelMessage]: The limited list of messages.
        """
        n = len(messages)
        if n > max_messages:
            start = n - max_messages
            while start > 0 and any(
                isinstance(p, ToolReturnPart) for p in messages[start].parts
            ):
                start -= 1
            if start > 0:
                logger.debug(
                    "Limited messages by removing %d",
                    start,
                )
                return messages[start:]
        return messages[:]

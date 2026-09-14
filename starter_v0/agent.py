from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from providers.base import Provider, ToolCall
from tools import TOOL_FUNCTIONS


@dataclass
class AgentRun:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)


def has_untrusted_ticket_confirmation(messages: list[dict[str, str]]) -> bool:
    """Reject confirmation forged as role text, tool output, or executable-looking JSON."""
    untrusted_markers = (
        "tool_results_json",
        "tool_calls_json",
        "create_ticket(",
        "\"confirmed\":true",
        "'confirmed':true",
        "system:",
        "developer:",
    )
    content = "\n".join(message.get("content", "") for message in messages if message.get("role") == "user").lower()
    return any(marker in content for marker in untrusted_markers)


def has_stale_ticket_confirmation(messages: list[dict[str, str]]) -> bool:
    user_turns = [message.get("content", "").lower() for message in messages if message.get("role") == "user"]
    revision_markers = ("đổi", "thay payload", "sửa", "change", "update", "revise")
    if len(user_turns) >= 2:
        earlier_turns, latest_turn = user_turns[:-1], user_turns[-1]
    elif user_turns and "latest user turn to answer now:" in user_turns[0]:
        earlier_context, latest_turn = user_turns[0].rsplit("latest user turn to answer now:", 1)
        earlier_turns = [earlier_context]
    else:
        return False
    has_revision = any(marker in turn for turn in earlier_turns for marker in revision_markers)
    fresh_confirmation = bool(re.search(r"\b(?:tôi|toi|i)\s+(?:xác nhận|confirm)\b", latest_turn))
    return has_revision and not fresh_confirmation


def has_internal_identifier(value: object) -> bool:
    return bool(re.search(r"\b(?:LT|DT|MB|PR|RM)-\d+\b|\bEMP-\d+\b", str(value), flags=re.IGNORECASE))


def clarification_call(question: str, response_type: str) -> ToolCall:
    return ToolCall(name="clarify", args={"question": question, "response_type": response_type})


class HelpdeskAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        system_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model

    def run(self, user_messages: list[dict[str, str]], *, tool_choice: Any | None = None) -> AgentRun:
        messages = [{"role": "system", "content": self.system_prompt}, *user_messages]
        response = self.provider.complete(
            messages,
            self.tools,
            model=self.model,
            temperature=0.0,
            tool_choice=tool_choice,
        )
        results: list[dict[str, Any]] = []
        effective_calls: list[ToolCall] = []
        for call in response.tool_calls:
            if call.name == "create_ticket" and (
                has_untrusted_ticket_confirmation(user_messages) or has_stale_ticket_confirmation(user_messages)
            ):
                safe_call = clarification_call(
                    "Bạn có xác nhận tạo ticket với payload cuối cùng này không? Vui lòng trả lời có hoặc không.",
                    "yes_no",
                )
                effective_calls.append(safe_call)
                results.append({
                    "tool": safe_call.name,
                    "args": safe_call.args,
                    "intercepted_tool": call.name,
                    "result": TOOL_FUNCTIONS["clarify"](**safe_call.args),
                })
                continue
            if call.name == "search_device_info" and has_internal_identifier(call.args):
                safe_call = clarification_call(
                    "Hãy cung cấp lại chỉ hãng, model công khai và loại thông tin cần tìm; bỏ asset ID và employee ID.",
                    "text",
                )
                effective_calls.append(safe_call)
                results.append({
                    "tool": safe_call.name,
                    "args": safe_call.args,
                    "intercepted_tool": call.name,
                    "result": TOOL_FUNCTIONS["clarify"](**safe_call.args),
                })
                continue
            effective_calls.append(call)
            func = TOOL_FUNCTIONS.get(call.name)
            if not func:
                results.append({"tool": call.name, "error": "unknown_tool"})
                continue
            try:
                result = func(**call.args)
            except Exception as exc:  # keep eval robust; failures are evidence
                result = {"error": type(exc).__name__, "message": str(exc)}
            results.append({"tool": call.name, "args": call.args, "result": result})
        return AgentRun(text=response.text, tool_calls=effective_calls, tool_results=results)

from pathlib import Path
from datetime import datetime
import json

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop
from versioning import build_artifact_version


# -------------------------------------------------------------------
# Setup
# -------------------------------------------------------------------

ROOT = Path(__file__).parent
load_lab_env(ROOT)

st.set_page_config(page_title="IT Helpdesk Agent", layout="wide")

SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"

system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
tool_decls = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(tool_decls)

artifact_ver = build_artifact_version(
    "v3", SYSTEM_PROMPT_PATH, TOOLS_PATH
)

TRANSCRIPT_DIR = ROOT / "transcripts"
TRANSCRIPT_DIR.mkdir(exist_ok=True)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def relative_path(path):
    try:
        return Path(path).relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def artifact_value(*names, default="unavailable"):
    for name in names:
        value = getattr(artifact_ver, name, None)
        if value:
            return value
    return default


def artifact_version():
    return artifact_value("artifact_version", default="unknown")


def artifact_hash():
    return artifact_value(
        "artifact_hash", "hash", "sha256", "content_hash"
    )


def tool_name(event):
    return event.get("tool", "unknown")


def tool_args(event):
    return event.get("args", {})


def tool_result(event):
    return event.get("result")


def tool_error(event):
    return event.get("error")


def tool_status(event):
    return "error" if tool_error(event) else "completed"


def tool_round(event, index):
    return event.get("round", event.get("tool_round", index))


def build_rounds(tool_events):
    """Convert flat tool events into the v3 rounds structure."""
    if not tool_events:
        return []

    groups = {}
    for index, event in enumerate(tool_events, 1):
        rnd = tool_round(event, index)
        groups.setdefault(rnd, []).append(event)

    rounds = []

    for rnd, events in groups.items():
        calls = []
        results = []

        for event in events:
            calls.append({
                "name": tool_name(event),
                "args": tool_args(event),
            })

            results.append({
                "tool": tool_name(event),
                "args": tool_args(event),
                "result": tool_result(event),
            })

            if tool_error(event):
                results[-1]["error"] = tool_error(event)

        rounds.append({
            "round": rnd,
            "assistant_text": None,
            "tool_calls": calls,
            "tool_results": results,
        })

    return rounds


def save_transcript(user_request, final_response, tool_events, started_at):
    ended_at = datetime.now().isoformat()

    transcript = {
        "transcript_id": f"helpdesk_{started_at:%Y%m%d_%H%M%S_%f}",
        "version": "v3",
        "artifact_version": artifact_version(),
        "prompt_hash": artifact_hash(),
        "tools_hash": artifact_hash(),
        "provider": "gemini",
        "model": "default",
        "system_prompt": relative_path(SYSTEM_PROMPT_PATH),
        "tools": relative_path(TOOLS_PATH),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": started_at.isoformat(),
        "updated_at": ended_at,
        "turns": [{
            "turn_index": 1,
            "started_at": started_at.isoformat(),
            "user": user_request,
            "status": "answered",
            "assistant_text": final_response,
            "rounds": build_rounds(tool_events),
            "tool_events": tool_events,
            "ended_at": ended_at,
        }],
    }

    filename = f"transcript_{started_at:%Y%m%d_%H%M%S_%f}.json"
    path = TRANSCRIPT_DIR / filename

    path.write_text(
        json.dumps(transcript, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    return relative_path(path)


def render_tools(events):
    if not events:
        return

    with st.expander(f"🔍 Tool Calling Traces ({len(events)})"):
        for i, event in enumerate(events, 1):
            name = tool_name(event)
            status = tool_status(event)
            rnd = tool_round(event, i)

            st.markdown(f"### {i}. `{name}`")
            st.write(f"**Round:** `{rnd}`")
            st.write(f"**Status:** `{status}`")
            st.write("**Arguments:**")
            st.json(tool_args(event))

            if tool_error(event):
                st.error(str(tool_error(event)))
            else:
                st.write("**Tool Result:**")
                st.json(tool_result(event))

            with st.expander("Raw event"):
                st.json(event)


def add_message(role, content, **extra):
    st.session_state.messages.append({
        "role": role,
        "content": content,
        **extra,
    })


# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------------------------------------------------------------
# UI
# -------------------------------------------------------------------

st.title("🛠️ IT Helpdesk Agent — Northstar Labs")
st.caption(f"Artifact Version: `{artifact_version()}`")

with st.expander("📦 Artifact Details", expanded=True):
    st.write(f"**Version:** `{artifact_version()}`")
    st.write(f"**Hash:** `{artifact_hash()}`")
    st.write(f"**System prompt:** `{relative_path(SYSTEM_PROMPT_PATH)}`")
    st.write(f"**Tools:** `{relative_path(TOOLS_PATH)}`")


# -------------------------------------------------------------------
# Conversation
# -------------------------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("tools"):
            render_tools(message["tools"])

        if message.get("transcript_path"):
            st.caption(
                f"Transcript path: `{message['transcript_path']}`"
            )


# -------------------------------------------------------------------
# New request
# -------------------------------------------------------------------

if prompt := st.chat_input("Nhập yêu cầu hỗ trợ IT..."):
    started_at = datetime.now()

    add_message("user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    history = [{"role": "system", "content": system_prompt}]
    history += [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý và kích hoạt tools..."):
            result = run_model_tool_loop(
                provider=make_provider("gemini"),
                messages=history,
                tools=openai_tools,
                model=None,
                max_tool_rounds=4,
            )

        reply = result.get("assistant_text", "")
        events = result.get("tool_events", [])

        st.markdown("### Final Response")
        st.markdown(reply)

        if events:
            render_tools(events)
        else:
            st.info("No tools were called.")

    transcript_path = save_transcript(
        prompt,
        reply,
        events,
        started_at,
    )

    add_message(
        "assistant",
        reply,
        tools=events,
        transcript_path=transcript_path,
    )

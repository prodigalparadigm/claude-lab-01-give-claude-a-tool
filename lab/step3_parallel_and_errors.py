"""Step 3 — Parallel calls, then a graceful error.

One question about two policies produces TWO tool_use blocks in one turn.
Return both results in ONE user message — splitting them across messages
trains Claude out of parallel calls. Then ask about a policy that doesn't
exist and watch the error come back as an explanation, not an invention.
"""
import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

POLICY_TOOL = {
    "name": "get_policy_status",
    "description": (
        "Look up the current status of a life insurance policy by policy number. "
        "Returns status (active/lapsed/pending), insured name, premium due date, "
        "and face amount. Use this whenever a user asks about a specific policy. "
        "Policy numbers look like LIC-12345."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "policy_number": {"type": "string", "description": "e.g. LIC-48213"}
        },
        "required": ["policy_number"],
        "additionalProperties": False,
    },
    "strict": True,
}

POLICIES = json.loads((Path(__file__).parent / "policies.json").read_text())


def get_policy_status(policy_number: str) -> str:
    record = POLICIES.get(policy_number.strip().upper())
    return json.dumps(record) if record else f"Error: no policy {policy_number}"


def run(question: str) -> None:
    print(f"\n--- {question}")
    messages = [{"role": "user", "content": question}]
    while True:
        response = client.messages.create(
            model=MODEL, max_tokens=2048, tools=[POLICY_TOOL], messages=messages
        )
        print("stop_reason:", response.stop_reason)
        if response.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print("Claude called:", block.name, block.input)
                result = get_policy_status(**block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                        "is_error": result.startswith("Error:"),
                    }
                )
        messages.append({"role": "user", "content": tool_results})
    print()
    print(next(b.text for b in response.content if b.type == "text"))


run("Compare policies LIC-48213 and LIC-77102 — which one needs attention first?")
run("What about policy LIC-00000?")

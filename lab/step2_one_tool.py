"""Step 2 — One tool, the loop exposed. This file is the lesson.

Three things to read before you run it: the tool definition (especially the
description), the local function it maps to, and the loop. Claude never runs
your code — it asks; you execute; you send the result back.
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


messages = [{"role": "user", "content": "What's the status of policy LIC-48213?"}]

while True:
    response = client.messages.create(
        model=MODEL, max_tokens=2048, tools=[POLICY_TOOL], messages=messages
    )
    print("stop_reason:", response.stop_reason)          # <- watch this change

    if response.stop_reason != "tool_use":
        break

    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print("Claude called:", block.name, block.input)   # <- and this
            result = get_policy_status(**block.input)
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": result}
            )
    messages.append({"role": "user", "content": tool_results})

print()
print(next(b.text for b in response.content if b.type == "text"))

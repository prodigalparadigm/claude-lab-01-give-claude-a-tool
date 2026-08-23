"""Step 4 — The SDK helper. Same tool, loop gone.

Now that you've traced the loop by hand once, here's how you'd build it for
real: decorate a plain function, hand it to the tool runner, and the SDK
drives request -> tool_use -> tool_result -> answer for you.

The runner is BETA in the Python SDK (client.beta.messages.tool_runner as of
anthropic 1.0.0) — say so when you demo it; accuracy is part of the brand.
"""
import json
import os
from pathlib import Path

import anthropic
from anthropic import beta_tool
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

POLICIES = json.loads((Path(__file__).parent / "policies.json").read_text())


@beta_tool
def get_policy_status(policy_number: str) -> str:
    """Look up the current status of a life insurance policy by policy number.
    Returns status (active/lapsed/pending), insured name, premium due date, and
    face amount. Use this whenever a user asks about a specific policy.
    Policy numbers look like LIC-12345.

    Args:
        policy_number: e.g. LIC-48213
    """
    record = POLICIES.get(policy_number.strip().upper())
    return json.dumps(record) if record else f"Error: no policy {policy_number}"


runner = client.beta.messages.tool_runner(
    model=MODEL,
    max_tokens=2048,
    tools=[get_policy_status],
    messages=[{"role": "user", "content": "Is policy LIC-90031 in good standing?"}],
)

for message in runner:
    print("stop_reason:", message.stop_reason)

print()
print(next(b.text for b in message.content if b.type == "text"))

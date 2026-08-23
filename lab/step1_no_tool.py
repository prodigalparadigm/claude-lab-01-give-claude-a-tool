"""Step 1 — The baseline. No tools. Claude cannot see your policy system.

Watch what it does when asked anyway: the good outcome is a clear "I can't
look that up," not a confident guess.
"""
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

response = client.messages.create(
    model=MODEL,
    max_tokens=2048,
    messages=[{"role": "user", "content": "What's the status of policy LIC-48213?"}],
)

print("stop_reason:", response.stop_reason)
print()
print(next(b.text for b in response.content if b.type == "text"))

# Maintenance — release-cycle checklist

A lab is only true on the day it was verified. This unit was authored and verified
on **2026-08-23** with the versions below. Re-verify on **every model release and
every SDK minor**, and after any edit to the scripts.

## Pinned surface

| Thing | Pinned at | Where |
|---|---|---|
| Python SDK | `anthropic==1.0.0` | `lab/requirements.txt` |
| Model (default) | `claude-sonnet-5` | `ANTHROPIC_MODEL` env override in every script |
| Model (verified alternate) | `claude-opus-5` | identical trace shape, ~2.5× price |
| Tool runner path | `client.beta.messages.tool_runner` — **beta** | `lab/step4_tool_runner.py` |
| dotenv | `python-dotenv==1.1.1` | `lab/requirements.txt` |

## The five-item checklist

1. **`python check.py` passes** — four PASS lines, from a *fresh* venv
   (`rm -rf .venv` first; a stale venv hides pin drift).
2. **The Step 2 trace still prints the same three lines** —
   `stop_reason: tool_use` → `Claude called: …` → `stop_reason: end_turn`.
   If a new model surfaces additional block types in the printed output, update
   the guide's transcript blocks and slide 4 of the deck to match what the
   terminal actually prints. The terminal is the source of truth, not the deck.
3. **Step 3 still produces two `tool_use` blocks in one assistant turn** for the
   compare question, and the unknown-policy path still returns
   `is_error: True` with a graceful, non-invented answer.
4. **The tool-runner import path hasn't moved.** It is beta; beta surfaces move.
   If `client.beta.messages.tool_runner` graduates or is renamed, update
   `step4_tool_runner.py`, the guide's Step 4 note, and this table.
5. **Bump the deck footer** (version, date, `anthropic` version, model) and
   re-export the PDF. The footer is this file in miniature; keep them agreeing.

## Known behaviors to preserve on purpose

- **Exercise 2b's two-stage degradation** is load-bearing: with only the
  description's format sentence deleted, the model recovers the `LIC-` prefix from
  the *property* example; with both deleted, it passes the bare number and the
  lookup errors. If a future model stops recovering in stage one, that's not a
  bug — update the guide's observed output and teach the new behavior. The lesson
  ("Claude reads every description field") survives either way.
- `policies.json` is loaded **relative to the script's own path**, never the
  working directory. This is the #1 way labs break on someone else's laptop;
  don't "simplify" it away.
- Scripts stay at one screen. If an edit makes one scroll, the edit is wrong.

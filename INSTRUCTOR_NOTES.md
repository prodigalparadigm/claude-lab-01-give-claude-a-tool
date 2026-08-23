# Instructor Notes — Lab 01: Give Claude a Tool

## The one rule

**Run `python check.py` before every class, full stop.** Four PASS lines in under a
minute means the room is safe. Anything red gets fixed before students arrive, not
discovered with twenty people watching. The check hits the live API with the same
scripts the students will run, so a green check is a rehearsal, not a hope.

## Timing (45-minute room)

| Block | Minutes | Watch for |
|---|---|---|
| Step 0 — setup | 5 (+10 buffer) | Budget the buffer every time. Anyone still red at minute 5 follows along with `sample_output/` — nobody sits idle. |
| Step 1 — baseline | 3 | Don't rush the discussion beat. "This is the good outcome — why?" sets up everything. |
| Step 2 — the loop | 10 | Make them read the description *before* running. Make them say the trace out loud. |
| Exercises 2a/2b | in Step 2 | 2b is the highest-value five minutes in the lab; protect it. |
| Step 3 — parallel + errors | 7 | Point at the two `Claude called:` lines. Then the error answer. |
| Step 4 — runner | 5 | One message: "now that you've traced it, here's the helper — and it's beta, say so." |
| Wrap | 5 | Question 3 is the discovery conversation. Let it run long if it's working. |

## The three most likely failures, and the fix for each

1. **`AuthenticationError` / 401.** The key isn't in `.env`, has a stray space, or the
   `.env` file is in the wrong directory (it belongs in `lab/`, next to the scripts).
   Fix: re-copy `.env.example`, paste the key directly after `=`, no quotes.
2. **`ModuleNotFoundError: anthropic`.** The venv isn't activated, or they installed
   into system Python. Fix: `source .venv/bin/activate` (Windows:
   `.venv\Scripts\activate`) and re-run; or call `.venv/bin/python` explicitly.
3. **Connection errors on corporate networks.** Some proxies block `api.anthropic.com`.
   Fix: phone hotspot for the session, or teach from `sample_output/` — every step's
   real transcript is there for exactly this reason. The lab is teachable through a
   full API outage.

## Cost

`check.py` end to end is one full pass of all four steps and measured about
$0.03–$0.05 on `claude-sonnet-5` during authoring. Budget **$0.25 per student** for
the session including exercise re-runs; a room of 20 is a five-dollar class.

## Model notes

Default is `claude-sonnet-5`, overridable per-machine with the `ANTHROPIC_MODEL`
environment variable — no code edits. `claude-opus-5` was run against Steps 1–2
during authoring and produces the **identical trace shape** (same `stop_reason`
sequence; no extra block types surface in the printed output) at roughly 2.5× the
price. There is no classroom reason to pay it; there is also no harm if a student's
org defaults to it. Both models ship with thinking enabled by default — the lab's
printed traces already reflect that, so what students see is what these scripts show.

## Discussion prompts that have worked

- After Step 1: *"Who has had a customer ask 'will it make things up about our
  data?' What did you say?"* Then: *"By the end of the hour you'll answer it in code."*
- After Exercise 2b: *"Notice the failure wasn't in Python. The code never changed.
  What changed?"* (The description. Descriptions are the product.)
- After Step 3's error: *"This is what you show the customer who asks about bad
  data. What's the equivalent 'LIC-00000' in their world?"*

## What not to do

Don't add a second tool, a web UI, or a framework mid-class, even if the room is
fast — every addition is a new way it breaks in front of them. Fast rooms get more
time on the wrap questions, which is where the selling actually happens.

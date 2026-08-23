# Lab 01 — Give Claude a Tool

A 30-minute hands-on lab for GTM teams — SEs, CSMs, AEs — on Claude tool use:
what a tool is, when Claude calls one, how the request → `tool_use` →
`tool_result` → answer loop works, and why the description is the part that
matters. The scenario is a tiny life-insurance policy lookup against a local
JSON file, which makes it a live answer to the first question every enterprise
buyer asks: *will it make things up about our data?* After the hour, a
participant can trace the loop, demo parallel calls and a graceful error, and
name what they'd tune first when a tool misfires.

## Run it in a room

```bash
cd lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # paste an API key after the =
python check.py          # four PASS lines or you don't teach yet
```

**Run `check.py` before every class.** It executes all four steps against the
live API in under a minute and prints one PASS/FAIL line per step. And
`lab/sample_output/` holds the captured real transcript of every step, so the
lab is teachable during an API outage or to a student whose key isn't working —
nobody sits idle.

## What's in here

```
LAB_GUIDE.md            the student-facing lab (the main artifact)
INSTRUCTOR_NOTES.md     timing, the three likely failures + fixes, cost, prompts
MAINTENANCE.md          the release-cycle checklist and pinned versions
deck/lab01_deck.pdf     6–8 instructor slides; cues, not a lecture
video/                  5-minute narrated walkthrough (link in this README)
lab/
  requirements.txt      pinned: anthropic==1.0.0, python-dotenv==1.1.1
  .env.example          ANTHROPIC_API_KEY=
  policies.json         six fake policies — the "system of record"
  step1_no_tool.py      baseline: no tool → Claude declines rather than guesses
  step2_one_tool.py     the manual loop, exposed — the teaching artifact
  step3_parallel_and_errors.py   two calls in one turn; a graceful is_error
  step4_tool_runner.py  the SDK's beta tool runner — the loop, productized
  check.py              pre-class smoke test: four steps, PASS/FAIL, <60s
  sample_output/        real captured transcripts of every step
```

## How this unit was built

Sources: the Claude Docs tool-use and strict-tool-use pages and the Python SDK
README, checked against the live docs on 2026-08-22/23. Every script, both
guide exercises, and both models' trace shapes were **verified by live runs on
2026-08-23** in a fresh Linux venv that had never seen the repo; the transcripts
in `lab/sample_output/` and every observed-output block in the guide are pasted
from those runs, not written from memory. Versions are pinned in
`lab/requirements.txt`; the default model is `claude-sonnet-5` with
`claude-opus-5` verified as producing the identical trace.

## Maintenance

A lab is only true on the day it was verified. `MAINTENANCE.md` carries the
five-item release-cycle checklist — fresh-venv `check.py`, the Step 2 trace, the
Step 3 parallel-and-error behavior, the beta tool-runner import path, the deck
footer — with the pinned surface in one table. The job isn't building a lab
once; it's keeping forty of them true.

## Authorship

Kathleen Bartin · Prodigal Paradigm LLC · August 2026 — built with Claude. The
co-byline is the house standard, not small print. Case study and contact:
[prodigalparadigm.com](https://www.prodigalparadigm.com) ·
[linkedin.com/in/kathleen-bartin](https://www.linkedin.com/in/kathleen-bartin)

## License

MIT. Copyright (c) 2026 Kathleen Bartin.

# Lab 01 — Give Claude a Tool

**Audience:** GTM — SEs, CSMs, AEs who need to understand and demo tool use to enterprise customers.
**Time:** 30 minutes hands-on; 45 with discussion.
**You need:** Python 3.10+, an Anthropic API key, a terminal. No prior coding experience assumed — every command you need is written out.

## What you'll be able to do afterward

1. Explain, in one sentence, what a "tool" is to Claude and what it is not.
2. Read a tool definition (name / description / `input_schema`) and predict when Claude will call it.
3. Trace the request → `tool_use` → `tool_result` → final-answer loop, and name the `stop_reason` at each step.
4. Demo parallel tool calls and a graceful tool error to a customer.
5. Explain why the *description* is the part that matters most — and show what breaks when it's wrong.

The scenario is a tiny life-insurance policy-status tool: six fake policies in a local JSON file. Claude can look up a policy, and *only* a policy. This is the smallest possible version of the question every enterprise buyer asks first: **"will it make things up about our data?"** By the end of this lab you can answer that live, in code, in under a minute.

---

## Step 0 — Setup (5 minutes)

```bash
cd lab
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then paste your API key after the = sign
python check.py
```

Expect four green lines:

```
PASS  step1_no_tool.py  (5.6s)
PASS  step2_one_tool.py  (4.6s)
PASS  step3_parallel_and_errors.py  (10.4s)
PASS  step4_tool_runner.py  (5.1s)
```

Anything red at minute five: raise a hand, keep going with the transcripts in `sample_output/` — they are the exact output of these scripts, captured from real runs, so nobody sits idle.

---

## Step 1 — The baseline (3 minutes)

```bash
python step1_no_tool.py
```

This asks Claude *"What's the status of policy LIC-48213?"* with **no tools**. What you'll see:

```
stop_reason: end_turn

I don't have access to any policy database, customer records, or external
systems—so I can't look up policy LIC-48213 ... I have no information about
this specific policy and want to be upfront about that rather than guess.
```

**Discussion — this is the good outcome. Why?** Because the alternative is a confident guess. A model with no access to your systems *saying so* is the floor every enterprise deployment stands on. Everything that follows is about raising the ceiling without breaking that floor.

---

## Step 2 — One tool, the loop exposed (10 minutes)

Open `step2_one_tool.py` and read three things **before** running it.

**First, the tool definition.** A tool is a *description plus a schema* that you hand to Claude. That's all it is:

```python
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
```

**Second, the local function it maps to.** It reads `policies.json` — our stand-in for a customer's system of record — and returns a JSON string, or an error string for unknown numbers. Note what this means: **Claude never runs this function. You do.** Claude can only *ask*.

**Third, the loop.** Written out by hand on purpose, because the loop *is* the lesson: send the question with the tool attached; if Claude stops with `tool_use`, run the function it asked for, send the result back, and go around again; when it stops with `end_turn`, print the answer.

Now run it:

```bash
python step2_one_tool.py
```

```
stop_reason: tool_use
Claude called: get_policy_status {'policy_number': 'LIC-48213'}
stop_reason: end_turn

Here are the details for policy LIC-48213:
- Status: Active
- Insured Name: Avery Chen
- Face Amount: $500,000
- Next Premium Due Date: September 15, 2026
```

**That three-line trace is the whole unit.** Say the sequence out loud before moving on: *Claude stopped to ask → my code ran the lookup → Claude answered from the result.* Same question as Step 1; the difference between "I can't see your systems" and a grounded answer is one tool definition and eleven lines of loop.

### Exercise 2a — When does Claude *not* call the tool?

Change the user message to `"Hi, how are you?"` and re-run. Observed result:

```
stop_reason: end_turn
```

No tool call. Claude had the tool available and left it alone. **How did it know?** The description. It says the tool is for "when a user asks about a specific policy," and nobody did. The description isn't documentation for humans — it's the operating instructions Claude actually follows.

### Exercise 2b — Break the description, watch the input degrade

The format hint lives in **two places**: the last sentence of the description ("Policy numbers look like LIC-12345") and the property description ("e.g. LIC-48213"). Delete the last sentence only, ask about `"policy 48213"` (no LIC prefix), and re-run — observed: Claude *still* sends `LIC-48213`, because the property example carried the format. Now delete the property example too and re-run. Observed:

```
stop_reason: tool_use
Claude called: get_policy_status {'policy_number': '48213'}
```

The bare number goes through, the lookup fails, and Claude has to recover from an error that better writing would have prevented. Two lessons in one: Claude reads *every* description field you give it, and **descriptions are the product** — when a tool gets called at the wrong time or with the wrong shape, the description is what you tune first, not the code.

Put both hints back before Step 3.

---

## Step 3 — Parallel calls and errors (7 minutes)

```bash
python step3_parallel_and_errors.py
```

**First question:** *"Compare policies LIC-48213 and LIC-77102 — which one needs attention first?"* Observed:

```
stop_reason: tool_use
Claude called: get_policy_status {'policy_number': 'LIC-48213'}
Claude called: get_policy_status {'policy_number': 'LIC-77102'}
stop_reason: end_turn
```

**Two** tool calls in one turn. The loop returns both results in **one** user message — look at the code and notice that. Splitting results across messages trains Claude out of parallel calls; keeping them together is the habit. The answer that follows is a comparison table and a judgment: the lapsed policy first, with the reason.

**Second question:** *"What about policy LIC-00000?"* The function returns `Error: no policy LIC-00000` and the loop marks the result `"is_error": True`. Observed: Claude explains the number isn't on file, suggests it may be a typo, and shows the expected format — **it does not invent a policy.**

**Discussion:** this is the demo for the customer who asks *"and what happens when your data is wrong?"* The honest answer, live: the error comes back as an explanation, not a hallucination, because the tool result — not the model's imagination — is the source of truth.

---

## Step 4 — The SDK helper (5 minutes)

```bash
python step4_tool_runner.py
```

Same tool, written as a decorated Python function — the description now lives in the docstring — handed to `client.beta.messages.tool_runner(...)`. The loop is gone; the SDK drives it. Observed: the same two `stop_reason` lines, then the answer.

Now that you've traced the loop by hand once, this is how you'd build it for real — **but you can only debug what you've traced.** When the runner misbehaves in a customer's environment, Step 2 is the mental model you fall back on. (The runner is **beta** in the Python SDK — `client.beta.messages.tool_runner` as of `anthropic` 1.0.0. Say so when you demo it; accuracy is part of the brand.)

---

## Wrap (5 minutes) — three questions for the room

1. What's the one thing Claude cannot do without a tool?
2. Which part of the tool definition would you change first if Claude called it at the wrong time?
3. What would you put in a tool for *your* customer's system of record?

That last one isn't rhetorical — it's the discovery conversation. A customer describing what their `get_policy_status` equivalent would be is a customer describing their integration, their data boundary, and their first use case, in their own words.

"""Pre-class smoke test. Run this before every class, full stop.

Executes steps 1-4 against the live API and prints one PASS/FAIL line per
step. Green means the room is safe; red means fix it before students arrive.
Expected runtime: under 60 seconds.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent

CHECKS = [
    ("step1_no_tool.py", ["stop_reason: end_turn"], ["Claude called:"]),
    ("step2_one_tool.py",
     ["stop_reason: tool_use", "Claude called: get_policy_status", "stop_reason: end_turn"], []),
    ("step3_parallel_and_errors.py",
     ["Claude called: get_policy_status {'policy_number': 'LIC-48213'}",
      "Claude called: get_policy_status {'policy_number': 'LIC-77102'}",
      "Claude called: get_policy_status {'policy_number': 'LIC-00000'}"], []),
    ("step4_tool_runner.py", ["stop_reason: tool_use", "stop_reason: end_turn"], []),
]

failures = 0
for script, must_contain, must_not_contain in CHECKS:
    start = time.time()
    proc = subprocess.run(
        [sys.executable, str(HERE / script)], capture_output=True, text=True, timeout=120
    )
    out = proc.stdout + proc.stderr
    ok = proc.returncode == 0
    ok = ok and all(marker in out for marker in must_contain)
    ok = ok and not any(marker in out for marker in must_not_contain)
    print(f"{'PASS' if ok else 'FAIL'}  {script}  ({time.time() - start:.1f}s)")
    if not ok:
        failures += 1
        print(out[-600:])

sys.exit(1 if failures else 0)

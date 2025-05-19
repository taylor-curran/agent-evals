"""Automate sending the next prompt from a CSV into Windsurf.

The implementation follows the plan documented in ``plan_run_ides.md``.
All timings were tuned by hand and are therefore configurable, but
reasonable defaults are provided.
"""

from __future__ import annotations

import csv
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
import shutil
from urllib.parse import urlparse
from pyautogui import hotkey, press, keyDown, keyUp, typewrite

__all__ = ["run_prompt_for_next_row"]

# ── Helpers ──────────────────────────────────────────────────────────


def _bring_windsurf_to_front() -> None:
    """macOS-only: Activate the Windsurf window via AppleScript."""
    script = 'tell application "System Events" to set frontmost of process "Windsurf" to true'
    subprocess.run(
        shlex.split("osascript -e " + shlex.quote(script)),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _close_all_editors() -> None:
    """Send ⌘K ⌘W to close every open editor tab.

    The 0.3-second pause at the end proved crucial in manual testing to
    ensure the second chord is fully processed before continuing.
    """
    keyDown("command")
    press("k")
    keyUp("command")

    keyDown("command")
    press("w")
    keyUp("command")

    time.sleep(0.3)


# ── Public API ────────────────────────────────────────────────────────


# Default CSV resolved relative to this file so it works from any cwd.
DEFAULT_CSV = (
    Path(__file__).resolve().parent.parent / "generate" / "generated_prompts.csv"
)


def run_prompt_for_next_row(
    *,
    repo_url: str | None = None,
    repo_path: Path | None = None,
    csv_path: Path = DEFAULT_CSV,
    startup_delay: float = 2,
    ui_settle_delay: float = 2,
    pre_type_wait: float = 10,
    chat_focus_pause: float = 0.5,
    pop_row: bool = True,
    diff_dir: Path = Path("diffs"),
    completion_wait: float = 600,
    poll_interval: float = 5,
    grace_period: float = 180,
    continue_interval: float = 60,
    n_prompts: int = 1,
    prompts: list[str] | None = None,
) -> Path:
    """Run the *next* CSV prompt in Windsurf and capture the resulting diff.

    Parameters
    ----------
    repo_url
        URL of the Git repository to clone and open in Windsurf.
    repo_path
        Path to the Git repository in which Windsurf should be opened.
    csv_path
        CSV containing the prompts; first row is consumed.
    startup_delay, ui_settle_delay, pre_type_wait, chat_focus_pause
        Tunable delays (seconds) that make the automation reliable.
    pop_row
        Whether to remove the used row from ``csv_path``.
    diff_dir
        Directory in which the resulting ``*.patch`` should be written.
    completion_wait
        Maximum total time (seconds) to wait for the diff to stabilise.
    poll_interval
        Seconds between successive ``git diff`` checks.
    grace_period
        Diff must remain unchanged for this many seconds before capture. Default 180 s.
    continue_interval
        How often (seconds) to send ⌥↵ to encourage the assistant to continue.
    n_prompts
        Number of prompts to run.
    prompts
        Optional hard-coded list of prompt strings. If provided, the CSV will
        be ignored and the first prompt in the list will be used.

    Returns
    -------
    Path
        Location of the ``.patch`` file that contains ``git diff`` output.
    """
    # 0. Clone the repository if a URL is given ---------------------------
    if repo_url:
        CLONE_BASE = Path("/Users/taylorcurran/Documents/dev/eval_dump/agent_cloned")
        CLONE_BASE.mkdir(parents=True, exist_ok=True)
        repo_name = Path(urlparse(repo_url).path).stem  # strips trailing .git
        target_dir = CLONE_BASE / repo_name
        if target_dir.exists():
            print(f"▶️  [0] Removing existing clone {target_dir}...", flush=True)
            shutil.rmtree(target_dir)
        print(f"▶️  [0] Cloning {repo_url} into {target_dir}...", flush=True)
        subprocess.check_call(
            ["git", "clone", "--depth", "1", repo_url], cwd=str(CLONE_BASE)
        )
        repo_path = target_dir

    if repo_path is None:
        sys.exit("[!] Either repo_url or repo_path must be provided.")

    repo_path = Path(repo_path).expanduser().resolve()
    if not repo_path.is_dir():
        sys.exit(f"[!] repo_path not found: {repo_path}")

    # 1. Ingest prompt --------------------------------------------------
    if prompts:
        prompt_text = prompts[0]
        pr_number = None
        print("▶️  [1] Using hard-coded prompt list (first entry)...", flush=True)
    else:
        print(f"▶️  [1] Ingesting prompt from {csv_path}...", flush=True)
        if not csv_path.is_file():
            sys.exit(f"[!] CSV not found: {csv_path}")

        with csv_path.open(newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            rows = list(reader)
        if not rows:
            sys.exit("[!] CSV appears empty.")

        first_row = rows[0]
        # Try a few common column names; fall back to first non-empty value.
        prompt_text: Optional[str] = (
            first_row.get("prompt")
            or first_row.get("prompt_text")
            or next((v for v in first_row.values() if v), None)
        )
        if not prompt_text:
            sys.exit("[!] Could not locate prompt text in first CSV row.")

        pr_number: str | None = first_row.get("pr_number") or first_row.get("id")

        # Optionally pop the row and rewrite CSV.
        if pop_row:
            with csv_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(rows[1:])

    print(f"▶️  [2] Launching Windsurf in {repo_path}...", flush=True)
    # 2. Launch Windsurf -------------------------------------------------
    subprocess.Popen(
        ["windsurf", "."],
        cwd=str(repo_path),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(startup_delay)

    print("▶️  [3] Bringing Windsurf window to front...", flush=True)
    # 3. Bring to front --------------------------------------------------
    _bring_windsurf_to_front()

    print(
        f"▶️  [4] UI prep: waiting {ui_settle_delay}s then closing editors...",
        flush=True,
    )
    # 4. UI prep --------------------------------------------------------
    time.sleep(ui_settle_delay)  # let tabs finish rendering
    _close_all_editors()  # chord must not mis-fire

    print("▶️  [5] Sending prompt to chat...", flush=True)
    # 5. Send prompt ----------------------------------------------------
    time.sleep(pre_type_wait)
    hotkey("command", "shift", "l")
    time.sleep(chat_focus_pause)
    typewrite(prompt_text, interval=0.02)
    press("enter")
    print("✔️  Sent prompt:", prompt_text[:80] + ("…" if len(prompt_text) > 80 else ""))

    print("▶️  [6] Waiting for diff to stabilise...", flush=True)
    # 6. Wait for completion (poll until diff stabilises) --------------
    start_time = time.time()
    last_diff: bytes | None = None
    stable_time = 0.0
    first_change_seen = False  # have we seen any diff yet?
    last_continue = start_time  # schedule ⌥↵ presses

    while True:
        now = time.time()

        # Periodically send ⌥↵ to nudge the assistant.
        if now - last_continue >= continue_interval:
            print("   ⌥↵   sending continue keystroke", flush=True)
            hotkey("option", "enter")  # Option + Return
            last_continue = now

        diff_bytes = subprocess.check_output(["git", "diff"], cwd=str(repo_path))

        # Ignore empty diffs until the first real change appears.
        if len(diff_bytes) == 0 and not first_change_seen:
            elapsed = time.time() - start_time
            if completion_wait and elapsed >= completion_wait:
                print(
                    f"⚠️  No diff produced after {completion_wait}s; capturing current (empty) diff.",
                    flush=True,
                )
                last_diff = diff_bytes  # will be empty
                break
            time.sleep(poll_interval)
            continue

        if diff_bytes != last_diff:
            last_diff = diff_bytes
            first_change_seen = True
            stable_time = 0.0  # reset stability timer on change
            print(
                f"   ↻ diff updated (size {len(diff_bytes)} bytes); stability timer reset",
                flush=True,
            )
        else:
            stable_time += poll_interval
            print(
                f"   … no change for {stable_time:.1f}/{grace_period}s (size {len(diff_bytes)} bytes)",
                flush=True,
            )

        if stable_time >= grace_period:
            break  # diff unchanged long enough

        elapsed = time.time() - start_time
        if completion_wait and elapsed >= completion_wait:
            print(
                f"⚠️  Reached max wait of {completion_wait}s; capturing current diff.",
                flush=True,
            )
            break

        time.sleep(poll_interval)

    # Out of the polling loop: diff considered stable or timeout reached
    final_elapsed = time.time() - start_time
    print(
        f"✔️  Diff stabilised in {final_elapsed:.1f}s; final size {len((last_diff or b''))} bytes",
        flush=True,
    )

    print("▶️  [7] Capturing git diff...", flush=True)
    # 7. Capture diff ---------------------------------------------------
    diff_dir.mkdir(parents=True, exist_ok=True)
    patch_name = f"{pr_number or int(time.time())}.patch"
    patch_path = diff_dir / patch_name

    patch_path.write_bytes(last_diff or b"")

    print("✔️  Diff saved to", patch_path)
    return patch_path


# ── CLI shim (single call) ────────────────────────────────────────────

if __name__ == "__main__":
    # Example usage. Replace with any public Git URL you want to test.
    run_prompt_for_next_row(
        repo_url="https://github.com/PrefectHQ/prefect",
        prompts=[
            "Add filtering logic to the cancellation-event subscription so that each process runner first verifies that the incoming event’s flow-run identifier (e.g., matching work_pool_id, deployment_id, or another runner-specific tag) corresponds to a run it launched, and only then executes PID lookup, on-cancellation hooks, and state updates—otherwise the runner should ignore the event entirely without mutating the flow run’s state or emitting warnings. Implement any and all changes once you determine the right course of action. Do not ask for my approval or solicit my opinion until you have made the required code changes."
        ],
    )


# hard coded prompt from https://github.com/PrefectHQ/prefect/issues/18106

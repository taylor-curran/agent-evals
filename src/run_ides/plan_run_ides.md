# Plan: `run_windsurf_prompts.py`

Automate **one** prompt from `generated_prompts.csv` in Windsurf, keeping the code reusable and import-friendly.

---
## 1. Objectives

1. Optionally clone a target repository from a given URL (`repo_url`).
2. Launch Windsurf in the target repository (`windsurf .`).
3. Feed the *next* prompt (FIFO) from `src/generate/generated_prompts.csv` into the chat (⌘⇧L).
4. Wait (fixed delay for v0) for the agent to finish.
5. Capture any code changes with `git diff` and save to `diffs/<pr_number>.patch` *(stdout too).*
6. Expose everything behind **one** well-named function; the `__main__` guard should call only that.

---
## 2. New file

`src/run_ides/run_windsurf_prompts.py`

```python
from pathlib import Path
from typing import Optional
import csv, subprocess, shlex, time, os, sys, shutil, pyautogui

__all__ = ["run_prompt_for_next_row"]

def run_prompt_for_next_row(
    *,  # keyword-only API
    repo_url: str | None = None,
    repo_path: Path | None = None,
    csv_path: Path = DEFAULT_CSV,  # Path relative to script location
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
) -> Path:  # returns diff file path
    """Run the next CSV prompt in Windsurf and capture resulting diff."""
    # 0. optionally clone repo if repo_url provided
    # 1. read & (optionally) pop first row
    # 2. launch windsurf .
    # 3. bring to front via osascript
    # 4. close all editors (⌘K ⌘W)
    # 5. focus chat (⌘⇧L), type prompt, press ↩
    # 6. wait; TODO smarter completion signal
    # 7. capture git diff
    # 8. return path to diff file

if __name__ == "__main__":
    run_prompt_for_next_row(
        repo_url="https://github.com/PrefectHQ/prefect",
        prompts=[
            "Add filtering logic to the cancellation-event subscription so that each process runner first verifies that the incoming event's flow-run identifier (e.g., matching work_pool_id, deployment_id, or another runner-specific tag) corresponds to a run it launched, and only then executes PID lookup, on-cancellation hooks, and state updates—otherwise the runner should ignore the event entirely without mutating the flow run's state or emitting warnings. Implement any and all changes once you determine the right course of action. Do not ask for my approval or solicit my opinion until you have finished making the required code changes."
        ],
    )
```

*No* argparse; parameters are normal Python arguments with sensible defaults.

---
## 3. Detailed Steps

0. **Clone repository (optional)**
   - If `repo_url` is supplied, clone into `/Users/taylorcurran/Documents/dev/eval_dump/agent_cloned/<repo_name>`.
   - If the target folder exists, delete it first, then clone (`git clone --depth 1`).
   - Set `repo_path` to that directory for the remaining steps.

1. **Prompt ingestion**
   - If `prompts` is provided, use the first prompt from that list.
   - Otherwise, open CSV with `newline=""` and `csv.DictReader`.
   - Store first row → `pr_number`, `prompt_text`.
   - If `pop_row=True`, rewrite CSV without that row.

2. **Launching Windsurf**
   - `subprocess.Popen(["windsurf", "."], cwd=repo_path, stdout=DEVNULL, stderr=DEVNULL)`.
   - Sleep `startup_delay` seconds.

3. **Bring app front-most** *(macOS)*
   ```python
   script = 'tell application "System Events" to set frontmost of process "Windsurf" to true'
   subprocess.run(shlex.split("osascript -e " + shlex.quote(script)), stdout=DEVNULL, stderr=DEVNULL)
   ```

4. **UI prep**
   - Sleep `ui_settle_delay` (let editor tabs finish rendering).
   - Close all editors with ⌘K ⌘W (pyautogui; includes a 0.3 s safety pause).

5. **Send prompt**
   - Sleep `pre_type_wait` (gives model warm-up + user margin).
   - `pyautogui.hotkey("command", "shift", "l")` → focus chat.
   - Sleep `chat_focus_pause`.
   - `pyautogui.typewrite(prompt_text, interval=0.02); pyautogui.press("enter")`.

6. **Wait for completion**
   - Poll `git diff` at regular intervals (`poll_interval` seconds).
   - Track when diff stabilizes (no changes for `grace_period` seconds).
   - Periodically send ⌥↵ (Option+Return) every `continue_interval` seconds to encourage the assistant to continue.
   - Timeout after `completion_wait` seconds if specified.

7. **Capture diff**
   - Ensure `diff_dir` exists.
   - `diff_bytes = subprocess.check_output(["git", "diff"], cwd=repo_path)`.
   - Write to `diff_dir/f"{pr_number or int(time.time())}.patch"`.
   - Print diff to stdout for debugging.

8. **Return path** so callers can fetch.

---
## 4. Future Enhancements

- Parameterise `ide="windsurf" | "cursor" | "copilot"` and switch launch / focus logic.
- Detect "END" or read Cascade chat DOM via AppleScript Accessibility API.
- Support for hard-coded prompts via the `prompts` parameter, bypassing CSV reading.
- Loop across all prompts; respect rate-limits.

---
## 5. Test-run checklist

1. Run `python run_windsurf_prompts.py` 
2. Observe Windsurf opens, prompt sent, waits, diff captured.
3. Confirm patch file exists and contains expected changes.


# General TODOs

- High Priority: The repo that is cloned should be a version that is reflective of the gh issues that generated the prompt. RN, these issues are historical and they don't apply to the current codebase.
- It appeared as if the script wasn't going to the csv for the propmts and it was instead getting a prompt from the md file... i need to verify that part of the script is working properly.
- Lower Priority: When a repo is cloned for the first time a message pops up in the IDE that asks if we trust the authors, we want to automate that acceptance perhaps.
- We now have diffs making themselves apparent in /diffs -- we will eventually need to build a grading system that grades the raw diff against the real PR.
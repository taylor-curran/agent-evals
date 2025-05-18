# Plan: `run_windsurf_prompt.py`

Automate **one** prompt from `generated_prompts.csv` in Windsurf, keeping the code reusable and import-friendly.

---
## 1. Objectives

1. Launch Windsurf in a target repo (`windsurf .`).
2. Feed the *next* prompt (FIFO) from `src/generate/generated_prompts.csv` into the chat (⌘⇧L).
3. Wait (fixed delay for v0) for the agent to finish.
4. Capture any code changes with `git diff` and save to `diffs/<pr_number>.patch` *(stdout too).*
5. Expose everything behind **one** well-named function; the `__main__` guard should call only that.

---
## 2. New file

`src/run_ides/run_windsurf_prompt.py`

```python
from pathlib import Path
from typing import Optional
import csv, subprocess, shlex, time, os, sys, pyautogui

__all__ = ["run_prompt_for_next_row"]

def run_prompt_for_next_row(
    repo_path: Path,
    csv_path: Path = Path("src/generate/generated_prompts.csv"),
    startup_delay: float = 2,
    ui_settle_delay: float = 2,
    pre_type_wait: float = 10,
    chat_focus_pause: float = 0.5,
    pop_row: bool = True,
    diff_dir: Path = Path("diffs"),
) -> Path:  # returns diff file path
    """Run the next CSV prompt in Windsurf and capture resulting diff."""
    # 1. read & (optionally) pop first row
    # 2. launch windsurf .
    # 3. bring to front via osascript
    # 4. close all editors (⌘K ⌘W)
    # 5. focus chat (⌘⇧L), type prompt, press ↩
    # 6. wait; TODO smarter completion signal
    # 7. capture git diff
    # 8. return path to diff file

if __name__ == "__main__":
    run_prompt_for_next_row(Path.cwd())
```

*No* argparse; parameters are normal Python arguments with sensible defaults.

---
## 3. Detailed Steps

1. **Prompt ingestion**
   - Open CSV with `newline=""` and `csv.DictReader`.
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
   - Close all editors with ⌘K ⌘W (pyautogui).
   - Sleep `ui_settle_delay`.

5. **Send prompt**
   - Sleep `pre_type_wait` (gives model warm-up + user margin).
   - `pyautogui.hotkey("command", "shift", "l")` → focus chat.
   - Sleep `chat_focus_pause`.
   - `pyautogui.typewrite(prompt_text, interval=0.02); pyautogui.press("enter")`.

6. **Wait for completion** *(v0)*
   - Simple `time.sleep(120)` or until user interrupts.
   - TODO: smarter parsing of chat area or git diff polling.

7. **Capture diff**
   - Ensure `diff_dir` exists.
   - `diff = subprocess.check_output(["git", "diff"], cwd=repo_path).decode()`.
   - Write to `diff_dir/f"{pr_number}.patch"`.
   - Print diff to stdout for debugging.

8. **Return path** so callers can fetch.

---
## 4. Future Enhancements

- Parameterise `ide="windsurf" | "cursor" | "copilot"` and switch launch / focus logic.
- Detect "END" or read Cascade chat DOM via AppleScript Accessibility API.
- Loop across all prompts; respect rate-limits.

---
## 5. Test-run checklist

1. `git pull --depth 1` if repo not present.
2. Run `python -m src.run_ides.run_windsurf_prompt` inside the target repo folder.
3. Observe Windsurf opens, prompt sent, waits, diff captured.
4. Confirm patch file exists and contains expected changes.
#!/usr/bin/env python3
import os
import subprocess
import time
import sys
import shlex
import pyautogui

# ── Config ──────────────────────────────────────────────────────────
REPO_PATH = "/Users/taylorcurran/Documents/demos/pre-made/windsurf-demo"
CHAT_QUESTION = "What does this repo do?"
STARTUP_DELAY = 2  # wait for the app process to spawn
UI_SETTLE_DELAY = 2  # ← new: wait for editor tabs to load **before** closing
PRE_TYPE_WAIT = 10  # extra time you wanted before typing
CHAT_FOCUS_PAUSE = 0.5
# ────────────────────────────────────────────────────────────────────


def launch_windsurf(path: str) -> None:
    if not os.path.isdir(path):
        sys.exit(f"[!] Repo path not found: {path}")
    subprocess.Popen(
        ["windsurf", "."],
        cwd=path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def activate_windsurf() -> None:
    script = (
        'tell application "System Events" to set frontmost of process '
        '"Windsurf" to true'
    )
    subprocess.run(
        shlex.split("osascript -e " + shlex.quote(script)),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def close_all_editors() -> None:
    """Send ⌘K ⌘W to close every open tab."""
    pyautogui.keyDown("command")
    pyautogui.press("k")
    pyautogui.keyUp("command")

    pyautogui.keyDown("command")
    pyautogui.press("w")
    pyautogui.keyUp("command")

    time.sleep(0.3)


def main() -> None:
    launch_windsurf(REPO_PATH)
    time.sleep(STARTUP_DELAY)  # process is started
    activate_windsurf()  # make it front-most
    time.sleep(UI_SETTLE_DELAY)  # ← let editor tabs finish rendering
    close_all_editors()  # now the chord won’t mis-fire

    time.sleep(PRE_TYPE_WAIT)  # your extra breathing room
    pyautogui.hotkey("command", "shift", "l")
    time.sleep(CHAT_FOCUS_PAUSE)
    pyautogui.typewrite(CHAT_QUESTION, interval=0.02)
    pyautogui.press("enter")
    print("✔️  Sent:", CHAT_QUESTION)


if __name__ == "__main__":
    main()

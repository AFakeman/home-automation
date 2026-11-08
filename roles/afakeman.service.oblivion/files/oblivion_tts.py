#!/usr/bin/env python3
"""Synthesize an Oblivion dialogue using the macOS Yuri voice."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile


def respond(environ, output):
    dialogue_id = environ.get("PATH_INFO", "")[1:]
    dialogue = None
    if dialogue_id:
        with Path(__file__).with_name("oblivion_dialogue.txt").open(encoding="utf-8") as source:
            for raw_line in source:
                key, separator, text = raw_line.rstrip("\r\n").partition("@")
                if separator and key == dialogue_id:
                    dialogue = text
                    break
    if dialogue is None:
        output.write(b"Content-type: text/html; charset=UTF-8\r\n\r\nNot found.")
        return

    with tempfile.TemporaryDirectory(prefix="oblivion-tts-") as directory:
        sound = Path(directory) / "sound.wav"
        subprocess.run(
            ["/usr/bin/say", "-v", "Yuri", "-o", str(sound),
             "--data-format=LEF32@22050", "--", dialogue],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        audio = sound.read_bytes()
        output.write(
            f"Content-length: {len(audio)}\r\nContent-type: audio/wav\r\n\r\n".encode("ascii")
        )
        output.write(audio)


if __name__ == "__main__":
    respond(os.environ, sys.stdout.buffer)

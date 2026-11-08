#!/usr/bin/env python3
"""Synthesize an Oblivion dialogue using the macOS Yuri voice."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile


SYNTHESIS_TIMEOUT_SECONDS = 20


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

    try:
        with tempfile.TemporaryDirectory(prefix="oblivion-tts-") as directory:
            sound = Path(directory) / "sound.wav"
            subprocess.run(
                ["/usr/bin/say", "-v", "Yuri", "-o", str(sound),
                 "--data-format=LEF32@22050", "--", dialogue],
                check=True,
                timeout=SYNTHESIS_TIMEOUT_SECONDS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            audio = sound.read_bytes()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as error:
        print(
            f"oblivion_tts: synthesis failed for {dialogue_id!r}: {error}; "
            f"stderr={getattr(error, 'stderr', None)!r}",
            file=sys.stderr,
            flush=True,
        )
        # http.server's CGI handler sends HTTP 200 before executing the script;
        # it does not translate a CGI Status header into an HTTP error status.
        body = b"Speech synthesis failed or timed out. Check the CGI server log.\n"
        output.write(
            f"Content-length: {len(body)}\r\n"
            "Content-type: text/plain; charset=UTF-8\r\n"
            "Cache-Control: no-store\r\n\r\n".encode("ascii")
        )
        output.write(body)
        return

    output.write(
        f"Content-length: {len(audio)}\r\nContent-type: audio/wav\r\n\r\n".encode("ascii")
    )
    output.write(audio)


if __name__ == "__main__":
    respond(os.environ, sys.stdout.buffer)

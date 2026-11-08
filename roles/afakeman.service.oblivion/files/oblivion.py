#!/usr/bin/env python3
"""Render an Oblivion dialogue as a CGI response."""

import html
import os
from pathlib import Path
import random
import sys
from urllib.parse import quote


def render(environ):
    dialogues = dict(
        line.rstrip("\r\n").split("@", 1)
        for line in Path(__file__).with_name("oblivion_dialogue.txt")
        .read_text(encoding="utf-8").splitlines()
        if "@" in line
    )
    english = environ.get("HTTP_USER_AGENT", "").startswith("oblivion.")
    title, more, permalink = (
        ("Oblivion dialogue", "another one", "permalink")
        if english else ("Даванем подливы", "еще", "пермалинк")
    )
    dialogue_id = environ.get("PATH_INFO", "")[1:]
    if not dialogue_id and dialogues:
        dialogue_id = random.choice(list(dialogues))

    parts = [
        "<html>", "<head>", '<meta name="viewport" content="width=device-width">',
        f"<title>{title}</title>", "</head>", "<body>",
    ]
    if dialogue_id not in dialogues:
        parts.extend(["<h1>404</h1>", f'<a href="/">{more}</a>'])
    else:
        parts.append(f"<h1>{html.escape(dialogues[dialogue_id])}</h1>")
        query = environ.get("QUERY_STRING", "")
        suffix = "?" + query if query else ""
        path = "/" + quote(dialogue_id, safe="")
        if query:
            parts.extend([
                f'<audio preload="none" controls src="/voice/{quote(dialogue_id, safe="")}.wav"></audio>',
                "<br>",
            ])
        parts.extend([
            f'<a href="{html.escape(path + suffix, quote=True)}">{permalink}</a>',
            "<br>",
            f'<a href="{html.escape("/" + suffix, quote=True)}">{more}</a>',
        ])
    parts.extend(["</body>", "</html>"])
    return "Content-type: text/html; charset=UTF-8\r\n\r\n" + "\n".join(parts) + "\n"


if __name__ == "__main__":
    sys.stdout.buffer.write(render(os.environ).encode("utf-8"))

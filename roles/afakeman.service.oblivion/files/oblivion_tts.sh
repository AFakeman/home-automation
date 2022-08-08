#!/usr/bin/env bash

set -eauo pipefail

if [ -z "$PATH_INFO" ] || [ "$PATH_INFO" = "/" ]; then
    echo -en 'Content-type: text/html; charset=UTF-8\r\n'
    echo -en '\r\n'
    echo -en 'Not found.'
    exit
else
    dialogueid="${PATH_INFO:1}"
fi

raw_line=`grep "^$dialogueid@" cgi-bin/oblivion_dialogue.txt || true`

if [ -z "$raw_line" ]; then
    echo -en 'Content-type: text/html; charset=UTF-8\r\n'
    echo -en '\r\n'
    echo -en 'Not found.'
    exit
fi

line=`echo "$raw_line" | cut -d'@' -f2`

directory=`mktemp -d`

trap "rm -rf $directory" EXIT

say -v Yuri "$line" -o "$directory/sound.wav" --data-format=LEF32@22050

size=`stat -f%z $directory/sound.wav`

echo -en "Content-length: $size\r\n"
echo -en 'Content-type: audio/wav\r\n'
echo -en '\r\n'
cat "$directory/sound.wav"

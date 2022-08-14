#!/usr/bin/env bash

set -eauo pipefail

if [[ "$HTTP_USER_AGENT" == oblivion.* ]]; then
    title="Oblivion dialogue"
    more="another one"
    permalink="permalink"
else
    title="Даванем подливы"
    more="еще"
    permalink="пермалинк"
fi

function random_voiceline() {
    sort -R cgi-bin/oblivion_dialogue.txt | head -n1 | cut -d'@' -f1
}

if [ -z "$PATH_INFO" ] || [ "$PATH_INFO" = "/" ]; then
    dialogueid=`random_voiceline || true`
else
    dialogueid="${PATH_INFO:1}"
fi

raw_line=`grep "^$dialogueid@" cgi-bin/oblivion_dialogue.txt || true`

echo -en 'Content-type: text/html; charset=UTF-8\r\n'
echo -en '\r\n'

echo "<html>"
echo "<head>"
echo '<meta name="viewport" content="width=device-width">'
echo "<title>$title</title>"
echo "</head>"
echo "<body>"
if [ -z "$raw_line" ]; then
    echo "<h1>404</h1>"
    echo "<a href=\"/\">$more</h1>"
else
    line=`echo "$raw_line" | cut -d'@' -f2`
    echo "<h1>$line</h1>"
    if [ -n "$QUERY_STRING" ]; then
        echo "<audio preload=\"none\" controls src=\"/voice/$dialogueid.wav\"></audio>"
        echo "<br>"
        echo "<a href=\"$dialogueid?$QUERY_STRING\">$permalink</h1>"
        echo "<br>"
        echo "<a href=\"/?$QUERY_STRING\">$more</h1>"
    else
        echo "<a href=\"$dialogueid\">$permalink</h1>"
        echo "<br>"
        echo "<a href=\"/\">$more</h1>"
    fi
fi
echo "</body>"
echo "</html>"

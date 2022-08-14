#!/usr/bin/env bash

export CGIT_CONFIG=/usr/local/etc/cgitrc
export SCRIPT_NAME=
export MODE="${HTTP_USER_AGENT}"

if [ "$HTTP_USER_AGENT" = "local" ]; then
    export MODE=all
else
    export MODE=public
fi

echo -en "X-Is-Remote: $MODE\r\n"
exec /usr/local/opt/cgit/share/cgit/cgit.cgi

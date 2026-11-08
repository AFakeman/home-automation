# MacPorts CGI server

Installs MacPorts Python 3.12 and runs `http.server --cgi` as a user LaunchAgent,
bound to `127.0.0.1` on port `8533`. The role requires macOS, MacPorts at
`/opt/local`, and `community.general`. It handles privilege escalation itself
and can run independently of nginx.

## User and GUI session

`cgi_user` defaults to `ansible_user`; no username or home directory is hardcoded.
The role resolves that account's UID, primary group, and home directory on the
target. The user must be logged into the macOS desktop. An SSH login alone does
not create the GUI session needed by speech synthesis.

The plist lives at `<home>/Library/LaunchAgents/afakeman.cgi.plist` and is loaded
explicitly into `gui/<uid>` using `launchctl bootstrap`. This ensures that
running Ansible over SSH or with `become: true` does not load it into the wrong
session. `LimitLoadToSessionType=Aqua` restricts it to a GUI session.

**The agent starts at GUI login and stops at logout. It will not serve requests
after reboot until that user logs in.**

## Configuration

Defaults are in `defaults/main.yml`. The web root and log directory follow
`nginx_www_dir` and `nginx_log_dir` when supplied, otherwise default to
`/opt/local/www` and `/opt/local/var/log/nginx`. Override `cgi_user`, `cgi_dir`,
`cgi_log_file`, `cgi_port`, or the Python settings as needed.

The role creates the log file with write access for the CGI user, preserves log
contents/timestamps, validates the plist with plutil, and reloads the agent on
plist or log-permission changes. Pending handlers run before the localhost
listener check.

Scripts are deployed by their application roles (for example,
`afakeman.service.oblivion`), not this service role. On the target, as the same
user configured in Ansible:

```sh
curl http://127.0.0.1:8533/
launchctl print "gui/$(id -u)/afakeman.cgi"
tail -n 50 /opt/local/var/log/nginx/cgi.log
```

Python's built-in CGI server is a legacy backend, not a general-purpose
production web server. Keep it bound to localhost behind nginx.

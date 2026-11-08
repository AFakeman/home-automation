# MacPorts nginx

Installs nginx through MacPorts, manages its configuration/directories and starts
the MacPorts-owned `org.macports.nginx` LaunchDaemon using `port load`.
The role requires macOS, MacPorts at `/opt/local`, and `community.general`.
It handles privilege escalation itself.

Defaults are in `defaults/main.yml`: `nginx_config_dir`, `nginx_log_dir`,
`nginx_www_dir`, `nginx_binary`, and `nginx_launchd_service`.

Virtual hosts are managed separately by `afakeman.utility.nginx-server`.
TLS/HSTS snippet files remain available for compatibility but are not included
by the HTTP virtual hosts.

The reload handler runs configuration validation and then launchctl HUP in one
task include. The legacy notifications `reload nginx` and
`reload nginx service` remain supported. Certificate renewal can still invoke
`tasks/reload_nginx.yml` directly through `include_role`.

MacPorts owns the launchd plist; this role no longer installs the obsolete
Homebrew `org.nginx.server` plist. If migrating an old installation, stop and
disable the old service separately to avoid port conflicts.

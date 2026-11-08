# afakeman.service.cloudflared

Installs the Catalina cloudflared package from the MacPorts overlay in
`AFakeman/cloudflared`, branch `catalina-compat`, and manages tunnel configuration
and its system LaunchDaemon.

## Prerequisites

- macOS with MacPorts installed at `/opt/local` and Apple's Command Line Tools.
- Run `sudo port selfupdate` first. The ports tree must provide `go-1.24` at
  **1.24.13 or newer** to satisfy the fork's `go.mod`.
- An Ansible-compatible Python on the target and `community.general` on the
  controller.
- Outbound access to GitHub and Go module downloads during installation.

The role registers a persistent local ports source under
`/opt/local/var/macports/local/cloudflared/macports`. The package pulls in
`go-1.24`, builds using that toolchain, and installs its launchd service. The
standard MacPorts `cloudflared` package conflicts with `cloudflared-catalina`;
remove it first if installed. Disable any separately installed cloudflared
launchd service to avoid duplicate connectors.

## Remotely managed tunnel (token)

Set `cloudflared_token` in `host_vars/mac-mini.yml`, preferably as an encrypted
Ansible Vault value:

```yaml
cloudflared_token: "{{ vault_cloudflared_token }}"
```

Cloudflare manages the ingress configuration for this tunnel. Additional client
options can be supplied through `cloudflared_config`.

## Locally managed tunnel

```yaml
cloudflared_config:
  tunnel: YOUR-TUNNEL-UUID
  ingress:
    - hostname: example.com
      service: http://127.0.0.1:80
    - service: http_status:404

# Store this mapping in Ansible Vault, not plaintext inventory.
cloudflared_credentials:
  AccountTag: YOUR-ACCOUNT-TAG
  TunnelSecret: YOUR-TUNNEL-SECRET
  TunnelID: YOUR-TUNNEL-UUID
```

Alternatively, omit `cloudflared_credentials` and set
`cloudflared_config['credentials-file']` to an existing credentials JSON file on
the target. Provision that file separately, readable by root.

Token authentication takes precedence if both modes are configured. The role
protects its configuration directory with mode `0700` and configuration/secrets
with mode `0600`, owned by root. Secret-writing tasks suppress output and diffs.
Old credential files are not automatically deleted when switching modes.

## Run

```sh
ansible-playbook playbook-cloudflared.yml --ask-vault-pass
```

The standalone playbook targets `mother-host`. It is intentionally not imported
into `playbook-setup.yml`, since tunnel credentials must be configured first.
The MacPorts module does not support check mode, so a dry run cannot reliably
simulate a fresh installation.

## Updates and service management

`cloudflared_version` defaults to `catalina-compat`; it can also be pinned to a
commit **containing the macports directory**. The role updates the checkout,
regenerates `PortIndex` as needed, and runs `port upgrade cloudflared-catalina`
when the checkout changes. To release a new binary, the Portfile itself must
have its pinned source SHA/checksums and package version/revision updated. Merely
pushing Go source changes to the branch does not update the packaged snapshot.

Configuration/package changes restart the service using `port unload` followed
by `port load`. Otherwise, the role loads an unloaded service or kickstarts a
loaded service that is not running.

```sh
sudo launchctl print system/org.macports.cloudflared-catalina
sudo tail -n 50 /opt/local/var/log/cloudflared/cloudflared.err.log
```

The package fixes the configuration location at
`/opt/local/etc/cloudflared/config.yml`; this role deliberately requires that
location. It runs as a system service under root. Do not also run
`cloudflared service install`.

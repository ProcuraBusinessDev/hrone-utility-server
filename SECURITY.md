# Security Policy

## 1. Network & Transport Security
The ZKTeco PUSH SDK / ADMS protocol communicates via HTTP POST. For production environments:
- Place the ADMS server behind a TLS-terminating reverse proxy (e.g. Caddy, NGINX, Traefik).
- Restrict inbound traffic to the terminal subnet via firewall rules (iptables/ufw).

## 2. Vulnerability Reporting
Please report any security issues to `vibhav.aggarwal2@gmail.com`.

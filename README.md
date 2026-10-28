![MAILTHORN Banner](assets/MAILTHORN-BANNER-1600x400.png)

![MAILTHORN PAGE VIEWS](https://hitscounter.dev/api/hit?url=https%3A%2F%2Fgithub.com%2FHellfire13666%2Fmailthorn-amber-herbarium&label=PAGE%20VIEWS&icon=eye&color=%23FF1493&style=flat)

# MAILTHORN // AMBER HERBARIUM v0.2.0

**GlitchByte Phantom Labs | Public DNS & Mail Intelligence**

## Quick Install

Debian-based Linux with Git and Python 3.9+:

    git clone https://github.com/Hellfire13666/mailthorn-amber-herbarium.git
    cd mailthorn-amber-herbarium
    python3 -m unittest -q
    python3 INSTALL_DESKTOP.py
    python3 OPEN_MAILTHORN.py

# MAILTHORN v0.2.0 — Amber Herbarium
GlitchByte Phantom Labs · Cultivation Room


## ONE-PASTE INSTALL & OPEN
Download `MAILTHORN-AMBER-HERBARIUM-v0.2.0.zip` into Downloads, then paste this whole block in your Debian-based Linux / Ubuntu terminal. Requires Python 3 (3.9+) already installed. No pip dependencies or API keys. Installs into its own versioned folder. Re-running restores this version's packaged files; reports are kept elsewhere.

```bash
cd "$HOME/Downloads" &&
python3 -m zipfile -e MAILTHORN-AMBER-HERBARIUM-v0.2.0.zip "$HOME/PhantomLabsTools" &&
cd "$HOME/PhantomLabsTools/mailthorn-v0.2.0" &&
python3 -m unittest -q &&
python3 INSTALL_DESKTOP.py &&
python3 OPEN_MAILTHORN.py
```

The menu offers live collection, an explicitly fictional offline demo, and tests. Live collection asks whether to save TXT + JSON. The desktop and app-menu launcher are versioned; keep the installed folder in place. Some desktops ask you to allow launching. Desktop integration is not tested on your machine yet.

## Copy-and-paste recipes

[Open EASY_RECIPES.md — 15 practical recipes](EASY_RECIPES.md). Each domain recipe puts `DOMAIN="example.com"` first so readers only change one value.

## What is different
Amber masthead, teal findings, amber failure notices, and three live terminal stages: SEED (base DNS/email policies), ROOTS (follow discovered relationships), HARVEST (relationship and published network totals). No dashboard. NO_COLOR disables terminal color.

Base collection: A, AAAA, NS, MX, SOA, TXT, CNAME, CAA, DS, DNSKEY, HTTPS; DMARC, MTA-STS, TLS reporting, default BIMI TXT locations; six mail-service SRV names; optional known DKIM selectors as TXT/CNAME. This is public DNS collection, not a port scan or mail-sending test.

New discovery follows literal SPF include/redirect references, A/MX mechanisms, published IPv4/IPv6 ranges; resolves MX/NS/SRV/CNAME targets; and looks up PTR records for discovered IP addresses. Deduplicates DNS jobs to stop include cycles. Default total job budget 150, four discovery rounds, four workers. Limits and unsupported terms are recorded in JSON, with readable discovery metadata in TXT. Each job may attempt Cloudflare and Google, so requests can exceed the DNS job count. Original raw replies, TTLs, URLs, timestamps and errors remain available in JSON. No paid keys; internet and third-party resolver services are required.

SPF ranges are published policy text, not proof that a host currently sends mail. This is an intelligence traversal, not a compliant SPF evaluation or security score. Mechanism qualifiers/ordering and CIDR restrictions on A/MX mechanisms are not evaluated. Macros, exists, ptr and exp mechanisms are not expanded. DKIM selector discovery, DMARC parent-domain fallback, MTA-STS HTTP policy fetching, DNSSEC validation, and enforcement tests are not implemented. PTR records are unverified names, not ownership evidence. Providers may return cached or differing views. Lookup failures are never reported as absent records.

## Easy recipes
Open menu:
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/OPEN_MAILTHORN.py"
```
Live domain collection:
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" example.com
```
More discovery, still bounded:
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" example.com --depth 6 --max-lookups 300
```
Save reports:
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" example.com -o "$HOME/MailthornReports/mailthorn-$(date +%Y%m%d-%H%M%S).txt"
```
Known DKIM selector:
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" example.com --selector selector1
```
Use a selector from a real email's DKIM-Signature s= value; selector1 is only an example. Up to 20 selectors. Never enter a mailbox address or full URL as the domain.

Offline visual preview (fictional records, no network requests):
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/DEMO_MAILTHORN.py"
```

## Verification and status
11 offline tests passed: validation, fallback/evidence retention, negative DNS versus failure, selectors and terminal sanitization, split TXT/SPF parsing, macro skip, reverse DNS planning, cycle prevention, budget reporting, and report saving/overwrite protection. Offline synthetic demo completed 25 jobs. Successful live retrieval remains unverified: the original live smoke test timed out in the build environment. No claim of MX/Ubuntu live testing or GitHub publication.

CLI exit statuses: 0 no lookup failures; 1 partial lookup failure; 2 all failed, argument or file error; 130 interrupted. Timeout 1–60 seconds per attempt (default 8); OS DNS resolution can outlast socket timeout. Ctrl+C does not save an interrupted run. Write failures can leave one member of the TXT/JSON pair; use a fresh output basename.

The exact approved artwork is preserved. Its pictured v0.1.0 command documents the earlier package; use the current text recipes above for v0.2.0.

## Next practical improvement
Add a comparison mode that shows DNS/policy changes between two saved snapshots.

## Technical references
- https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/make-api-requests/dns-json/
- https://developers.google.com/speed/public-dns/docs/doh/json
- https://www.rfc-editor.org/rfc/rfc7208.html
- https://www.rfc-editor.org/rfc/rfc6186.html
- https://www.rfc-editor.org/info/rfc8314/

## Public release and privacy standards

MAILTHORN is a public-source DNS and mail-policy research tool
for Debian-based Linux systems.

- Use generic Linux terminology and portable project-relative paths.
- Never publish personal usernames, hostnames, workstation paths,
  credentials, authentication tokens, private messages, or research reports.
- Keep generated evidence files and local backups outside Git tracking.
- Public DNS records are infrastructure observations, not proof of
  a person's identity, mailbox ownership, or physical location.
- Network lookups may disclose the queried domain to DNS providers.
- Report collection limits and provider failures accurately.
- Use fictional or reserved example domains in public documentation.
- No API key, account bypass, mailbox access, or private-data collection
  is required for the documented public-DNS features.
- Keep each GlitchByte tool independent, with its own repository,
  approved artwork, tests, and beginner examples.
- Official publication uses GitHub Free. No paid upgrade is required.

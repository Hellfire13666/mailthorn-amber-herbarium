#!/usr/bin/env python3
"""MAILTHORN v0.2.0: independent public DNS/email evidence collector."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import ipaddress
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

PROVIDERS = [('Cloudflare', 'https://cloudflare-dns.com/dns-query'),
             ('Google', 'https://dns.google/resolve')]
TYPES = {'A':1, 'NS':2, 'CNAME':5, 'SOA':6, 'MX':15, 'TXT':16,
         'PTR':12, 'SRV':33, 'AAAA':28, 'DS':43, 'DNSKEY':48, 'CAA':257, 'HTTPS':65}

def now():
    return datetime.now(timezone.utc).isoformat()

def domain(value):
    try:
        value = value.strip().rstrip('.').encode('idna').decode('ascii').lower()
    except UnicodeError:
        raise argparse.ArgumentTypeError('Invalid internationalized domain')
    if len(value) > 253 or '.' not in value or any(
        not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', p)
        for p in value.split('.')):
        raise argparse.ArgumentTypeError('Enter a domain, without a URL or path.')
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return value
    raise argparse.ArgumentTypeError('Enter a domain rather than an IP address.')

def query(name, kind, timeout=8):
    attempts = []
    for provider, base in PROVIDERS:
        url = base + '?' + urllib.parse.urlencode({'name':name, 'type':kind})
        attempt = {'provider':provider, 'url':url, 'time_utc':now()}
        try:
            req = urllib.request.Request(url, headers={'Accept':'application/dns-json',
                                                       'User-Agent':'MAILTHORN/0.2.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read(1048577)
            if len(data) > 1048576:
                raise ValueError('Response exceeds 1 MiB limit')
            data = json.loads(data)
            if not isinstance(data, dict) or type(data.get('Status')) is not int:
                raise ValueError('Invalid DNS response')
            attempt['response'] = data
            attempts.append(attempt)
            if data['Status'] not in (0, 3) or data.get('TC'):
                continue
            answers = [a for a in data.get('Answer', [])
                       if a.get('type') == TYPES[kind]]
            return {'name':name, 'type':kind, 'state':
                    'NXDOMAIN' if data['Status'] == 3 else
                    ('ANSWER' if answers else 'NO_ANSWER'),
                    'answers':answers, 'attempts':attempts}
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            attempt['error'] = str(exc)
            attempts.append(attempt)
        time.sleep(0.2)
    return {'name':name, 'type':kind, 'state':'LOOKUP_FAILED',
            'answers':[], 'attempts':attempts}

def clean(text):
    # Prevent remote DNS text from injecting terminal control sequences.
    return ''.join(c if c.isprintable() else ' ' for c in str(text))

def emit(result):
    color = sys.stdout.isatty() and 'NO_COLOR' not in os.environ
    prefix = ('\033[38;5;214m' if result['state'] == 'LOOKUP_FAILED' else '\033[38;5;80m') if color else ''
    suffix = '\033[0m' if color else ''
    print(f"{prefix}[{result['state']}]{suffix} {result['name']} {result['type']}", flush=True)
    for answer in result['answers']:
        print('  ' + clean(answer.get('data', '')), flush=True)

def collect(jobs, workers, timeout):
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        tasks = [pool.submit(query, n, t, timeout) for n, t in sorted(set(jobs))]
        for task in as_completed(tasks):
            result = task.result()
            emit(result)
            results.append(result)
    return results

def plan(target, selectors):
    jobs = [(target, t) for t in TYPES if t not in ('PTR','SRV')]
    jobs += [(p+'._tcp.'+target, 'SRV') for p in ('_submission','_submissions','_imap','_imaps','_pop3','_pop3s')]
    jobs += [(prefix + '.' + target, 'TXT') for prefix in
             ('_dmarc', '_mta-sts', '_smtp._tls', 'default._bimi')]
    for selector in selectors:
        jobs += [(selector+'._domainkey.'+target, t) for t in ('TXT','CNAME')]
    return jobs

def dnsname(value):
    value = value.rstrip('.').lower()
    if len(value) > 253 or '.' not in value or any(
            not re.fullmatch(r'[a-z0-9_-]{1,63}', p) for p in value.split('.')):
        raise ValueError('Unsupported DNS name')
    return value

def txt(value):
    # DNS presentation format may split one TXT value into quoted chunks.
    chunks = re.findall(r'"((?:[^"\\]|\\.)*)"', value)
    if not chunks:
        return value
    def unescape(m):
        token = m.group(1)
        return chr(int(token)) if token.isdigit() else token
    return ''.join(re.sub(r'\\([0-9]{3}|.)', unescape, c) for c in chunks)

def discoveries(result):
    jobs, edges, networks, skipped = set(), [], set(), []
    source = result['name']
    def add(host, kinds, relation):
        try:
            host = dnsname(host)
        except ValueError:
            skipped.append({'source':source, 'value':host, 'reason':'unsupported name or SPF macro'})
            return
        edges.append({'source':source,'target':host,'relation':relation})
        jobs.update((host,t) for t in kinds)
    for answer in result['answers']:
        value = str(answer.get('data',''))
        if result['type'] in ('MX','NS','SRV','CNAME'):
            fields = value.split()
            if fields and fields[-1] != '.':
                add(fields[-1], ('A','AAAA'), result['type'])
        if result['type'] in ('A','AAAA'):
            try:
                address = ipaddress.ip_address(value)
                jobs.add((address.reverse_pointer,'PTR'))
            except ValueError:
                pass
        if result['type'] != 'TXT':
            continue
        value = txt(value)
        if not value.lower().startswith('v=spf1 '):
            continue
        for term in value.split()[1:]:
            term = term.lstrip('+~-?')
            lower = term.lower()
            if lower.startswith(('ip4:','ip6:')):
                try:
                    networks.add(str(ipaddress.ip_network(term.split(':',1)[1],strict=False)))
                except ValueError:
                    skipped.append({'source':source,'value':term,'reason':'invalid network'})
            elif lower.startswith('include:') or lower.startswith('redirect='):
                target = term.split(':',1)[1] if ':' in term else term.split('=',1)[1]
                add(target,('TXT',),'SPF '+('include' if ':' in term else 'redirect'))
            elif lower == 'a' or lower.startswith(('a:', 'a/')):
                target = term[2:] if lower.startswith('a:') else source
                add(target.split('/')[0],('A','AAAA'),'SPF a')
            elif lower == 'mx' or lower.startswith(('mx:', 'mx/')):
                target = term[3:] if lower.startswith('mx:') else source
                add(target.split('/')[0],('MX',),'SPF mx')
            elif '%' in term or lower.startswith(('exists:','ptr','exp=')):
                skipped.append({'source':source,'value':term,'reason':'not expanded by this collector'})
    return jobs, edges, networks, skipped

def deepen(results, workers, timeout, budget, depth):
    results = list(results)
    seen = {(r['name'],r['type']) for r in results}
    frontier = list(results)
    meta = {'edges':[], 'networks':[], 'skipped':[], 'budget':budget,
            'depth':depth, 'limits_reached':False, 'unqueried_jobs':[]}
    networks = set()
    for turn in range(depth+1):
        pending = set()
        for r in frontier:
            jobs, edges, nets, skipped = discoveries(r)
            pending.update(jobs-seen)
            meta['edges'].extend(e for e in edges if e not in meta['edges'])
            networks.update(nets)
            meta['skipped'].extend(skipped)
        if not pending:
            break
        room = max(0,budget-len(seen)) if turn < depth else 0
        chosen = sorted(pending)[:room]
        omitted = sorted(pending-set(chosen))
        if omitted:
            meta['limits_reached'] = True
            meta['unqueried_jobs'].extend([{'name':n,'type':t} for n,t in omitted])
        if not chosen:
            break
        print(f'[02 ROOTS / round {turn+1}] {len(chosen)} sourced lookups', flush=True)
        frontier = collect(chosen,workers,timeout)
        seen.update(chosen)
        results.extend(frontier)
    meta['networks'] = sorted(networks)
    print(f"[03 HARVEST] {len(meta['edges'])} relationships / {len(networks)} published SPF networks",flush=True)
    for network in sorted(networks):
        print('  SPF NETWORK '+network,flush=True)
    if meta['limits_reached']:
        print('[LIMIT] Some discoveries were not queried; see saved evidence.',flush=True)
    return results, meta

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('domain', type=domain)
    parser.add_argument('--max-lookups', type=int, default=150, help='Total DNS job budget, 65–500')
    parser.add_argument('--depth', type=int, choices=range(1,9), default=4, help='Discovery rounds, default 4')
    parser.add_argument('--selector', action='append', default=[],
                        help='Known DKIM selector; repeat up to 20 times')
    parser.add_argument('--workers', type=int, choices=range(1,9), default=4)
    parser.add_argument('--timeout', type=float, default=8)
    parser.add_argument('-o', '--output', type=Path, help='New TXT report; JSON saved alongside')
    args = parser.parse_args()
    if not 1 <= args.timeout <= 60:
        parser.error('--timeout must be between 1 and 60 seconds')
    if len(args.selector) > 20 or any(not re.fullmatch(r'[A-Za-z0-9_-]{1,63}', s)
                                     for s in args.selector):
        parser.error('Use at most 20 selectors, each 1–63 letters/digits/underscores/hyphens')
    if args.output and args.output.suffix.lower() != '.txt':
        parser.error('-o must end in .txt')
    if args.output and (args.output.exists() or args.output.with_suffix('.json').exists()):
        parser.error('Report already exists; choose a new filename')
    if not 65 <= args.max_lookups <= 500:
        parser.error('--max-lookups must be 65–500')
    started = now()
    if sys.stdout.isatty() and 'NO_COLOR' not in os.environ:
        print('\033[38;5;214m', end='')
    print('\nMAILTHORN / AMBER HERBARIUM / v0.2.0\nGlitchByte Phantom Labs · Cultivation Room\n[01 SEED] DNS + policies + mail service records', flush=True)
    if sys.stdout.isatty() and 'NO_COLOR' not in os.environ:
        print('\033[0m', end='')
    results = collect(plan(args.domain, args.selector), args.workers, args.timeout)
    results, cultivation = deepen(results, args.workers, args.timeout,
                                   args.max_lookups, args.depth)
    failures = sum(r['state'] == 'LOOKUP_FAILED' for r in results)
    report = {'tool':'MAILTHORN', 'version':'0.2.0', 'domain':args.domain,
              'started_utc':started, 'finished_utc':now(),
              'lookup_failures':failures, 'cultivation':cultivation,
              'scope':'Public DNS snapshot; no email delivery or policy enforcement testing',
              'results':sorted(results, key=lambda r:(r['name'],r['type']))}
    print(f'Completed {len(results)} lookups; {failures} failed. No answer is not a security verdict.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        lines = [f'MAILTHORN — {args.domain}', started, report['scope']]
        lines += ['Discovery: '+json.dumps(cultivation, ensure_ascii=True)]
        for r in report['results']:
            lines.append(f"\n[{r['state']}] {r['name']} {r['type']}")
            lines.extend('  '+clean(a.get('data','')) for a in r['answers'])
            for a in r['attempts']:
                lines.append(f"  Source: {a['url']} at {a['time_utc']}")
                if 'error' in a:
                    lines.append('  Error: '+clean(a['error']))
        # Exclusive creation prevents overwriting earlier evidence.
        with args.output.open('x', encoding='utf-8') as f:
            f.write('\n'.join(lines)+'\n')
        with args.output.with_suffix('.json').open('x', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=True)
        print(f'Saved {args.output} and {args.output.with_suffix(".json")}')
    return 2 if failures == len(results) else (1 if failures else 0)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\nStopped.', file=sys.stderr)
        sys.exit(130)
    except OSError as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(2)

#!/usr/bin/env python3
"""Offline visual demo. Synthetic records only; sends no network requests."""
import sys
from unittest.mock import patch
import mailthorn_cultivator as m
FIXTURES={
 ('example.com','MX'):['10 mail.example.com.'],
 ('example.com','TXT'):['"v=spf1 include:_spf.example.net -all"'],
 ('_spf.example.net','TXT'):['"v=spf1 ip4:192.0.2.0/24 ip6:2001:db8::/32 -all"'],
 ('mail.example.com','A'):['192.0.2.25'],
 ('25.2.0.192.in-addr.arpa','PTR'):['mail.example.com.'],
 ('_dmarc.example.com','TXT'):['"v=DMARC1; p=reject"'],
}
def fake(name,kind,timeout=8):
    answers=[{'name':name+'.','type':m.TYPES[kind],'TTL':300,'data':v} for v in FIXTURES.get((name,kind),[])]
    return {'name':name,'type':kind,'state':'ANSWER' if answers else 'NO_ANSWER',
            'answers':answers,'attempts':[{'provider':'OFFLINE SYNTHETIC DEMO','url':'offline:fixture','time_utc':m.now()}]}
print('OFFLINE DEMO / FICTIONAL DATA / NO NETWORK REQUESTS')
with patch.object(m,'query',side_effect=fake), patch.object(sys,'argv',['mailthorn','example.com']):
    raise SystemExit(m.main())

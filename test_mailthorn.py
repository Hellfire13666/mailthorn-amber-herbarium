import sys
import io
import json
import unittest
from unittest.mock import patch
import argparse
import mailthorn_cultivator as m

class Tests(unittest.TestCase):
    def test_domain(self):
        self.assertEqual(m.domain('EXAMPLE.COM.'), 'example.com')
        for bad in ('https://example.com', '127.0.0.1', '-x.example', 'a/b.com'):
            with self.assertRaises(argparse.ArgumentTypeError):
                m.domain(bad)

    def test_fallback_and_evidence(self):
        payload = {'Status':0, 'Answer':[{'type':1,'data':'192.0.2.1'},
                                        {'type':5,'data':'alias.example.'}]}
        with patch.object(m.urllib.request, 'urlopen', side_effect=[OSError('offline'),
                io.BytesIO(json.dumps(payload).encode())]), patch.object(m.time,'sleep'):
            r = m.query('example.com','A')
        self.assertEqual(r['state'],'ANSWER')
        self.assertEqual(len(r['attempts']),2)
        self.assertEqual(len(r['answers']),1)

    def test_failure_is_not_absence(self):
        with patch.object(m.urllib.request,'urlopen',side_effect=OSError('offline')), patch.object(m.time,'sleep'):
            self.assertEqual(m.query('example.com','TXT')['state'],'LOOKUP_FAILED')

    def test_nxdomain(self):
        with patch.object(m.urllib.request,'urlopen',return_value=io.BytesIO(b'{"Status":3}')):
            self.assertEqual(m.query('example.com','TXT')['state'],'NXDOMAIN')

    def test_plan_and_terminal(self):
        self.assertIn(('s1._domainkey.example.com','TXT'),m.plan('example.com',['s1']))
        self.assertNotIn('\x1b',m.clean('\x1b[31mremote'))


class DiscoveryTests(unittest.TestCase):
    def record(self,name,kind,value):
        return {'name':name,'type':kind,'state':'ANSWER','answers':[{'data':value}], 'attempts':[]}

    def test_split_txt_and_spf(self):
        r=self.record('example.com','TXT','"v=spf1 include:_spf.example.net " "ip4:192.0.2.0/24 a mx -all"')
        jobs,edges,nets,skipped=m.discoveries(r)
        self.assertIn(('_spf.example.net','TXT'),jobs)
        self.assertIn(('example.com','MX'),jobs)
        self.assertIn('192.0.2.0/24',nets)
        self.assertEqual(skipped,[])

    def test_macro_not_queried(self):
        jobs,edges,nets,skipped=m.discoveries(self.record('example.com','TXT','v=spf1 include:%{d}.example.net -all'))
        self.assertFalse(jobs)
        self.assertTrue(skipped)

    def test_ptr(self):
        jobs,*_=m.discoveries(self.record('mail.example.com','A','192.0.2.5'))
        self.assertIn(('5.2.0.192.in-addr.arpa','PTR'),jobs)

    def test_cycle_deduplication(self):
        first=self.record('example.com','TXT','v=spf1 include:_spf.example.net -all')
        second=self.record('_spf.example.net','TXT','v=spf1 include:example.com -all')
        with patch.object(m,'collect',return_value=[second]) as c, patch('sys.stdout',new=io.StringIO()):
            records,meta=m.deepen([first],1,1,20,4)
        self.assertEqual(c.call_count,1)
        self.assertEqual(len(records),2)
        self.assertEqual(len(meta['edges']),2)

    def test_budget_is_reported(self):
        first=self.record('example.com','TXT','v=spf1 include:_spf.example.net -all')
        with patch.object(m,'collect') as c, patch('sys.stdout',new=io.StringIO()):
            records,meta=m.deepen([first],1,1,1,4)
        c.assert_not_called()
        self.assertTrue(meta['limits_reached'])
        self.assertEqual(meta['unqueried_jobs'][0]['type'],'TXT')

class ReportTests(unittest.TestCase):
    def test_reports_and_no_overwrite(self):
        import tempfile
        from pathlib import Path
        def empty(name,kind,timeout=8):
            return {'name':name,'type':kind,'state':'NO_ANSWER','answers':[], 'attempts':[]}
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'evidence.txt'
            with patch.object(sys,'argv',['mailthorn','example.com','-o',str(path)]), patch.object(m,'query',side_effect=empty), patch('sys.stdout',new=io.StringIO()):
                self.assertEqual(m.main(),0)
            report=json.loads(path.with_suffix('.json').read_text())
            self.assertEqual(len(report['results']),21)
            self.assertIn('cultivation',report)
            original=path.read_bytes()
            with patch.object(sys,'argv',['mailthorn','example.com','-o',str(path)]), patch('sys.stderr',new=io.StringIO()):
                with self.assertRaises(SystemExit): m.main()
            self.assertEqual(path.read_bytes(),original)

if __name__ == '__main__':
    unittest.main()

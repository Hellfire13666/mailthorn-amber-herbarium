#!/usr/bin/env python3
"""Interactive launcher for desktop or terminal use."""
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parent
print('MAILTHORN / AMBER HERBARIUM\n1. Collect live intel\n2. Offline visual demo\n3. Run tests')
choice=input('Choose [1]: ').strip() or '1'
if choice=='2':
    cmd=[sys.executable,str(root/'DEMO_MAILTHORN.py')]
elif choice=='3':
    cmd=[sys.executable,'-m','unittest','-v']
elif choice=='1':
    target=input('Domain: ').strip()
    cmd=[sys.executable,str(root/'mailthorn_cultivator.py'),target]
    if input('Save TXT + JSON reports? [y/N]: ').lower()=='y':
        import uuid
        from datetime import datetime
        dest=Path.home()/'MailthornReports'/('mailthorn-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]+'.txt')
        cmd+=['-o',str(dest)]
else:
    print('Unknown choice.')
    raise SystemExit(2)
result=subprocess.run(cmd,cwd=root)
print('Exit status:',result.returncode)
input('Press Enter to close...')

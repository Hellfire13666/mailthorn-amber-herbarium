# MAILTHORN — Easy Recipes

Run the ONE-PASTE INSTALL & OPEN block in README first. Every recipe below is independent: copy the entire block. Change only `example.com` in its first line to your domain. Enter a domain such as `example.com`, not a full URL or mailbox. Selectors are an exception: use a selector you actually know.

## 1. Standard live collection
```bash
DOMAIN="example.com"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN"
```

## 2. Collect and save both TXT and JSON
Reports go to MailthornReports in your home folder. A unique filename protects older reports.
```bash
DOMAIN="example.com"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" -o "$HOME/MailthornReports/mailthorn-$(python3 -c 'import uuid; print(uuid.uuid4().hex)').txt"
```

## 3. Deeper discovery
Allow six discovery rounds and up to 300 DNS jobs. This can take longer and does not guarantee more records.
```bash
DOMAIN="example.com"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" --depth 6 --max-lookups 300
```

## 4. Deeper discovery with saved evidence
```bash
DOMAIN="example.com"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" --depth 6 --max-lookups 300 -o "$HOME/MailthornReports/mailthorn-deep-$(python3 -c 'import uuid; print(uuid.uuid4().hex)').txt"
```

## 5. Largest supported collection budget
Eight rounds and up to 500 jobs. Maximum supported does not mean exhaustive; unsupported SPF terms and limit stops remain documented.
```bash
DOMAIN="example.com"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" --depth 8 --max-lookups 500
```

## 6. Gentle collection
Two workers instead of four, with more time per request.
```bash
DOMAIN="example.com"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" --workers 2 --timeout 15
```

## 7. Slow connection
One worker, up to 20 seconds per request. This may take substantially longer; it cannot repair blocked network access.
```bash
DOMAIN="example.com"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" --workers 1 --timeout 20
```

## 8. Smaller first look
One discovery round with a budget of 65 DNS jobs.
```bash
DOMAIN="example.com"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" --depth 1 --max-lookups 65
```

## 9. Add one known DKIM selector
Replace `selector1` with the `s=` value from a real email's DKIM-Signature header. Use its signing domain (`d=`) for DOMAIN. This is not selector guessing.
```bash
DOMAIN="example.com"
SELECTOR="selector1"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" --selector "$SELECTOR"
```

## 10. Add two known DKIM selectors
```bash
DOMAIN="example.com"
SELECTOR_ONE="selector1"
SELECTOR_TWO="selector2"
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN" --selector "$SELECTOR_ONE" --selector "$SELECTOR_TWO"
```

## 11. Plain terminal text without colors
```bash
DOMAIN="example.com"
NO_COLOR=1 python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" "$DOMAIN"
```

## 12. Open the friendly menu instead
Enter the domain when asked, then choose whether to save reports.
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/OPEN_MAILTHORN.py"
```

## 13. Preview the look offline
Fictional demonstration only. No internet needed and no real findings.
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/DEMO_MAILTHORN.py"
```

## 14. Open your report folder
```bash
python3 -c 'from pathlib import Path; (Path.home()/"MailthornReports").mkdir(exist_ok=True)'
xdg-open "$HOME/MailthornReports"
```

## 15. Show all options
```bash
python3 "$HOME/PhantomLabsTools/mailthorn-v0.2.0/mailthorn_cultivator.py" --help
```

## Reading your results
| Label | Meaning |
|---|---|
| ANSWER | Requested record type returned |
| NO_ANSWER | Successful DNS response without the requested type |
| NXDOMAIN | Resolver reported that the queried name does not exist |
| LOOKUP_FAILED | Both provider attempts failed or gave unusable replies |
| ROOTS | Following relationships from collected records |
| SPF NETWORK | Network range published in an SPF record; not a verified active sender |
| LIMIT | Some discovered jobs were left unqueried |

NO_ANSWER is not a security verdict. PTR names are not proof of ownership. A nonzero exit status can mean a partial report; read the displayed summary. More rounds and larger budgets still do not collect all possible information.

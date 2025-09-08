import sys, webbrowser

RECEIPTS = [
    {"key":"perplexity","title":"Perplexity vs Google — Find the Source, Not the Hype","url":"https://vibeaxis.com/perplexity-vs-google-find-the-source-not-the-hype/"},
    {"key":"memoryab","title":"A/B Test My Memories — Audit the Recall","url":"https://vibeaxis.com/a-b-test-my-memories-audit-the-recall/"},
    {"key":"hub-basics","title":"Hub: AI Basics","url":"https://vibeaxis.com/ai-basics/"},
    {"key":"hub-real","title":"Hub: AI in Real Life","url":"https://vibeaxis.com/ai-in-real-life/"},
    {"key":"home","title":"VibeAxis — Home","url":"https://vibeaxis.com/"},
]

HELP = """\
vax-receipts — list/open VibeAxis receipts

Usage:
  vax-receipts list            Show all receipts
  vax-receipts hubs            Show hub-only entries
  vax-receipts open <key>      Open a receipt in your default browser
  vax-receipts help            Show help
"""

def list_all():
    for r in RECEIPTS:
        print(f"{r['key']:<11} — {r['title']}")

def list_hubs():
    for r in RECEIPTS:
        if r["key"].startswith("hub-"):
            print(f"{r['key']:<11} — {r['title']}")

def open_key(k: str):
    found = next((r for r in RECEIPTS if r["key"].lower() == k.lower()), None)
    if not found:
        print(f'No receipt for key "{k}".\nTry: vax-receipts list'); sys.exit(1)
    print(f"Opening: {found['title']}\n{found['url']}")
    webbrowser.open(found["url"], new=2, autoraise=True)

def main():
    args = sys.argv[1:]
    if not args:
        print(HELP); return
    cmd = args[0].lower()
    if cmd == "list": list_all()
    elif cmd == "hubs": list_hubs()
    elif cmd == "open":
        if len(args) < 2:
            print("Usage: vax-receipts open <key>"); sys.exit(1)
        open_key(args[1])
    else:
        print(HELP)

if __name__ == "__main__":
    main()

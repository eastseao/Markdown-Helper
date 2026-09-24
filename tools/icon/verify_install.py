import hashlib, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
STAGE = pathlib.Path("stage"); REPO = pathlib.Path(r"I:/mar/markdown-helper")
MAIN = REPO / "app/src/main"; ATEST = REPO / "app/src/flavorAtest"
D = ["mdpi","hdpi","xhdpi","xxhdpi","xxxhdpi"]
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
pairs, bad = [], []
for d in D:
    for n in ["ic_launcher_background","ic_launcher_foreground","ic_launcher_monochrome",
              "ic_launcher","ic_launcher_todo","ic_launcher_quicknote","ic_launcher_linkbox",
              "ic_launcher_share_into"]:
        pairs.append((STAGE/f"res/drawable-{d}/{n}.png", MAIN/f"res/drawable-{d}/{n}.png"))
    pairs.append((STAGE/f"res/drawable-{d}/ic_launcher.png", ATEST/f"res/drawable-{d}/ic_launcher.png"))
pairs.append((STAGE/"ic_launcher-web.png", MAIN/"ic_launcher-web.png"))
for s, t in pairs:
    ok = s.exists() and t.exists() and md5(s) == md5(t)
    if not ok: bad.append((s, t, s.exists(), t.exists()))
print(f"compared {len(pairs)} file pairs against the staged assets")
print("MISMATCH" if bad else "ALL IDENTICAL (byte-for-byte)")
for s,t,se,te in bad: print(f"  {s} -> {t}  src={se} dst={te}")
# also confirm no stale vector override survives
stale = sorted(str(p.relative_to(REPO)) for p in REPO.rglob("res/drawable*/ic_launcher*"))
print("\nremaining ic_launcher* under res/drawable*/:")
for p in stale: print("  ", p)

import subprocess, sys, os, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = r"I:\mar\markdown-helper"
GH = r"C:\Users\Administrator\.local\bin\gh.exe"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def run(args, cwd=REPO, env=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return r.returncode, r.stdout, r.stderr

rc, out, err = run([GH, "auth", "token"])
token = out.strip()
print(f"gh auth token: {'OK, len=' + str(len(token)) if rc == 0 and token else 'FAILED: ' + err.strip()}")
if not token:
    sys.exit(1)

import base64
b64 = base64.b64encode(f"x-access-token:{token}".encode()).decode()

env = dict(os.environ)
env["GIT_TERMINAL_PROMPT"] = "0"

# fetch first so we know if we are behind
rc, out, err = run([GIT, "fetch", "origin", "main"])
print(f"\nfetch: rc={rc} {err.strip()[:300]}")

rc, out, err = run([GIT, "status", "-sb"])
print(f"status: {out.strip()}")

rc, out, err = run([GIT, "log", "--oneline", "-1", "origin/main"])
print(f"origin/main before push: {out.strip()}")

rc, out, err = run([
    GIT, "-c", "credential.helper=",
    "-c", f"http.extraHeader=Authorization: Basic {b64}",
    "push", "origin", "main",
])
print(f"\npush: rc={rc}")
print("stdout:", out.strip()[:800])
print("stderr:", err.strip()[:800])

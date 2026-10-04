import json, os, subprocess, sys

BASE = os.environ.get("BASE_REF", "main")
MODEL = os.environ.get("AUDIT_MODEL", "gemini-2.5-flash")
FAIL_ON = {"high", "critical"}

diff = subprocess.run(
    ["git", "diff", f"origin/{BASE}...HEAD"],
    capture_output=True, text=True
).stdout[:60000]

if not diff.strip():
    open("report.md", "w").write("No code changes to audit.")
    sys.exit(0)

prompt = f"""You are a security and code-quality reviewer. Review this pull request diff.
Check for OWASP issues (injection, hardcoded secrets, broken auth, unsafe deserialization)
and quality problems (bugs, missing error handling).
Return ONLY a JSON array. Each item: {{"severity": "low|medium|high|critical",
"file": "...", "issue": "...", "fix": "..."}}. Return [] if there are no issues.

DIFF:
{diff}"""


def call_llm(prompt: str) -> str:
    # Swap this one function to use Claude, OpenAI, etc.
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    return resp.text


text = call_llm(prompt).strip().removeprefix("```json").removesuffix("```").strip()

try:
    findings = json.loads(text)
except json.JSONDecodeError:
    open("report.md", "w").write("Audit failed: could not parse model output.")
    sys.exit(1)  # fail closed

lines = ["## AI Code Audit", ""]
if not findings:
    lines.append("No issues found.")
else:
    lines += ["| Severity | File | Issue | Fix |", "|---|---|---|---|"]
    for f in findings:
        lines.append(f"| {f['severity']} | {f['file']} | {f['issue']} | {f['fix']} |")

blocked = [f for f in findings if f["severity"].lower() in FAIL_ON]
lines += ["", "**Result: FAIL**" if blocked else "**Result: PASS**"]
open("report.md", "w").write("\n".join(lines))
sys.exit(1 if blocked else 0)

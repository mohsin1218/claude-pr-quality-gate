import json, os, subprocess, sys, time

BASE = os.environ.get("BASE_REF", "main")
MODEL = os.environ.get("AUDIT_MODEL", "gemini-2.5-flash")
FAIL_ON = {"high", "critical"}


def write_report(text, code):
    open("report.md", "w").write(text)
    sys.exit(code)


diff = subprocess.run(
    ["git", "diff", f"origin/{BASE}...HEAD", "--", ".",
     ":(exclude)*.md", ":(exclude)*.txt"],
    capture_output=True, text=True
).stdout[:60000]

if not diff.strip():
    write_report("## AI Code Audit\n\nNo code changes to audit.\n\n**Result: PASS**", 0)

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


text, last_err = None, None
for attempt in range(3):
    try:
        text = call_llm(prompt)
        break
    except Exception as e:
        last_err = e
        print(f"Attempt {attempt + 1} failed: {e}", file=sys.stderr)
        time.sleep(5 * (attempt + 1))

if text is None:
    write_report(f"## AI Code Audit\n\nAudit could not run: `{type(last_err).__name__}`.\n\n**Result: FAIL (fail closed)**", 1)

text = text.strip().removeprefix("```json").removesuffix("```").strip()

try:
    findings = json.loads(text)
except json.JSONDecodeError:
    write_report("## AI Code Audit\n\nCould not parse model output.\n\n**Result: FAIL (fail closed)**", 1)

lines = ["## AI Code Audit", ""]
if not findings:
    lines.append("No issues found.")
else:
    lines += ["| Severity | File | Issue | Fix |", "|---|---|---|---|"]
    for f in findings:
        lines.append(f"| {f['severity']} | {f['file']} | {f['issue']} | {f['fix']} |")

blocked = [f for f in findings if f["severity"].lower() in FAIL_ON]
lines += ["", "**Result: FAIL**" if blocked else "**Result: PASS**"]
write_report("\n".join(lines), 1 if blocked else 0)

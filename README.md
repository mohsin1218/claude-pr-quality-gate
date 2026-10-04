# AI PR Quality Gate

A CI/CD gate that sends every pull request diff to an LLM for a security and code-quality review, then passes or fails the check based on severity rules. Failed audits block the merge.

## How it works

PR opened -> GitHub Action -> `git diff` -> LLM review (JSON findings) -> severity rules -> PASS/FAIL -> report posted on the PR

- **Fail closed:** unparseable model output fails the check
- **Configurable severity:** `FAIL_ON` in `scripts/audit.py` (default: high, critical)
- **Model-agnostic:** the LLM call is isolated in `call_llm()`, so switching to Claude, OpenAI or any other provider is a one-function change
- **Secrets:** API key stored as a GitHub Actions secret, never in code
- **Merge protection:** a branch ruleset requires the `audit` check to pass

## Demo

- [PR #1](../../pull/1): insecure code (hardcoded secrets, SQL injection) -> FAIL, merge blocked
- [PR #2](../../pull/2): clean code -> PASS

## Roadmap

- Slack / Teams / email notifications on failed audits
- Bitbucket Pipelines version
- SonarQube integration
- Audit report artifacts

## Setup

1. Add `GEMINI_API_KEY` (or your provider's key) as a repository secret
2. Keep `.github/workflows/ai-audit.yml` and `scripts/audit.py`
3. Add a ruleset requiring the `audit` status check

# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:59 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 12 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 31 unique findings (1 critical, 8 medium) / 31 occurrences / 31 raw records; 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-35cb15f77c04ca8e72b7` | CRITICAL | Data Flow: opener.open(request, timeout=3) | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-8e1fcdbf37b720508663` | MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | 1 | Security Scan |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-0471792d8071dda1f3e1` | LOW | openclaw: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own. | 1 | Harness Compatibility |
| ... | | *21 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| qa-troubleshooting-router | 77.8 | C | script-based | 65.0 | 85.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'qa-troubleshooting-router'
- [OK] **naming_convention**: Folder name 'qa-troubleshooting-router' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (149/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: agents, references, scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'qa-troubleshooting-router'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/qa-troubleshooting-router</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-42bbed569de08519db84`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-20e52348126864605101`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-25b9e14b8a708cdfcaad`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-ef3208957aadfc35762c`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-6c553d8093110466b9cd`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-8dcfef5b1c51cec99e20`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**1 errors, 2 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [CRIT] CRITICAL | Data Flow: opener.open(request, timeout=3) | <code>scripts/report-usage.py:31</code> |
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | <code>SKILL.md:1</code> |

<details>
<summary>View Details</summary>

**1. Data Flow: opener.open(request, timeout=3)**
- File: `scripts/report-usage.py:31`
- Check: `Tainted flow: 'request' from os.environ.get (line 24, credential/environment) → urllib.request.build_opener.open (network output) (TT3)`
- Finding ID: `SEF-35cb15f77c04ca8e72b7`
- Occurrence ID: `SEO-70e7e61d5f59ba1446da`
- Content: `method="POST",
    )
    opener = urllib.request.build_op...`
- Fix: Credentials or environment variables flow to a network sink. This is a high-confidence indicator of credential exfiltration. Never send credentials or environment variables over the network. Use secure credential stores and avoid transmitting secrets in request bodies or URLs.

**2. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 38 files for PII
- [OK] **pii_detection**: No PII detected in 38 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- [OK] **bandit**: Bandit: No security issues found

### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 35 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 35 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 38 file(s)

### ✅ C QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 77.8/100 (Grade: C)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 65.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 77.8/100 (Grade: C)

**Non-blocking findings: 11**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | No examples provided | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| ... | *1 more issues* | |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-c01706f7230456f9e0a0`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-fa415901b0e36d043187`
- Fix: Add explicit run_script() call examples

**3. No examples provided**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-0d2215183b14101ae2c2`
- Occurrence ID: `SEO-9795589dd699c8482525`
- Fix: Add example usage with code blocks

**4. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-10f3bb20a3387fd6cac3`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**5. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-05dff0075f7186f37030`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**6. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-885ad2dae19ddc7b8886`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**7. No '## Purpose' section**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-5a8c159f63770df553ad`
- Fix: Add purpose section to clarify use cases

**8. No mention of error handling or validation**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-3197d6ece13a7cb6fea1`
- Fix: Document expected errors and how to handle them

**9. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-5eaf53a85e15f371a602`
- Fix: Document dependencies, API keys, or setup needed

**10. No limitations documented**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-11bfd67b78f2ec4751e7`
- Fix: Add '## Limitations' section with known issues/constraints

*... and 1 more issues*

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | report-usage.py contains magic numbers | <code>/skills/library-20261118/G9/qa-troubleshooting-router/scripts/report-usage.py</code> |
| [LOW] LOW | report-usage.py may lack input validation | <code>/skills/library-20261118/G9/qa-troubleshooting-router/scripts/report-usage.py</code> |

<details>
<summary>View Details</summary>

**1. report-usage.py contains magic numbers**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/scripts/report-usage.py`
- Check: `magic_numbers`
- Finding ID: `SEF-d68f60454c13558f0b48`
- Occurrence ID: `SEO-8ec17d9c693de0afa419`
- Fix: Extract magic numbers to named constants

**2. report-usage.py may lack input validation**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/scripts/report-usage.py`
- Check: `no_input_validation`
- Finding ID: `SEF-432097ac656784bd33d7`
- Occurrence ID: `SEO-7eeacdd277706ef903f9`
- Fix: Add argument checks and raise descriptive errors

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 10**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | claude-code: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | copilot-cli: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [INFO] INFO | hermes: 1 files outside references/, templates/, assets/ and scripts/ (agents) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | hermes: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | openclaw: SKILL.md reads as 19,001 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | openclaw: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |
| [LOW] LOW | opencode: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own. | <code>/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. claude-code: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `CC-CODEX-POLICY`
- Finding ID: `SEF-3e26a8d9f731140a5fcd`
- Occurrence ID: `SEO-e364e745a6bd7598ae49`
- Fix: Also set disable-model-invocation: true (Claude Code, Copilot and OpenClaw honour it).

**2. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-518b3358b6c8bcd2adcc`

**3. copilot-cli: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `CP-CODEX-POLICY`
- Finding ID: `SEF-65282fbd03f4bb6a62e4`
- Occurrence ID: `SEO-91196baa44930e4fb70d`
- Fix: Also set disable-model-invocation: true (Claude Code, Copilot and OpenClaw honour it).

**4. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-efa62992a5692842c742`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**5. hermes: 1 files outside references/, templates/, assets/ and scripts/ (agents) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-e843862971441e2bf711`
- Occurrence ID: `SEO-dc35c3874968f7fb437d`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**6. hermes: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `HM-CODEX-POLICY`
- Finding ID: `SEF-404b53314b4118940459`
- Occurrence ID: `SEO-8e26570040683692b57d`
- Fix: No equivalent setting in Hermes.

**7. openclaw: SKILL.md reads as 19,001 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `OW-READ-BUDGET`
- Finding ID: `SEF-826e17e4f76b44a44951`
- Occurrence ID: `SEO-3de66e362f61e3df7057`
- Fix: Keep SKILL.md under about 15,000 characters (about 3,700 CJK characters); move detail into references/ files.

**8. openclaw: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `OW-CODEX-POLICY`
- Finding ID: `SEF-0471792d8071dda1f3e1`
- Occurrence ID: `SEO-4dc7dc822447dcae35f8`
- Fix: Also set disable-model-invocation: true (Claude Code, Copilot and OpenClaw honour it).

**9. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-ae48715dbc0d5db4048c`

**10. opencode: agents/openai.yaml implicit-invocation policy is Codex-only: here the model can still use this skill on its own.**
- File: `/skills/library-20261118/G9/qa-troubleshooting-router/SKILL.md`
- Check: `OC-CODEX-POLICY`
- Finding ID: `SEF-dc384ffb37999d190eca`
- Occurrence ID: `SEO-84c29844335da75352b0`
- Fix: No equivalent setting in OpenCode.

</details>


---
*Generated by SkillEvaluator*
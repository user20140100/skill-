# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:01 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 9 |
| ❌ Failed | 4 |
| ⚠️ Incomplete | 1 |
| Total Issues | 19 unique findings (4 high, 3 medium) / 20 occurrences / 19 raw records; 1 error and 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-bbc961d935bd7baa75c1` | HIGH | Personal macOS user path: /Users/malanjun/ — 2 occurrences (SKILL.md lines 450, 453) | 2 | PII Scan |
| `SEF-1b78e439199206c2106c` | HIGH | Invalid name format: 'BizSolution' (lowercase/numbers/hyphens only) | 1 | QUALITY |
| `SEF-d346c81e06e71927e255` | HIGH | Tool Misuse: rm -rf ./BizSolution)", | 1 | Security Scan |
| `SEF-e5ff8e74d20ec6f6e280` | HIGH | Field 'name': Value error, Skill name 'BizSolution' must be in kebab-case format (lowercase letters, numbers, and hyphens only, starting with a letter) | 1 | Schema &amp; Repository Governance |
| `SEF-7964b650b0b3e5d1d6b3` | MEDIUM | Skill name not following convention: 'BizSolution' | 1 | QUALITY |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| `SEF-378f24adfec67572e606` | LOW | No troubleshooting section documented | 1 | QUALITY |
| `SEF-4a6560f4aec006f302f9` | LOW | No prerequisites/requirements documented | 1 | QUALITY |
| ... | | *9 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| BizSolution | 78.8 | C | resource-based | 75.0 | 75.0 | 75.0 | 100.0 |

## Results

### ❌ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

**1 errors, 1 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Field 'name': Value error, Skill name 'BizSolution' must be in kebab-case format (lowercase letters, numbers, and hyphens only, starting with a letter) | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Field 'name': Value error, Skill name 'BizSolution' must be in kebab-case format (lowercase letters, numbers, and hyphens only, starting with a letter)**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `frontmatter_field`
- Finding ID: `SEF-e5ff8e74d20ec6f6e280`
- Occurrence ID: `SEO-2ff9d07fdad3240e255c`
- Fix: Fix the 'name' field in frontmatter according to schema requirements

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**Incomplete scanners:** skillspector

**2 errors, 0 warnings**

**Execution errors:**

- ❌ skillspector JSON field 'analysis_completeness' reports incomplete analysis (status 'partial'): SKILL.md:453 [reference_resolution; reference_missing]; examples/case-delivery-transparency.md [static; static_parse_limit; analyzers=static_patterns_tool_misuse]; security scan did not complete

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Tool Misuse: rm -rf ./BizSolution)", | <code>.claude/settings.local.json:4</code> |

<details>
<summary>View Details</summary>

**1. Tool Misuse: rm -rf ./BizSolution)",**
- File: `.claude/settings.local.json:4`
- Check: `Tool Parameter Abuse (TM1)`
- Finding ID: `SEF-d346c81e06e71927e255`
- Occurrence ID: `SEO-fbbe9400f26a43bcc39f`
- Content: `{
  "permissions": {
    "allow": [
      "Bash(rm -rf ./...`
- Fix: Tool parameters are crafted to achieve unintended or unsafe behavior. Parameter abuse can bypass intended safety checks (e.g. shell=True, --force, dangerous glob patterns). Validate all tool parameters against an allowlist. Reject dangerous parameter values (shell=True, --force, -rf /) and use safe defaults.

</details>


### ❌ PII Scan
*Detect PII and local identifiers*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Personal macOS user path: /Users/malanjun/ — 2 occurrences (SKILL.md lines 450, 453) | <code>SKILL.md:450</code> |

<details>
<summary>View Details</summary>

**1. Personal macOS user path: /Users/malanjun/ — 2 occurrences (SKILL.md lines 450, 453)**
- File: `SKILL.md:450`
- Check: `personal_paths`
- Finding ID: `SEF-bbc961d935bd7baa75c1`
- Occurrence ID: `SEO-a46513c3d9abdc0cf86a`
- Content: `skill-creator search-skill --pwd "/Users/malanjun/Documen...`
- Fix: Use generic path like /path/to/file or environment variable like $HOME

</details>


### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- [OK] **code_file_discovery**: No code files found - code risk analysis is not applicable

### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 3 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 3 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- All checks passed

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>examples/case-delivery-transparency.md:347</code> |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `examples/case-delivery-transparency.md:347`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-28ce4acaf4c040fdf649`
- Content: `| 场景完整 | ⚠️ 部分 | 已覆盖 5 个主场景；「客户退货/拒收」场景待业务补充 |`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

</details>


### ❌ C QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 78.8/100 (Grade: C)** | Skill Type: resource-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 75.0 | 35% |
| Discoverability | 75.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

**1 errors, 9 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Invalid name format: 'BizSolution' (lowercase/numbers/hyphens only) | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [MED] MEDIUM | Skill name not following convention: 'BizSolution' | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Invalid name format: 'BizSolution' (lowercase/numbers/hyphens only)**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-1b78e439199206c2106c`
- Occurrence ID: `SEO-661a625ea5cb724edc70`
- Fix: Use only lowercase letters, numbers, and hyphens

**2. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-fe7ec7e49b50c08f3ba3`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**3. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-4a2842a1f9d6b27b2408`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**4. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-56a73d1f48eeaac28a5c`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**5. No '## Purpose' section**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-136f81480d14cd58d16f`
- Fix: Add purpose section to clarify use cases

**6. Skill name not following convention: 'BizSolution'**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-7964b650b0b3e5d1d6b3`
- Occurrence ID: `SEO-a735b5f89bcf05ef6149`
- Fix: Use lowercase with hyphens: my-skill-name

**7. No mention of error handling or validation**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-eed151f55a7828f76a02`
- Fix: Document expected errors and how to handle them

**8. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-e1628733154130e5e9a8`
- Fix: Document dependencies, API keys, or setup needed

**9. No limitations documented**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-a10d2f72b296a8650e05`
- Fix: Add '## Limitations' section with known issues/constraints

**10. No troubleshooting section documented**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-047440a442465608bc4a`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 5**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [INFO] INFO | hermes: 3 files outside references/, templates/, assets/ and scripts/ (.claude, examples, outputs) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [LOW] LOW | openclaw: SKILL.md reads as 28,487 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup. | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G4/BizSolution/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-b564a0798356717b504d`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-f92498a8d8ffd122e745`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 3 files outside references/, templates/, assets/ and scripts/ (.claude, examples, outputs) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-334631a9ae287f4a399a`
- Occurrence ID: `SEO-195d933c136e2bfd6f6e`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. openclaw: SKILL.md reads as 28,487 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup.**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `OW-READ-BUDGET`
- Finding ID: `SEF-c0ba0be3f915857375c6`
- Occurrence ID: `SEO-88e507e842dbee24764f`
- Fix: Keep SKILL.md under about 15,000 characters (about 3,700 CJK characters); move detail into references/ files.

**5. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G4/BizSolution/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-e1caab75fb3a86eb5468`

</details>


---
*Generated by SkillEvaluator*
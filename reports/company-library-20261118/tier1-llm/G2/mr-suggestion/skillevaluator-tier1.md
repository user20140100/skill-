# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 03:07 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 14 |
| Validators Run | 14 |
| ✅ Passed | 13 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 38 unique findings (3 high, 13 medium) / 38 occurrences / 38 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-77850483b8a7663bd842` | HIGH | Preserving the Authorization header across redirects without origin validation is dangerous because a redirect from the | 1 | Security Scan |
| `SEF-9138eb12abd8618b0605` | HIGH | Disabling TLS certificate/hostname verification is a real risk because the script sends an authenticated GitLab API requ | 1 | Security Scan |
| `SEF-b7d35be7d631bdb0fc94` | HIGH | MCP Tool Poisoning: The description claims the skill can both fetch and apply GitLab MR code review suggestions, and also suggests it can be | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-45e27c4438ce58ede236` | MEDIUM | The batch-apply flow instructs the agent to filter high-priority suggestions, group them by file, apply replacements fro | 1 | Security Scan |
| `SEF-61d5a466f8b0ac28b42f` | MEDIUM | MCP Least Privilege: The skill instructs the agent to locate and run a Python script that performs network requests and reads a configuration | 1 | Security Scan |
| `SEF-631d43cdffa56141fe88` | MEDIUM | The file-application instructions allow the agent to use fuzzy matching, ignore whitespace differences, or prompt the us | 1 | Security Scan |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| ... | | *28 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| mr-suggestion | 82.0 | B | script-based | 70.0 | 95.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'mr-suggestion'
- [OK] **naming_convention**: Folder name 'mr-suggestion' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (160/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'mr-suggestion'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G2/mr-suggestion</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | Unexpected 'config.example.json' in skill root | <code>/skills/library-20261118/G2/mr-suggestion/config.example.json</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G2/mr-suggestion`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-24683591113d2a833973`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-473c7958df12d7f7ad16`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-1d34f184052c0588937a`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Unexpected 'config.example.json' in skill root**
- File: `/skills/library-20261118/G2/mr-suggestion/config.example.json`
- Check: `unexpected_file`
- Finding ID: `SEF-14347db996d4e3d1f519`
- Occurrence ID: `SEO-9638869bdb18820407b0`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**5. Author not specified in metadata**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-9562b580edb449c7a0bd`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-f1179173be7e7d1c7090`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**3 errors, 7 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.<br><strong>LLM verification:</strong> True positive (high confidence)<br>Reasoning: The skill directs execution of a network/file-accessing Python script but declares no allowed-tools or permissions, so its capability scope is unconstrained.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:1</code> |
| [HIGH] HIGH | MCP Tool Poisoning: The description claims the skill can both fetch and apply GitLab MR code review suggestions, and also suggests it can be<br><strong>LLM verification:</strong> False positive (medium confidence)<br>Reasoning: The script is only the retrieval step; the broader SKILL.md workflow includes later apply steps, so the description does not materially overstate the skill as a whole.<br>Reported severity: HIGH; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:1</code> |
| [HIGH] HIGH | Disabling TLS certificate/hostname verification is a real risk because the script sends an authenticated GitLab API requ<br><strong>LLM verification:</strong> True positive (high confidence)<br>Reasoning: The code explicitly disables TLS hostname and certificate verification while sending an auth token, enabling MITM or token leakage.<br>Reported severity: HIGH; only high-confidence false positives are downgraded to INFO by verification. | <code>scripts/fetch_suggestions.py:24</code> |
| [HIGH] HIGH | Preserving the Authorization header across redirects without origin validation is dangerous because a redirect from the <br><strong>LLM verification:</strong> True positive (high confidence)<br>Reasoning: The custom redirect handler preserves the Authorization header across redirects without origin validation, allowing token leakage to a different host.<br>Reported severity: HIGH; only high-confidence false positives are downgraded to INFO by verification. | <code>scripts/fetch_suggestions.py:31</code> |
| [MED] MEDIUM | MCP Least Privilege: The skill instructs the agent to locate and run a Python script that performs network requests and reads a configuration<br><strong>LLM verification:</strong> True positive (high confidence)<br>Reasoning: The skill instructs the agent to locate and run a script using broad project/global filename search with no declared tool permissions, creating a script-hijack and least-privilege gap.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:1</code> |
| [MED] MEDIUM | The activation description includes broad phrases such as "代码审核" and "wants to fix code based on review feedback" withou<br><strong>LLM verification:</strong> Uncertain (medium confidence)<br>Reasoning: The trigger phrases are broad, but the workflow still requires an MR IID and local configuration, so the practical security impact is limited and context-dependent.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:3</code> |
| [MED] MEDIUM | The batch-apply flow instructs the agent to filter high-priority suggestions, group them by file, apply replacements fro<br><strong>LLM verification:</strong> True positive (high confidence)<br>Reasoning: Applying remote suggestion content in batch without mandatory review or warnings can turn a compromised or malicious endpoint into remote-controlled source modification.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:140</code> |
| [MED] MEDIUM | The file-application instructions allow the agent to use fuzzy matching, ignore whitespace differences, or prompt the us<br><strong>LLM verification:</strong> True positive (medium confidence)<br>Reasoning: Fuzzy matching and whitespace-insensitive edits can apply remote content to unintended code locations without explicit confirmation, increasing risk.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:153</code> |
| [MED] MEDIUM | Sending a GitLab auth token to a fully arbitrary user-configured API base URL is a vulnerability when the config file ca<br><strong>LLM verification:</strong> True positive (medium confidence)<br>Reasoning: The script sends the auth token to an arbitrary configured base URL without scheme/origin validation; combined with TLS and redirect issues this can leak credentials if the config is tampered with.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>scripts/fetch_suggestions.py:60</code> |
| [INFO] INFO | Lines L54, L68, L89, and L92 print Chinese-language error messages directly to the user. This can force a specific langu<br><strong>LLM verification:</strong> False positive (high confidence)<br>Reasoning: Chinese-language user messages are a localization or usability concern, not a security or PII issue.<br>Verifier recorded a downgrade to INFO; reported severity: INFO. | <code>scripts/fetch_suggestions.py:54</code> |

<details>
<summary>View Details</summary>

**1. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

**2. MCP Tool Poisoning: The description claims the skill can both fetch and apply GitLab MR code review suggestions, and also suggests it can be**
- File: `SKILL.md:1`
- Check: `Unknown (TP4)`
- Finding ID: `SEF-b7d35be7d631bdb0fc94`
- Occurrence ID: `SEO-9d525571318311b4e772`
- Fix: The description claims the skill can both fetch and apply GitLab MR code review suggestions, and also suggests it can be used when the user wants to fix code based on review feedback. The supplied code chunk only performs retrieval and output of suggestion data. There is no implementation of applying diffs, editing source files, staging changes, or resolving MR suggestions. This is a material overstatement of the skill's behavior. The script also preserves the Authorization header across redirects and disables TLS hostname/certificate validation, which are security-sensitive behaviors not reflected in the declared purpose, although the main mismatch is the claimed `apply` capability. Trigger metadata is also inconsistent: `Triggers: []` while the description lists several trigger phrases, but this is a metadata issue rather than a code behavior mismatch. Update the skill description to accurately reflect all capabilities, or remove undeclared functionality from the implementation.

**3. Disabling TLS certificate/hostname verification is a real risk because the script sends an authenticated GitLab API requ**
- File: `scripts/fetch_suggestions.py:24`
- Check: `Unknown (SDI-2)`
- Finding ID: `SEF-9138eb12abd8618b0605`
- Occurrence ID: `SEO-e57be3ec353748903b66`
- Fix: Disabling TLS certificate/hostname verification is a real risk because the script sends an authenticated GitLab API request with an auth token. If an attacker can intercept or redirect the network path (MITM), the client will accept any TLS endpoint without validating its identity. In this skill's context, this can leak MR review suggestions, tamper with the JSON response, or potentially lead to malicious suggestions being applied if downstream automation trusts the output. Remove the custom SSL context that sets check_hostname=False and verify_mode=CERT_NONE. Use the default ssl.create_default_context() and verify the server certificate and hostname. If a corporate self-managed GitLab requires a custom CA, provide an explicit opt-in CA bundle file or environment variable while still keeping hostname verification enabled.

**4. Preserving the Authorization header across redirects without origin validation is dangerous because a redirect from the **
- File: `scripts/fetch_suggestions.py:31`
- Check: `Unknown (SDI-2)`
- Finding ID: `SEF-77850483b8a7663bd842`
- Occurrence ID: `SEO-f2cba9ce018f6acc9f4c`
- Fix: Preserving the Authorization header across redirects without origin validation is dangerous because a redirect from the configured API endpoint can send the token to a different host. If api_base_url is attacker-controlled or an intermediate response is tampered with, the auth token can be exfiltrated. The custom handler also makes redirects more sensitive because it explicitly retains AUTHORIZATION on redirected requests. Do not preserve Authorization across redirects unless the redirect target is strictly validated as the same origin (scheme, host, port) or an explicitly allow-listed host. Prefer disabling redirects for authenticated requests and requiring the configured endpoint to be the final URL, or reject redirects to cross-origin hosts.

**5. MCP Least Privilege: The skill instructs the agent to locate and run a Python script that performs network requests and reads a configuration**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-61d5a466f8b0ac28b42f`
- Occurrence ID: `SEO-f2454c5a18c306fa72d0`
- Fix: The skill instructs the agent to locate and run a Python script that performs network requests and reads a configuration file containing an authentication token. However, it declares no allowed tools or permissions. This creates a control gap: the agent may execute network and file operations without explicit platform authorization or user awareness. The risk is increased by the script discovery rules, which include searching common project paths and even globally for fetch_suggestions.py. If an attacker controls the repository or can influence project files, they could place a malicious script with the same name in a searched location and cause it to be executed. Add explicit tool scopes and permission requirements such as network access, file read/write, and Python execution. Require the agent to request user confirmation before running scripts. Restrict script execution to the canonical skill package path and disable broad project-wide or global filename searches. Validate the resolved script path against a trusted allowlist and checksum/signature. Require explicit user approval before using any token from .mr-suggestion.json. Consider replacing inline scripts with a verified platform tool or sandboxed network client.

**6. The activation description includes broad phrases such as "代码审核" and "wants to fix code based on review feedback" withou**
- File: `SKILL.md:3`
- Check: `Unknown (SQP-1)`
- Finding ID: `SEF-c00d4d7cb8edef3582b3`
- Occurrence ID: `SEO-56d1015ce7ee4930ca6b`
- Fix: The activation description includes broad phrases such as "代码审核" and "wants to fix code based on review feedback" without negative examples or constraints limiting activation to GitLab MR suggestion workflows (e.g., requiring an MR IID and `.mr-suggestion.json`), which may trigger the skill for ordinary code-review requests that are not MR-suggestion specific. Tighten the trigger scope by requiring explicit MR/GitLab suggestion context and add negative examples or exclusion conditions.

**7. The batch-apply flow instructs the agent to filter high-priority suggestions, group them by file, apply replacements fro**
- File: `SKILL.md:140`
- Check: `Unknown (SQP-2)`
- Finding ID: `SEF-45e27c4438ce58ede236`
- Occurrence ID: `SEO-f8cce28e0b798d88f464`
- Fix: The batch-apply flow instructs the agent to filter high-priority suggestions, group them by file, apply replacements from remote suggestion content, and report results. It does not warn the user that remote improved_code content is being written into the repository. If the suggestions endpoint, configuration, or returned JSON is compromised, this can become a remote-controlled source-code modification path. The lack of user warnings and mandatory review/approval makes the skill more exploitable, especially when multiple files are modified in a batch. Require explicit user confirmation before any batch modification. Show a diff or patch preview for every suggested change and require the user to approve each change or approve a batch only after reviewing a summary. Warn that improved_code comes from a remote service and may be incorrect or malicious. Apply changes on a separate branch, create a backup or snapshot, and never auto-commit, auto-merge, or auto-push. Validate file paths are inside the repository and restrict edits to source files relevant to the MR.

**8. The file-application instructions allow the agent to use fuzzy matching, ignore whitespace differences, or prompt the us**
- File: `SKILL.md:153`
- Check: `Unknown (SQP-2)`
- Finding ID: `SEF-631d43cdffa56141fe88`
- Occurrence ID: `SEO-953f6eb44a994cc6e61d`
- Fix: The file-application instructions allow the agent to use fuzzy matching, ignore whitespace differences, or prompt the user when exact existing_code is not found. This can lead to silent or semi-silent local code modifications based on remote content. Missing warnings here increase the likelihood of applying an incorrect replacement to the wrong code region, which could introduce functional defects or malicious changes, especially if the remote suggestion content is adversarial. Prohibit automatic fuzzy replacement without explicit user confirmation. Default to exact matching only. When fuzzy matching is allowed, present the proposed old and new code, line context, and diff for approval. Warn that code changes are based on remote suggestions and must be reviewed. Require user confirmation before editing files with ambiguous matches. Use file locks, backups, and a change log to allow rollback.

**9. Sending a GitLab auth token to a fully arbitrary user-configured API base URL is a vulnerability when the config file ca**
- File: `scripts/fetch_suggestions.py:60`
- Check: `Unknown (SDI-2)`
- Finding ID: `SEF-bd90b0ff301610366b18`
- Occurrence ID: `SEO-b6ab068c8e4e7da77bf5`
- Fix: Sending a GitLab auth token to a fully arbitrary user-configured API base URL is a vulnerability when the config file can be modified by an untrusted source. Combined with disabled TLS validation and redirect header preservation, an attacker can direct requests to a malicious endpoint and receive or replay the authenticated request. However, the config is loaded from a local .mr-suggestion.json file, so exploitation generally requires local/project file compromise or user misconfiguration. Validate api_base_url: require https, enforce exact origin validation, allow-list expected GitLab hosts or self-managed endpoints, and reject suspicious URLs. Store credentials securely or use environment variables with least-privilege tokens. At minimum, do not allow arbitrary endpoints silently and do not disable TLS verification.

**10. Lines L54, L68, L89, and L92 print Chinese-language error messages directly to the user. This can force a specific langu**
- File: `scripts/fetch_suggestions.py:54`
- Check: `Unknown (SQP-3)`
- Finding ID: `SEF-d7adcc63b155ce9230a0`
- Occurrence ID: `SEO-6f26b1f3691391dd61e8`
- Fix: Lines L54, L68, L89, and L92 print Chinese-language error messages directly to the user. This can force a specific language on users without providing a way to select or opt into another locale. If Chinese is intentionally required for this skill, add a clear note or configuration/locale option. Add locale/user-language selection or provide English fallback messages, or document that the skill is intended for Chinese-speaking users.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 3 files for PII
- [OK] **pii_detection**: No PII detected in 3 files (emails, SSNs, phone numbers, paths)

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

- [OK] **dead_links_scan**: Checking 1 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 1 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 3 file(s)

### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 82.0/100 (Grade: B)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 70.0 | 35% |
| Discoverability | 95.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 82.0/100 (Grade: B)

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-5835812bc23a0cfc1315`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-1041f196b28b2b834229`
- Fix: Add explicit run_script() call examples

**3. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-e24122c3dc60268029bf`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**4. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-6e4deb9e80d53b2c50b3`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**5. No '## Purpose' section**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-4456b8345c6230224303`
- Fix: Add purpose section to clarify use cases

**6. No mention of error handling or validation**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-0bf2310dc5b936d24852`
- Fix: Document expected errors and how to handle them

**7. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-6b3d526932278f2a86c4`
- Fix: Document dependencies, API keys, or setup needed

**8. No limitations documented**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-af6fe219a7329daf3f53`
- Fix: Add '## Limitations' section with known issues/constraints

**9. No troubleshooting section documented**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-46be2314cae65774f3c0`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | fetch_suggestions.py contains magic numbers | <code>/skills/library-20261118/G2/mr-suggestion/scripts/fetch_suggestions.py</code> |

<details>
<summary>View Details</summary>

**1. fetch_suggestions.py contains magic numbers**
- File: `/skills/library-20261118/G2/mr-suggestion/scripts/fetch_suggestions.py`
- Check: `magic_numbers`
- Finding ID: `SEF-a1b39f2181efa8ce7e6c`
- Occurrence ID: `SEO-b523294132c7f8baaa5f`
- Fix: Extract magic numbers to named constants

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [INFO] INFO | hermes: 1 files outside references/, templates/, assets/ and scripts/ (config.example.json) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-fc79debb1f0585776db7`

**2. hermes: 1 files outside references/, templates/, assets/ and scripts/ (config.example.json) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-552d5ec6faa883b6a760`
- Occurrence ID: `SEO-ec831796903293562cff`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**3. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-75e5fd0ba2c9b7149d05`

</details>


### ✅ RUBRIC_EVAL
*LLM-as-Judge qualitative evaluation across 9 criteria (description clarity, instruction quality, trigger simulation, etc.)*

- [OK] **rubric_eval**: LLM Rubric Score: 78.2/100

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | [9/10] Description is clear, specific, and explains WHEN to use the skill | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | [8/10] Instructions are easy to follow with clear action steps | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | [7/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | [8/10] All necessary information is present (purpose, scripts, parameters) | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | [8/10] Skill scope is well-defined (clear boundaries, not too broad/narrow) | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | [9/10] Documentation uses professional, consistent tone and formatting | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | [7/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |
| [LOW] LOW | [7/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | <code>/skills/library-20261118/G2/mr-suggestion/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. [9/10] Description is clear, specific, and explains WHEN to use the skill**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_description_clarity`
- Finding ID: `SEF-957e47d4db212b70e418`
- Occurrence ID: `SEO-05e96109bd65de2e8d9b`
- Fix: It explicitly names GitLab MR review suggestions and includes useful trigger phrases in English and Chinese.

**2. [8/10] Instructions are easy to follow with clear action steps**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_instruction_clarity`
- Finding ID: `SEF-65d7a4e2d6ce63107155`
- Occurrence ID: `SEO-60278a1af1fecbcd2551`
- Fix: The workflow is well structured with script location, commands, parameters, and application steps. It could clarify how to obtain the MR IID when the user does not provide it.

**3. [7/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_example_quality`
- Finding ID: `SEF-e970e771a45079b3f175`
- Occurrence ID: `SEO-9baa58f612ecef6af24d`
- Fix: Config, command, output, and summary examples are useful. More user-query examples would better demonstrate trigger variations.

**4. [8/10] All necessary information is present (purpose, scripts, parameters)**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_documentation_completeness`
- Finding ID: `SEF-6bea62275f1974815c70`
- Occurrence ID: `SEO-8a6eb04f52683dad25a6`
- Fix: Purpose, configuration, script path, parameters, output schema, and workflow are documented. Details about obtaining project_id and auth_token are limited.

**5. [8/10] Skill scope is well-defined (clear boundaries, not too broad/narrow)**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_scope_definition`
- Finding ID: `SEF-48e39f97470f95892d1f`
- Occurrence ID: `SEO-b0b80ce4c5fcc0fd45ae`
- Fix: The scope is clearly limited to GitLab MR code review suggestions. The phrase 'code review suggestions' is slightly broad but contextualized by GitLab MR.

**6. [9/10] Documentation uses professional, consistent tone and formatting**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_professional_tone`
- Finding ID: `SEF-3a0ce9e26fc0e46c5205`
- Occurrence ID: `SEO-9fc5c2873469d75b748b`
- Fix: The tone is clear and professional, with consistent headings, tables, and code blocks. Mixed English and Chinese is appropriate for the stated use case.

**7. [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives?**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_trigger_simulation`
- Finding ID: `SEF-e43c4d52cf365a74f0f0`
- Occurrence ID: `SEO-81f8f6a7794dcf80739f`
- Fix: Queries about MR suggestions, GitLab review feedback, and Chinese terms should trigger correctly. Generic local code review or GitHub PR requests are less likely to be misrouted, though 'code review suggestions' could be slightly broad.

**8. [7/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance.**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_workflow_completeness`
- Finding ID: `SEF-73c5c3cb2720900ea889`
- Occurrence ID: `SEO-17c69e3612fd3eabf208`
- Fix: The workflow covers fetching, displaying, prioritizing, applying, and batch fixing. It lacks guidance for missing MR IID, MR URL parsing, and post-fix validation such as tests or builds.

**9. [7/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate?**
- File: `/skills/library-20261118/G2/mr-suggestion/SKILL.md`
- Check: `rubric_error_handling_quality`
- Finding ID: `SEF-ebf53579d652f6e53a47`
- Occurrence ID: `SEO-6c0ed440434244a094f2`
- Fix: Missing config, empty suggestions, missing file paths, and fuzzy match failures are handled realistically. API authentication, network, and GitLab project errors are not sufficiently documented.

</details>


---
*Generated by SkillEvaluator*
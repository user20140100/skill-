---
name: Create-testcases
description: >-
  Create or optimize test cases, test points, QA mind maps, and similar QA
  outputs from Figma and local code. Use when the user asks in English or
  Chinese for things like generate test cases, optimize test cases, supplement
  test points, 输出测试用例, 优化测试用例, 补充测试点, 输出思维导图, or 结合 Figma 和代码写测试用例. First
  collect any missing inputs: Figma 地址, 代码路径, 读取 Figma 全模块还是部分模块, 是否提供测试用例模板,
  and 是否还需要思维导图. Treat Figma and code as read-only sources by default.
author: binchunmei
version: 0.0.1
---

# Generate Test Cases

## Overview

Generate test cases from design and implementation together instead of relying on only one source.
Collect missing inputs first, read Figma and code in read-only mode by default, then output test cases, a mind map, or both in the user's template or a default structure.

## Intake

Before reading any source, reuse information already present in the thread and ask only for the missing items below.

Use concise questions that cover:

1. Figma address or design source path
2. Code path or repo path
3. Scope
   - Read all Figma modules
   - Read only selected modules, pages, frames, or titles
4. Template
   - Whether the user provides a test case template
   - If provided, where the file is and whether its format must stay unchanged
5. Deliverables
   - Test cases only
   - Mind map only
   - Test cases and mind map together
   - If a mind map is needed, what format is preferred

If the user says to read only part of Figma, ask for the exact module names when the scope is still ambiguous.
If the user wants a mind map but does not specify a format, default to a hierarchical Markdown outline that is easy to copy, review, and convert.

## Read-Only Rules

Treat Figma and code as read-only inputs by default.

- Do not modify the Figma source document.
- Do not modify source code while generating test cases.
- Do not modify a user-provided template unless the user explicitly asks to write output into that file.
- If you do write into a template file, preserve its original format, columns, order, and style.
- If both test cases and a mind map are requested, derive them from the same reviewed scope instead of reading sources twice.

## Workflow

### 1. Confirm Scope

Determine whether the user wants:

- Full-module reading: inspect all relevant Figma modules in scope.
- Partial-module reading: inspect only the named modules, pages, sections, frames, or titles.

Do not expand a partial scope on your own.

### 2. Read Figma Requirements

Extract user-visible and test-relevant information from the requested Figma scope:

- Module names and page structure
- Buttons, icons, entry points, tabs, and menus
- Visible copy and labels
- Default states
- Empty, error, loading, offline, disabled, and success states
- User flows and page transitions
- Different role or device variants when shown

Prefer exact visible text from Figma when the user asks for copy-level checks.

### 3. Read Code Logic

Read the relevant code path in read-only mode and use it to verify or supplement:

- Actual feature gates and enable conditions
- Default visibility and default state logic
- Branches caused by data, permissions, plugin enablement, network, or account status
- Retry, loading, refresh, and failure behavior
- Sorting, filtering, timing windows, and state transitions
- User-visible results after clicks or submissions

### 4. Merge Design and Code

Use Figma for intended UI content and layout coverage, and use code for implemented behavior and logic details.

When Figma and code differ:

- Do not silently ignore the mismatch.
- Note the conflict in the output or assumptions.
- Prefer the user's explicit instruction if they already defined the source of truth.

### 5. Generate Test Cases

Decompose cases by module, state, and user action.

At minimum, cover what is relevant in the requested scope:

- Functional checks
- State and copy checks
- Default-state checks
- Boundary and exception checks
- Stability, reliability, or performance checks when the user asks for them

Write cases with these rules:

- Keep test names short and clear.
- Make preconditions actionable for a real tester.
- Put steps on separate lines when the target template supports multi-line content.
- Make expected results correspond to the steps and focus on user-visible outcomes.
- Split independent scenarios into separate cases instead of merging unrelated actions.
- When behavior differs by platform, plugin, role, device, layout, or state, split them into separate cases.
- Prefer exact visible copy, button names, and labels when the source shows them.
- Avoid internal-only wording in titles and expectations unless the user explicitly wants protocol or parameter coverage.

### 6. Generate the Mind Map

If the user requests a mind map, generate it from the final test-case structure rather than inventing a separate classification.

Build the hierarchy in this order unless the user asks for another structure:

1. Product or feature name
2. Module
3. Submodule, page, state, or flow
4. Test focus
5. Representative test point or case title

Mind map rules:

- Keep one node per line.
- Use short node text, not paragraphs.
- Keep sibling granularity consistent.
- Reflect important branches such as platform variants, role variants, empty states, and exception states.
- If the user wants the mind map to mirror the test cases, keep the node names aligned with the final case grouping.

### 7. Use the Template

If the user provides a template:

- Fill that template first.
- Keep its format unchanged unless the user explicitly asks for restructuring.
- Follow its existing columns, wording style, and field order.

If the user does not provide a template, use a simple default structure such as:

- Module
- Test Case Name
- Preconditions
- Steps
- Expected Result
- Priority
- Test Type
- Notes

If the user wants a mind map and does not provide a template or target format, use a clean Markdown outline such as:

```md
# Feature
## Module A
### State 1
- Case A1
- Case A2
### State 2
- Case A3
## Module B
### Flow 1
- Case B1
```

## Output Rules

Include enough detail for execution, but do not pad cases with vague statements.

Prefer:

- Exact button and copy checks when the source shows them
- User-visible expected results instead of internal command descriptions
- Separate cases for different modules, different platforms, different states, and different roles when behavior changes
- A mind map that matches the final case grouping instead of a disconnected summary tree

If access to Figma or code is incomplete, state what was available, what was missing, and how that limits the result.

For complex requests, read [references/quality-checklist.md](references/quality-checklist.md) before finalizing the output.

## Quality Checks

Before final output, verify these points:

1. Every requested module is covered, and no unrequested module was added without permission.
2. Buttons, visible copy, tabs, icons, and default states are covered where relevant.
3. Empty, loading, offline, error, disabled, and success states are covered where the source shows them or code supports them.
4. Different platforms, roles, devices, layouts, or plugin states are split when behavior changes.
5. Preconditions are user-actionable, not vague environment statements.
6. Steps and expected results are aligned and describe user-visible outcomes.
7. If a template was provided, the output keeps its structure unchanged.
8. If a mind map was requested, its hierarchy matches the final test-case grouping.

## Example Questions

Use short prompts like:

- `请提供 Figma 地址。`
- `请提供代码路径。`
- `需要读取 Figma 全模块，还是只读取部分模块？如果是部分模块，请列出模块标题或页面范围。`
- `是否提供测试用例模板？如果提供，请给出文件路径，并说明是否需要严格保持原格式。`
- `是否还需要同时输出思维导图？如果需要，请说明导图格式要求。`

Ask only for the missing items instead of repeating everything already provided.

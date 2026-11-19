# Quality Checklist

Use this checklist when the request is large, multi-module, or requires both test cases and a mind map.

## Source Coverage

1. Confirm the exact Figma scope.
2. Confirm the exact code path.
3. Confirm whether the user wants all modules or only named modules.
4. Confirm whether a template must be preserved.
5. Confirm whether a mind map is also required.

## Test-Case Coverage

Check whether the final output covers:

- Main flow
- Default state
- Empty state
- Loading state
- Offline or network failure state
- Error or exception state
- Disabled or unavailable state
- Success or recovery state
- Platform differences
- Role differences
- Device differences
- Layout differences
- Multi-language differences when requested
- Stability, reliability, and performance when requested

## Writing Rules

- Use short and clear test names.
- Use actionable preconditions.
- Keep one logical scenario per case.
- Keep steps and expected results aligned.
- Prefer user-visible results.
- Use exact visible copy when the source provides it.
- Avoid internal parameter names in user-facing case titles unless explicitly requested.

## Mind-Map Rules

- Build the mind map from the final test-case grouping.
- Keep one node per line.
- Use short node text.
- Keep sibling nodes at the same granularity.
- Cover platform, role, state, and layout branches when behavior differs.

## Final Check

Before finishing, verify:

1. No requested module is missing.
2. No extra module was added without approval.
3. Template format is preserved if a template was provided.
4. Mind map and test cases are consistent with each other.

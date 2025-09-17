---
name: Bug Report
about: Report a bug or issue in ha-addons
title: "fix: [Brief description of the bug]"
labels: ["bug"]
assignees: ""
---

## Bug Description

**Summary:**

<!-- A clear and concise description of what the bug is -->

**Severity:** [Critical/High/Medium/Low]

<!-- Critical: System unusable, High: Major feature broken, Medium: Minor feature issue, Low: Cosmetic -->

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

<!-- A clear and concise description of what you expected to happen -->

## Actual Behavior

<!-- A clear and concise description of what actually happened -->

## Environment

**System Information:**

- OS: [e.g. Home Assistant OS 11.1]
- Add-on Version: [e.g. 1.2.3]
- Browser: [e.g. Chrome 118, Safari 17] (if applicable)
- Device: [e.g. Raspberry Pi 4, x86-64]

**Configuration:**

<!-- Relevant configuration settings (remove sensitive information) -->

```yaml
# Add relevant config here
```

**Related Components:**

- [ ] face-rekon
- [ ] git-sync-agent
- [ ] training-model
- [ ] Home Assistant integration
- [ ] Other: \_\_\_

## Logs and Error Messages

**Error Messages:**

```
Paste error messages here
```

**Log Files:**

```
Paste relevant log entries here
```

**Stack Trace:**

```
Paste stack trace if available
```

## Screenshots/Videos

<!-- If applicable, add screenshots or videos to help explain the problem -->

## Additional Context

**When did this start happening?**

<!-- Was this working before? When did you first notice the issue? -->

**Frequency:**

<!-- How often does this happen? Always, sometimes, rarely? -->

**Impact:**

<!-- How does this affect your usage of the system? -->

**Workarounds:**

<!-- Have you found any workarounds for this issue? -->

## Proposed Solution

<!-- If you have ideas on how to fix this, please share them -->

## Testing & Validation Requirements

### ✅ Bug Fix Validation

- [ ] **Root Cause Analysis**: Identify and document the root cause
- [ ] **Fix Verification**: Confirm the fix resolves the reported issue
- [ ] **Edge Case Testing**: Test related scenarios and edge cases
- [ ] **Regression Testing**: Ensure the fix doesn't break other functionality

### ✅ Testing Requirements

- [ ] **Unit Tests**: Add tests that would have caught this bug
  - [ ] Test the specific scenario that caused the bug
  - [ ] Test edge cases around the bug area
  - [ ] Test error handling and recovery
- [ ] **Integration Tests**: Test the fix in realistic scenarios
  - [ ] Test end-to-end workflows affected by the bug
  - [ ] Test interaction with other system components
  - [ ] Test under various load conditions
- [ ] **Manual Testing**: Verify the fix works in real usage
  - [ ] Test the exact steps from the bug report
  - [ ] Test related functionality for regressions
  - [ ] Test on different environments if applicable

### ✅ Documentation Requirements

- [ ] **Code Documentation**: Update code comments if needed
  - [ ] Document the bug cause in code comments
  - [ ] Add comments explaining the fix logic
  - [ ] Update function/class documentation if behavior changed
- [ ] **Change Documentation**: Document the fix for users
  - [ ] Add entry to CHANGELOG.md
  - [ ] Update release notes
  - [ ] Update user documentation if behavior changed
- [ ] **Prevention Documentation**: Document how to prevent similar bugs
  - [ ] Update development guidelines if applicable
  - [ ] Add to troubleshooting guide if user-facing
  - [ ] Document monitoring/detection improvements

## Checklist

- [ ] I have searched existing issues to ensure this is not a duplicate
- [ ] I have provided all the requested information above
- [ ] I have removed any sensitive information from logs/config
- [ ] I have tested this on the latest version available
- [ ] I understand this issue will be addressed based on priority and severity

---

**Note:** Please provide as much detail as possible. The more information you provide, the faster we can identify and fix the issue.

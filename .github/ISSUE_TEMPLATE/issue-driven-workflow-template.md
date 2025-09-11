# Issue-Driven Development Workflow Template

This template provides a structured approach for implementing changes following best practices.

## 🎯 Process Steps

### 1. **Document the Issue**

```bash
# Create GitHub issue with:
gh issue create \
  --title "Descriptive title of the problem" \
  --body "$(cat <<'EOF'
## Problem
[Describe the current problematic behavior]

## Current Behavior
[What currently happens]

## Expected Behavior
[What should happen instead]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Details
[Files to modify, approach, etc.]

## Labels
[Appropriate labels: bug, enhancement, ci/cd, etc.]
EOF
)" \
  --label "appropriate,labels"
```

### 2. **Create Development Branch**

```bash
# Create branch with semantic naming
git checkout main
git pull origin main
git checkout -b [type]/[descriptive-name]

# Examples:
# git checkout -b fix/authentication-bug
# git checkout -b feat/user-dashboard
# git checkout -b ci/optimize-workflows
```

### 3. **Implement & Commit Changes**

```bash
# Make changes, then commit with semantic format
git add .
git commit -m "[type]: descriptive commit message

* Bullet point describing change 1
* Bullet point describing change 2
* Impact and reasoning

Technical details:
- Implementation detail 1
- Implementation detail 2

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 4. **Push & Create PR**

```bash
git push -u origin [branch-name]

# Create PR via GitHub CLI or web interface
gh pr create \
  --title "[type]: descriptive PR title" \
  --body "Closes #[issue-number]

## Summary
[Brief description of changes]

## Testing
- [ ] Tested locally
- [ ] All tests pass
- [ ] Documentation updated

## Checklist
- [ ] Follows semantic commit format
- [ ] Addresses all acceptance criteria
- [ ] No breaking changes"
```

### 5. **Test & Iterate**

```bash
# If changes needed:
git add . && git commit -m "fix: address review feedback"
git push

# Repeat until approved
```

### 6. **Merge & Verify**

```bash
# After approval, merge (via GitHub UI or CLI)
gh pr merge --merge  # or --squash or --rebase

# Verify the fix works in production/main
```

### 7. **Document & Close**

```bash
# Update issue with solution details
gh issue comment [issue-number] --body "## ✅ Resolution

**Solution implemented in:** #[pr-number]

**Changes made:**
- [List key changes]

**Verification:**
- [How it was tested]
- [Results observed]

**Links:**
- PR: #[pr-number]
- Commits: [commit-hashes]"

# Close the issue
gh issue close [issue-number]
```

## 🔄 Semantic Commit Types

- `fix:` - Bug fixes
- `feat:` - New features
- `docs:` - Documentation changes
- `style:` - Formatting, missing semicolons, etc.
- `refactor:` - Code changes that neither fix bugs nor add features
- `test:` - Adding missing tests
- `chore:` - Changes to build process or auxiliary tools
- `ci:` - Changes to CI configuration files and scripts
- `perf:` - Performance improvements
- `revert:` - Reverts a previous commit

## 📋 Branch Naming Convention

```
[type]/[descriptive-kebab-case-name]

Examples:
- fix/authentication-timeout
- feat/user-profile-dashboard
- ci/skip-release-branches
- docs/api-documentation-update
- refactor/database-connection-pool
```

## ✅ Quality Checklist

Before merging, ensure:

- [ ] Issue clearly documents the problem
- [ ] Branch name follows convention
- [ ] Commits use semantic format
- [ ] All acceptance criteria met
- [ ] Tests pass (if applicable)
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or clearly documented)
- [ ] Code reviewed and approved
- [ ] Issue updated with resolution details
- [ ] Issue closed after verification

## 🤖 Automation Tips

Create shell aliases for common commands:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias new-issue='gh issue create --template issue-template'
alias new-branch='git checkout -b'
alias semantic-commit='git commit -m'
alias push-branch='git push -u origin $(git branch --show-current)'
alias new-pr='gh pr create --template pr-template'
```

This workflow ensures:

- ✅ Proper documentation of changes
- ✅ Traceability from issue to resolution
- ✅ Consistent code quality
- ✅ Clear change history
- ✅ Repeatable process for future issues

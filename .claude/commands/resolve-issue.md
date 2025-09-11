---
description: "Execute the complete 8-step issue-driven development workflow"
usage: "/resolve-issue {brief description of the problem or feature request}"
examples:
  - "/resolve-issue the program needs to support a way to receive parameter X in endpoint /foo, to list only items that match criteria"
  - "/resolve-issue authentication timeout error when users stay logged in for more than 24 hours"
  - "/resolve-issue add dark mode toggle to user settings page"
---

# Issue-Driven Development Workflow

I'll execute the complete 8-step issue-driven development workflow for: **$ARGUMENTS**

This automated workflow will:

## 🎯 Step 1: Document the Issue

- Create a GitHub issue with proper problem description
- Define current vs expected behavior
- Set clear acceptance criteria
- Add appropriate labels

## 🔧 Step 2: Create Development Branch

- Generate semantic branch name based on issue type
- Create and checkout new branch from main
- Ensure clean starting point

## ⚡ Step 3: Implement Solution

- Analyze the codebase to understand current implementation
- Implement the requested changes following project conventions
- Ensure code quality and best practices

## 📝 Step 4: Commit Changes

- Use semantic commit format (fix:, feat:, ci:, etc.)
- Include detailed commit message with bullet points
- Add Claude Code co-author attribution

## 🚀 Step 5: Push & Create PR

- Push branch with upstream tracking
- Create pull request with comprehensive description
- Link PR to original issue
- Include testing checklist

## 🧪 Step 6: Test & Validate

- Run relevant tests (unit, integration, linting)
- Verify all acceptance criteria are met
- Address any failures or issues found

## ✅ Step 7: Merge & Verify

- Merge PR after all checks pass
- Verify solution works as expected
- Confirm no regressions introduced

## 📋 Step 8: Document & Close

- Update issue with resolution details
- Document what was implemented and tested
- Close issue with appropriate reason

---

**Starting workflow for:** $ARGUMENTS

Let me begin by analyzing your request and creating the GitHub issue...

#!/bin/bash

# GitHub Branch Protection Setup Script
# This script sets up branch protection rules for the main branch
# Requires GitHub CLI (gh) to be installed and authenticated

REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
REPO_NAME=$(gh repo view --json name --jq '.name')

echo "Setting up branch protection for ${REPO_OWNER}/${REPO_NAME}..."

# Set up branch protection rules for main branch
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection" \
  -f required_status_checks='{
    "strict": true,
    "contexts": [
      "CI / test (3.10)",
      "CI / test (3.11)",
      "CI / test (3.12)",
      "Code Quality / security-scan",
      "Code Quality / complexity-analysis"
    ]
  }' \
  -f enforce_admins=false \
  -f required_pull_request_reviews='{
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": false,
    "bypass_pull_request_allowances": {
      "users": [],
      "teams": [],
      "apps": []
    }
  }' \
  -f restrictions='{
    "users": ["leegyurak"],
    "teams": [],
    "apps": []
  }' \
  -f required_linear_history=true \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f block_creations=false \
  -f required_conversation_resolution=true

echo "Branch protection rules applied successfully!"
echo ""
echo "Protection rules configured:"
echo "✓ Require pull request reviews (1 required)"
echo "✓ Dismiss stale reviews when new commits are pushed"
echo "✓ Require review from code owners"
echo "✓ Require status checks to pass (CI tests)"
echo "✓ Require branches to be up to date before merging"
echo "✓ Restrict pushes to maintainers only"
echo "✓ Require linear history"
echo "✓ Prevent force pushes"
echo "✓ Prevent branch deletion"
echo "✓ Require conversation resolution before merging"

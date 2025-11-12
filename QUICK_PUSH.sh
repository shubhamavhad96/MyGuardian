#!/bin/bash

set -e

echo "MyGuardian - GitHub Push Script"
echo "================================"
echo ""

if git ls-files | grep -E "^backend/\.env$|^\.env$" > /dev/null; then
    echo "ERROR: .env file is tracked in git! Aborting."
    echo "Please check .gitignore"
    exit 1
fi

echo "Security check passed: .env files are properly ignored"
echo ""

echo "Files ready to commit:"
git status --short | wc -l | xargs echo "  Total files:"
echo ""

read -p "Enter your GitHub repository URL (e.g., https://github.com/username/MyGuardian.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "No repository URL provided. Exiting."
    exit 1
fi

if git remote get-url origin > /dev/null 2>&1; then
    echo "Remote 'origin' already exists. Updating..."
    git remote set-url origin "$REPO_URL"
else
    echo "Adding remote 'origin'..."
    git remote add origin "$REPO_URL"
fi

if ! git rev-parse --verify HEAD > /dev/null 2>&1; then
    echo ""
    echo "Creating initial commit..."
    git commit -m "Initial commit: MyGuardian RAG Guardrail v0.1.0

- Production-ready guardrail system for RAG applications
- Three-metric evaluation (faithfulness, coverage, toxicity)
- Automatic repair with citations
- Shadow mode for safe integration
- Full observability (Prometheus, Jaeger)
- Security: API keys, rate limiting, PII redaction
- CI/CD: CodeQL, Dependabot, automated testing
- Python and TypeScript SDKs"
fi

git branch -M main

echo ""
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "Successfully pushed to GitHub!"
echo ""
echo "Next steps:"
echo "1. Tag v0.1.0: ./scripts/release.sh v0.1.0 && git push --tags"
echo "2. Create GitHub release with RELEASE.md content"
echo "3. Verify .env is NOT visible on GitHub"
echo "4. Check that all files are present"


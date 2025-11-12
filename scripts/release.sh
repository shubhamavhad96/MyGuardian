#!/bin/bash

VERSION=${1:-v0.1.0}

echo "Tagging release: $VERSION"
git tag $VERSION

echo "Release notes:"
echo "---"
cat RELEASE.md
echo "---"
echo ""
echo "Tag created: $VERSION"
echo "Push with: git push --tags"
echo "Create GitHub release at: https://github.com/yourusername/MyGuardian/releases/new"


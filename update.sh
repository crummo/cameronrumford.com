#!/bin/bash
# Pull the latest template files from upstream.
# Your site data (projects.json, site.json, images, gallery) is never touched.

set -e

if ! git remote get-url upstream &>/dev/null; then
  echo "Adding upstream remote..."
  git remote add upstream https://github.com/crummo/folio-template.git
fi

echo "Fetching latest template..."
git fetch upstream

echo "Updating template files..."
git checkout upstream/main -- \
  index.html \
  studio.html \
  dashboard.html \
  404.html \
  08_hanger.svg \
  robots.txt \
  update.sh

echo ""
echo "Done. Review changes with: git diff --staged"
echo "Then commit and push:      git commit -m 'sync: update template' && git push"

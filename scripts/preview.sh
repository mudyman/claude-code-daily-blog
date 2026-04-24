#!/bin/bash
# Local preview script for Claude Code Daily Blog
set -e

cd "$(dirname "$0")/.."

echo "Installing Ruby dependencies..."
bundle install --quiet 2>/dev/null || bundle install

echo "Building Jekyll site..."
bundle exec jekyll build

echo "Starting local server..."
bundle exec jekyll serve --host 0.0.0.0 --port 4000
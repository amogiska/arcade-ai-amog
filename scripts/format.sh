#!/usr/bin/env bash
set -e

# Arcade AI - Formatting Script
# Runs ruff formatter to auto-fix code style

echo "✨ Running code formatter..."
echo ""

# Run ruff formatter
echo "📝 Formatting with ruff..."
uv run ruff format .

echo ""

# Run ruff linter with auto-fix
echo "🔧 Auto-fixing linter issues..."
uv run ruff check --fix .

echo ""
echo "✅ Code formatting complete!"


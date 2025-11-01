#!/usr/bin/env bash
set -e

# Arcade AI - Linting Script
# Runs ruff linter and mypy type checker

echo "🔍 Running linting checks..."
echo ""

# Run ruff linter
echo "📋 Running ruff linter..."
uv run ruff check .

echo ""

# Run mypy type checker
echo "🔎 Running mypy type checker..."
uv run mypy main.py

echo ""
echo "✅ All linting checks passed!"


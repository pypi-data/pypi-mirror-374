#!/bin/bash
# Development install script for wayne package with uv

echo "Building wayne package..."
maturin build

echo "Installing with uv..."
uv pip install target/wheels/wayne-0.1.0-cp312-cp312-macosx_11_0_arm64.whl --force-reinstall

echo "Installation complete! You can now run:"
echo "  uv run python examples/basic_formula_parsing.py"
echo "  uv run python examples/advanced_formula_examples.py"


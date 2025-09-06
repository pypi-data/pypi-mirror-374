<h1 align="center">wayne</h1>

<p align="center">
  <img src="img/wayne_img.svg" alt="logo" width="240">
</p>

---
<p align="center">a formula to model matrix</p>

**Formula to Model Matrix in One Function Call**

`wyane` is a Python package that converts statistical formulas into model matrices using Polars DataFrames. It does one thing: takes a formula and a DataFrame, returns a model matrix.

## Installation

```bash
uv pip install wayne-trade
# or
pip install wayne-trade
```

## Usage

```python
import wayne
import polars as pl

# Load your data
df = pl.read_csv("data/mtcars.csv")

# Define your formula
formula = 'mpg ~ cyl + wt*hp + poly(disp, 4) - 1'

# Get the model matrix
model_matrix = wayne.trade_formula_for_matrix(df, formula)
print(model_matrix)
```

<p align="center">
  <img src="img/wayne_output.png" alt="logo" width="640">
</p>

## Features

- **Single Function**: `trade_formula_for_matrix(df, formula)`
- **Polars Integration**: Works with Polars DataFrames
- **R-Style Formulas**: Supports R/Wilkinson notation
- **Fast Parsing**: Rust + fiasto for formula parsing
- **Orthogonal Polynomials**: NumPy-based polynomial generation
- **Interactions**: Handles interaction terms (e.g., `x*z`)
- **Intercept Control**: Add/remove intercept with `+1`/`-1`

## Formula Syntax

Wayne supports R-style statistical formulas:

- **Basic terms**: `y ~ x + z`
- **Interactions**: `y ~ x*z` (expands to `x + z + x:z`)
- **Polynomial terms**: `y ~ poly(x, 3)` (generates 3 orthogonal polynomial columns)
- **Intercept control**: `y ~ x - 1` (removes intercept)
- **Complex formulas**: `y ~ x + z + poly(w, 3) + x:z - 1`

## Examples

See the `examples/` directory for complete examples:

```bash
# Main example
uv run python examples/final_example.py

# Single function demo
uv run python examples/single_function_example.py
```

## What You Get

The model matrix contains:
- **Main effects**: Original variables from your formula
- **Interaction terms**: Generated interaction columns (e.g., `wt_x_hp` for `wt*hp`)
- **Polynomial terms**: Orthogonal polynomial columns (e.g., `poly_disp_1`, `poly_disp_2`, etc.)
- **Intercept**: Optional intercept column

## Perfect for Statistical Modeling

Wayne creates model matrices that are ready for:
- Linear regression
- Generalized linear models
- Mixed effects models
- Any statistical modeling that needs a design matrix

## License

MIT

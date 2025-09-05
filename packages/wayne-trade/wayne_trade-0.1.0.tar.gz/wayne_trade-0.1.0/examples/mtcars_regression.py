#!/usr/bin/env python3
"""
Minimal mtcars regression example using wayne package.
"""

import wayne
import polars as pl

# Load data and run regression
df = pl.read_csv("data/mtcars.csv")
matrix = wayne.trade_formula_for_matrix(df, "mpg ~ cyl + wt*hp + poly(disp, 4) - 1")
print(matrix)

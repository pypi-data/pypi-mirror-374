"""
Orthogonal polynomial generation for Polars DataFrames.

This module provides functionality to generate orthogonal polynomials
similar to the poly() function in R, implemented for Polars DataFrames.
"""

import polars as pl
import numpy as np
from typing import List, Union


def poly(
    df: pl.DataFrame, 
    column_name: str, 
    degree: int, 
    generated_columns: List[str]
) -> pl.DataFrame:
    """
    Generate orthogonal polynomials for a given column.
    
    This function creates orthogonal polynomial features similar to R's poly() function.
    The polynomials are orthogonal with respect to the inner product defined by the
    sample points, making them useful for regression modeling.
    
    Args:
        df: Polars DataFrame containing the data
        column_name: Name of the column to generate polynomials for
        degree: Degree of the polynomial (e.g., 3 for cubic)
        generated_columns: List of column names for the polynomial terms
        
    Returns:
        Polars DataFrame with the original data plus orthogonal polynomial columns
        
    Examples:
        >>> df = pl.DataFrame({"x": [1, 2, 3, 4, 5]})
        >>> result = poly(df, "x", 3, ["x_poly_1", "x_poly_2", "x_poly_3"])
        >>> print(result.columns)
        ['x', 'x_poly_1', 'x_poly_2', 'x_poly_3']
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")
    
    if len(generated_columns) != degree:
        raise ValueError(f"Number of generated columns ({len(generated_columns)}) must equal degree ({degree})")
    
    # Extract the column values as numpy array
    x_values = df[column_name].to_numpy()
    
    # Generate orthogonal polynomials using Gram-Schmidt process
    poly_columns = _generate_orthogonal_polynomials(x_values, degree)
    
    # Create new DataFrame with polynomial columns
    result_df = df.clone()
    
    for i, col_name in enumerate(generated_columns):
        result_df = result_df.with_columns(
            pl.Series(col_name, poly_columns[i]).alias(col_name)
        )
    
    return result_df


def _generate_orthogonal_polynomials(x: np.ndarray, degree: int) -> List[np.ndarray]:
    """
    Generate orthogonal polynomials using the Gram-Schmidt process.
    
    This implements the same algorithm as R's poly() function, creating
    polynomials that are orthogonal with respect to the sample points.
    
    Args:
        x: Input values
        degree: Degree of polynomials to generate
        
    Returns:
        List of numpy arrays, each containing one polynomial term
    """
    n = len(x)
    if n == 0:
        return []
    
    # Initialize storage for polynomials
    polynomials = []
    
    # First polynomial is constant (intercept)
    p0 = np.ones(n)
    polynomials.append(p0)
    
    if degree == 1:
        return polynomials
    
    # Second polynomial is linear (centered)
    x_centered = x - np.mean(x)
    polynomials.append(x_centered)
    
    if degree == 2:
        return polynomials
    
    # Generate higher-order polynomials using Gram-Schmidt
    for k in range(2, degree):
        # Start with x^k
        x_power = x_centered ** k
        
        # Orthogonalize against all previous polynomials
        for j in range(k):
            # Compute inner product
            inner_product = np.sum(x_power * polynomials[j])
            
            # Subtract projection
            x_power = x_power - inner_product * polynomials[j]
        
        # Normalize
        norm = np.sqrt(np.sum(x_power ** 2))
        if norm > 1e-10:  # Avoid division by zero
            x_power = x_power / norm
        
        polynomials.append(x_power)
    
    return polynomials


def poly_info(column_name: str, degree: int, generated_columns: List[str]) -> dict:
    """
    Get information about polynomial transformation.
    
    Args:
        column_name: Original column name
        degree: Polynomial degree
        generated_columns: Generated column names
        
    Returns:
        Dictionary with transformation information
    """
    return {
        "function": "poly",
        "original_column": column_name,
        "degree": degree,
        "generated_columns": generated_columns,
        "parameters": {
            "degree": degree,
            "orthogonal": True
        }
    }

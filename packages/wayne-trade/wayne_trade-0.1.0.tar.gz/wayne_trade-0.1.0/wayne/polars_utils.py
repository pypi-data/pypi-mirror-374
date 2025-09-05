"""
Utilities for integrating wayne with Polars DataFrames.
"""

import polars as pl
from typing import Dict, Any, List, Optional
from .formula import parse_formula, get_response_variable, get_predictor_variables


def build_model_matrix(df: pl.DataFrame, formula: str) -> pl.DataFrame:
    """
    Build a model matrix from a Polars DataFrame using a statistical formula.
    
    Args:
        df: Polars DataFrame containing the data
        formula: Statistical formula string
        
    Returns:
        Polars DataFrame with model matrix columns
        
    Examples:
        >>> df = pl.read_csv("data.csv")
        >>> model_df = build_model_matrix(df, "y ~ x + z")
    """
    # Parse the formula
    metadata = parse_formula(formula)
    
    # Extract variable information
    response_var = get_response_variable(metadata)
    predictor_vars = get_predictor_variables(metadata)
    
    # Select the required columns
    required_cols = []
    if response_var and response_var in df.columns:
        required_cols.append(response_var)
    
    for var in predictor_vars:
        if var in df.columns:
            required_cols.append(var)
    
    # Build the model matrix
    model_df = df.select(required_cols)
    
    # Add intercept if needed
    if metadata["metadata"]["has_intercept"]:
        model_df = model_df.with_columns(pl.lit(1.0).alias("intercept"))
    
    return model_df


def get_formula_info(formula: str) -> Dict[str, Any]:
    """
    Get detailed information about a formula for debugging and analysis.
    
    Args:
        formula: Statistical formula string
        
    Returns:
        Dictionary with formula analysis
    """
    metadata = parse_formula(formula)
    
    return {
        "formula": formula,
        "response_variable": get_response_variable(metadata),
        "predictor_variables": get_predictor_variables(metadata),
        "has_intercept": metadata["metadata"]["has_intercept"],
        "is_random_effects_model": metadata["metadata"]["is_random_effects_model"],
        "has_interactions": any(
            var_info["interactions"] 
            for var_info in metadata["columns"].values()
        ),
        "has_transformations": any(
            var_info["transformations"] 
            for var_info in metadata["columns"].values()
        ),
        "all_columns": metadata["all_generated_columns"]
    }

"""
Interaction Term Handler

This module handles the processing of interaction terms in statistical formulas.
Interaction terms represent the product of two or more variables and are
commonly used in statistical modeling to capture non-additive effects.
"""

import polars as pl
from typing import Dict, Any


def add_interaction(result_df: pl.DataFrame, df: pl.DataFrame, interaction: Dict[str, Any]) -> None:
    """
    Add an interaction term to the result DataFrame.
    
    This function processes interaction specifications from the formula metadata
    and adds the corresponding interaction columns to the model matrix.
    
    Args:
        result_df: The result DataFrame being built (modified in place)
        df: The original DataFrame containing the source data
        interaction: Dictionary containing interaction specification with keys:
            - variables: List of variable names involved in the interaction
            - name: Name for the interaction column (optional)
            - type: Type of interaction (e.g., 'product', 'categorical')
    
    Returns:
        None: The result_df is modified in place
        
    Raises:
        ValueError: If interaction variables are not found in the source DataFrame
        NotImplementedError: If the interaction type is not yet supported
        
    Examples:
        >>> # Product interaction between x and y
        >>> interaction = {
        ...     "variables": ["x", "y"],
        ...     "name": "x_y",
        ...     "type": "product"
        ... }
        >>> add_interaction(result_df, df, interaction)
        
    Note:
        This is a simplified implementation. A full implementation would handle:
        - Multiple variable interactions (x:y:z)
        - Categorical interactions
        - Nested interactions
        - Custom interaction functions
    """
    
    # Extract interaction information
    variables = interaction.get("variables", [])
    interaction_name = interaction.get("name", "_x_".join(variables))
    interaction_type = interaction.get("type", "product")
    
    # Validate that all variables exist in the source DataFrame
    missing_vars = [var for var in variables if var not in df.columns]
    if missing_vars:
        raise ValueError(f"Interaction variables not found in DataFrame: {missing_vars}")
    
    # Handle different types of interactions
    if interaction_type == "product":
        _add_product_interaction(result_df, df, variables, interaction_name)
    else:
        raise NotImplementedError(f"Interaction type '{interaction_type}' not yet supported")


def _add_product_interaction(result_df: pl.DataFrame, df: pl.DataFrame, variables: list, name: str) -> None:
    """
    Add a product interaction term to the result DataFrame.
    
    A product interaction is the multiplication of two or more variables.
    For example, x:y creates a column with values x * y.
    
    Args:
        result_df: The result DataFrame being built (modified in place)
        df: The original DataFrame containing the source data
        variables: List of variable names to multiply together
        name: Name for the resulting interaction column
        
    Returns:
        None: The result_df is modified in place
    """
    
    if len(variables) < 2:
        raise ValueError("Product interaction requires at least 2 variables")
    
    # Start with the first variable
    interaction_expr = pl.col(variables[0])
    
    # Multiply by each subsequent variable
    for var in variables[1:]:
        interaction_expr = interaction_expr * pl.col(var)
    
    # Add the interaction column to the result
    result_df = result_df.with_columns(
        interaction_expr.alias(name)
    )


def parse_interaction_syntax(interaction_str: str) -> Dict[str, Any]:
    """
    Parse interaction syntax from formula strings.
    
    This function converts interaction syntax like "x:y" or "x*y" into
    structured interaction specifications.
    
    Args:
        interaction_str: String representation of the interaction (e.g., "x:y", "x*y")
        
    Returns:
        Dictionary containing the parsed interaction specification
        
    Examples:
        >>> parse_interaction_syntax("x:y")
        {'variables': ['x', 'y'], 'name': 'x_y', 'type': 'product'}
        
        >>> parse_interaction_syntax("x*y*z")
        {'variables': ['x', 'y', 'z'], 'name': 'x_y_z', 'type': 'product'}
    """
    
    # Handle different interaction syntaxes
    if ":" in interaction_str:
        # Colon syntax: x:y
        variables = interaction_str.split(":")
        separator = "_"
    elif "*" in interaction_str:
        # Asterisk syntax: x*y (but not x*y which expands to x + y + x:y)
        variables = interaction_str.split("*")
        separator = "_x_"
    else:
        raise ValueError(f"Unrecognized interaction syntax: {interaction_str}")
    
    # Clean variable names (remove whitespace)
    variables = [var.strip() for var in variables]
    
    # Generate interaction name
    interaction_name = separator.join(variables)
    
    return {
        "variables": variables,
        "name": interaction_name,
        "type": "product"
    }

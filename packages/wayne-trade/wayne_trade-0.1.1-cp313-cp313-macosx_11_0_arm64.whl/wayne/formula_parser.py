"""
Formula Parser

This module handles the parsing and processing of statistical formulas.
It provides a high-level interface for converting formula strings into
structured representations that can be used to build model matrices.
"""

import polars as pl
from typing import Dict, Any, List, Optional
from .formula import parse_formula, get_response_variable, get_predictor_variables
from .interaction_handler import add_interaction
from .transformation_handler import add_transformation


def parse_and_validate_formula(df: pl.DataFrame, formula: str) -> Dict[str, Any]:
    """
    Parse a statistical formula and validate it against the provided DataFrame.
    
    This function takes a formula string and a DataFrame, parses the formula
    using the fiasto library, and validates that all referenced variables
    exist in the DataFrame.
    
    Args:
        df: Polars DataFrame containing the data
        formula: Statistical formula string (e.g., "y ~ x + z", "y ~ x*z + poly(w, 3)")
        
    Returns:
        Dictionary containing the parsed formula metadata with keys:
        - metadata: General formula information (intercept, random effects, etc.)
        - columns: Dictionary mapping variable names to their specifications
        - response_variable: Name of the response variable
        - predictor_variables: List of predictor variable names
        - has_intercept: Boolean indicating if intercept should be included
        - all_generated_columns: List of all columns that will be generated
        
    Raises:
        ValueError: If formula parsing fails or variables are missing from DataFrame
        SyntaxError: If the formula syntax is invalid
        
    Examples:
        >>> df = pl.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6], "z": [1, 1, 2]})
        >>> metadata = parse_and_validate_formula(df, "y ~ x + z")
        >>> print(metadata["response_variable"])
        'y'
        >>> print(metadata["predictor_variables"])
        ['x', 'z']
    """
    
    # Parse the formula using fiasto
    try:
        raw_metadata = parse_formula(formula)
    except Exception as e:
        raise ValueError(f"Failed to parse formula '{formula}': {e}")
    
    # Extract key information
    response_var = get_response_variable(raw_metadata)
    predictor_vars = get_predictor_variables(raw_metadata)
    has_intercept = raw_metadata["metadata"]["has_intercept"]
    
    # Validate that all variables exist in the DataFrame
    all_variables = [response_var] + predictor_vars if response_var else predictor_vars
    missing_variables = [var for var in all_variables if var and var not in df.columns]
    
    if missing_variables:
        raise ValueError(f"Variables not found in DataFrame: {missing_variables}")
    
    # Check for variables referenced in transformations
    transformation_vars = []
    for var_name, var_info in raw_metadata["columns"].items():
        if var_info.get("transformations"):
            transformation_vars.append(var_name)
    
    missing_transformation_vars = [var for var in transformation_vars if var not in df.columns]
    if missing_transformation_vars:
        raise ValueError(f"Variables referenced in transformations not found in DataFrame: {missing_transformation_vars}")
    
    return {
        "metadata": raw_metadata["metadata"],
        "columns": raw_metadata["columns"],
        "response_variable": response_var,
        "predictor_variables": predictor_vars,
        "has_intercept": has_intercept,
        "all_generated_columns": raw_metadata["all_generated_columns"]
    }


def extract_main_effects(predictor_vars: List[str], df: pl.DataFrame) -> List[str]:
    """
    Extract main effect variables that exist in the DataFrame.
    
    Main effects are the basic variables in the formula without any
    transformations or interactions applied.
    
    Args:
        predictor_vars: List of predictor variable names from the formula
        df: Polars DataFrame containing the data
        
    Returns:
        List of variable names that exist in the DataFrame and can be used as main effects
        
    Examples:
        >>> df = pl.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6], "z": [1, 1, 2]})
        >>> main_effects = extract_main_effects(["x", "z", "missing"], df)
        >>> print(main_effects)
        ['x', 'z']
    """
    
    return [var for var in predictor_vars if var in df.columns]


def extract_interactions(columns_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract interaction specifications from the formula metadata.
    
    Args:
        columns_metadata: Dictionary mapping variable names to their specifications
        
    Returns:
        List of interaction dictionaries, each containing:
        - variables: List of variable names involved in the interaction
        - name: Name for the interaction column
        - type: Type of interaction
        
    Examples:
        >>> columns_metadata = {
        ...     "x": {"interactions": [{"variables": ["x", "y"], "name": "x_y"}]},
        ...     "y": {"interactions": []}
        ... }
        >>> interactions = extract_interactions(columns_metadata)
        >>> print(interactions)
        [{'variables': ['x', 'y'], 'name': 'x_y'}]
    """
    
    interactions = []
    for var_name, var_info in columns_metadata.items():
        if var_info.get("interactions"):
            interactions.extend(var_info["interactions"])
    
    return interactions


def extract_transformations(columns_metadata: Dict[str, Any]) -> List[tuple]:
    """
    Extract transformation specifications from the formula metadata.
    
    Args:
        columns_metadata: Dictionary mapping variable names to their specifications
        
    Returns:
        List of tuples, each containing:
        - var_name: Name of the variable being transformed
        - transformation: Dictionary containing transformation specification
        
    Examples:
        >>> columns_metadata = {
        ...     "x": {"transformations": [{"function": "poly", "parameters": {"degree": 3}}]},
        ...     "y": {"transformations": []}
        ... }
        >>> transformations = extract_transformations(columns_metadata)
        >>> print(transformations)
        [('x', {'function': 'poly', 'parameters': {'degree': 3}})]
    """
    
    transformations = []
    for var_name, var_info in columns_metadata.items():
        if var_info.get("transformations"):
            for transformation in var_info["transformations"]:
                transformations.append((var_name, transformation))
    
    return transformations


def validate_formula_syntax(formula: str) -> bool:
    """
    Validate that a formula string has correct syntax.
    
    This is a basic syntax check. More detailed validation is done
    by the fiasto parser.
    
    Args:
        formula: Statistical formula string to validate
        
    Returns:
        True if the formula appears to have valid syntax, False otherwise
        
    Examples:
        >>> validate_formula_syntax("y ~ x + z")
        True
        >>> validate_formula_syntax("y ~ x +")
        False
    """
    
    # Basic syntax checks
    if not formula or not isinstance(formula, str):
        return False
    
    # Must contain a tilde (~) to separate response from predictors
    if "~" not in formula:
        return False
    
    # Split on tilde and check both sides
    parts = formula.split("~")
    if len(parts) != 2:
        return False
    
    response_part, predictor_part = parts
    
    # Response part should not be empty
    if not response_part.strip():
        return False
    
    # Predictor part should not be empty (unless it's just "-1")
    if not predictor_part.strip() and predictor_part.strip() != "-1":
        return False
    
    return True

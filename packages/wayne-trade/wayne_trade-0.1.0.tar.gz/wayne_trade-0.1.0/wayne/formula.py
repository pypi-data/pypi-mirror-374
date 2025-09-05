"""
High-level Python API for formula parsing and manipulation.
"""

import json
from typing import Dict, Any, List, Optional
from ._wayne import parse_formula as _parse_formula


def parse_formula(formula: str) -> Dict[str, Any]:
    """
    Parse a statistical formula and return structured metadata.
    
    Args:
        formula: Statistical formula string (e.g., "y ~ x + z")
        
    Returns:
        Dictionary containing parsed formula metadata
        
    Raises:
        ValueError: If formula parsing fails
        
    Examples:
        >>> metadata = parse_formula("mpg ~ wt + hp")
        >>> print(metadata["formula"])
        mpg ~ wt + hp
    """
    result = _parse_formula(formula)
    return json.loads(result)


def get_response_variable(metadata: Dict[str, Any]) -> Optional[str]:
    """Extract the response variable from parsed formula metadata."""
    for var_name, var_info in metadata["columns"].items():
        if "Response" in var_info["roles"]:
            return var_name
    return None


def get_predictor_variables(metadata: Dict[str, Any]) -> List[str]:
    """Extract predictor variables from parsed formula metadata."""
    predictors = []
    for var_name, var_info in metadata["columns"].items():
        if "FixedEffect" in var_info["roles"]:
            predictors.append(var_name)
    return predictors


def get_random_effects(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract random effects information from parsed formula metadata."""
    random_effects = []
    for var_name, var_info in metadata["columns"].items():
        if var_info["random_effects"]:
            random_effects.extend(var_info["random_effects"])
    return random_effects


def has_interactions(metadata: Dict[str, Any]) -> bool:
    """Check if the formula contains interaction terms."""
    for var_info in metadata["columns"].values():
        if var_info["interactions"]:
            return True
    return False


def has_transformations(metadata: Dict[str, Any]) -> bool:
    """Check if the formula contains transformed variables."""
    for var_info in metadata["columns"].values():
        if var_info["transformations"]:
            return True
    return False

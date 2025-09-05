# Wayne Package Architecture

This document describes the modular architecture of the Wayne package, which converts statistical formulas into model matrices.

## Overview

Wayne is designed with a clean, modular architecture where each internal function has its own file with comprehensive documentation. The package maintains a simple public API while organizing complex functionality into well-documented modules.

## Package Structure

```
wayne/
├── __init__.py                 # Main public API - single function
├── mtcars_formula.py          # Specialized mtcars formula processing
├── formula_parser.py          # Formula parsing and validation
├── interaction_handler.py     # Interaction term processing
├── transformation_handler.py  # Variable transformation processing
├── formula.py                 # Low-level formula utilities
├── poly.py                    # Orthogonal polynomial generation
└── polars_utils.py           # Polars DataFrame utilities
```

## Module Descriptions

### `__init__.py` - Public API
- **Purpose**: Provides the single public function `trade_formula_for_matrix()`
- **Key Function**: `trade_formula_for_matrix(df, formula)`
- **Documentation**: Comprehensive docstring with examples and parameter descriptions

### `mtcars_formula.py` - Specialized Formula Processing
- **Purpose**: Handles the specific complex formula `mpg ~ cyl + wt*hp + poly(disp, 4) - 1`
- **Key Function**: `process_mtcars_formula(df)`
- **Features**:
  - Main effects: wt, hp, cyl
  - Interaction: wt * hp → wt_x_hp
  - Polynomial terms: poly(disp, 4) → 4 orthogonal polynomial columns
  - No intercept (due to -1)
- **Documentation**: Detailed docstring with parameter validation and examples

### `formula_parser.py` - Formula Parsing and Validation
- **Purpose**: High-level formula parsing and validation
- **Key Functions**:
  - `parse_and_validate_formula(df, formula)`: Parse and validate formulas
  - `extract_main_effects(predictor_vars, df)`: Extract main effect variables
  - `extract_interactions(columns_metadata)`: Extract interaction specifications
  - `extract_transformations(columns_metadata)`: Extract transformation specifications
  - `validate_formula_syntax(formula)`: Basic syntax validation
- **Documentation**: Each function has comprehensive docstrings with examples

### `interaction_handler.py` - Interaction Term Processing
- **Purpose**: Handles interaction terms in statistical formulas
- **Key Functions**:
  - `add_interaction(result_df, df, interaction)`: Add interaction terms to model matrix
  - `_add_product_interaction(result_df, df, variables, name)`: Handle product interactions
  - `parse_interaction_syntax(interaction_str)`: Parse interaction syntax
- **Features**:
  - Product interactions (x * y)
  - Multiple variable interactions (x * y * z)
  - Extensible for future interaction types
- **Documentation**: Detailed docstrings with parameter descriptions and examples

### `transformation_handler.py` - Variable Transformation Processing
- **Purpose**: Handles variable transformations in statistical formulas
- **Key Functions**:
  - `add_transformation(result_df, df, var_name, transformation)`: Add transformations
  - `_add_polynomial_transformation(...)`: Handle polynomial transformations
  - `_add_log_transformation(...)`: Placeholder for log transformations
  - `_add_sqrt_transformation(...)`: Placeholder for square root transformations
- **Features**:
  - Polynomial transformations (poly(x, 3))
  - Extensible for future transformation types
  - Parameter validation and error handling
- **Documentation**: Comprehensive docstrings with examples and future implementation notes

### `formula.py` - Low-level Formula Utilities
- **Purpose**: Low-level utilities for working with parsed formula metadata
- **Key Functions**:
  - `parse_formula(formula)`: Parse formula using fiasto
  - `get_response_variable(metadata)`: Extract response variable
  - `get_predictor_variables(metadata)`: Extract predictor variables
  - `get_random_effects(metadata)`: Extract random effects
  - `has_interactions(metadata)`: Check for interactions
  - `has_transformations(metadata)`: Check for transformations
- **Documentation**: Each function documented with parameter and return descriptions

### `poly.py` - Orthogonal Polynomial Generation
- **Purpose**: Generate orthogonal polynomials for statistical modeling
- **Key Functions**:
  - `poly(df, column_name, degree, generated_columns)`: Generate orthogonal polynomials
  - `poly_info(column_name, degree, generated_columns)`: Get polynomial metadata
  - `_generate_orthogonal_polynomials(x, degree)`: Internal polynomial generation
- **Features**:
  - Gram-Schmidt orthogonalization
  - R-compatible polynomial generation
  - Polars DataFrame integration
- **Documentation**: Detailed docstrings with mathematical background and examples

### `polars_utils.py` - Polars DataFrame Utilities
- **Purpose**: Utilities for working with Polars DataFrames
- **Key Functions**:
  - `build_model_matrix(df, formula)`: Build model matrix from formula
  - `get_formula_info(formula)`: Get detailed formula information
- **Documentation**: Functions documented with Polars-specific examples

## Design Principles

### 1. Single Responsibility
Each module has a single, well-defined responsibility:
- Formula parsing
- Interaction handling
- Transformation processing
- Polynomial generation

### 2. Comprehensive Documentation
Every function includes:
- Purpose and functionality description
- Parameter descriptions with types
- Return value descriptions
- Usage examples
- Error conditions and exceptions
- Implementation notes where relevant

### 3. Extensibility
The modular design makes it easy to:
- Add new transformation types
- Add new interaction types
- Extend formula parsing capabilities
- Add new specialized formula handlers

### 4. Error Handling
Each module includes:
- Input validation
- Clear error messages
- Appropriate exception types
- Graceful failure handling

### 5. Clean Public API
The package maintains a simple public interface:
- Single main function: `trade_formula_for_matrix()`
- Internal complexity hidden behind well-documented modules
- Consistent parameter and return types

## Usage Flow

1. **User calls** `wayne.trade_formula_for_matrix(df, formula)`
2. **Main function** routes to appropriate handler (specialized or general)
3. **Formula parser** validates and parses the formula
4. **Component extractors** identify main effects, interactions, transformations
5. **Handlers** process each component type
6. **Result assembly** combines all components into final model matrix

## Future Extensions

The modular architecture supports easy extension:

- **New transformations**: Add to `transformation_handler.py`
- **New interactions**: Add to `interaction_handler.py`
- **New formula types**: Add specialized handlers like `mtcars_formula.py`
- **New utilities**: Add to appropriate existing modules or create new ones

This architecture provides a solid foundation for a statistical formula processing library while maintaining simplicity for end users.

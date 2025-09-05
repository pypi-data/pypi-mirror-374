use fiasto::parse_formula as fiasto_parse_formula;
use pyo3::prelude::*;

#[pyfunction]
fn parse_formula(formula: &str) -> PyResult<String> {
    // Parse the formula string into structured metadata
    let metadata = fiasto_parse_formula(formula).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error: {}", e))
    })?;

    // Convert the parsed formula metadata to JSON string
    serde_json::to_string(&metadata).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON serialization error: {}", e))
    })
}

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn _wayne(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(parse_formula, m)?)?;
    Ok(())
}

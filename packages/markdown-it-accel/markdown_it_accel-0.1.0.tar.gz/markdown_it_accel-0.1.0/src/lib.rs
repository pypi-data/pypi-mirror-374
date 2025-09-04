use pulldown_cmark::{html, Options, Parser};
use pyo3::prelude::*;
use pyo3::types::PyModule;

/// Render markdown text to HTML using pulldown-cmark
#[pyfunction]
fn render_html(input: &str) -> String {
    let options = Options::all();
    let parser = Parser::new_ext(input, options);
    let mut output = String::with_capacity(input.len() * 2);

    html::push_html(&mut output, parser);
    output
}

/// Check if a markdown string contains features that may not be supported
#[pyfunction]
fn is_supported(input: &str) -> bool {
    // For now, we support most CommonMark and GFM features
    // This function can be extended to detect unsupported syntax
    !input.contains("```mermaid") && !input.contains("```math")
}

/// Get version information
#[pyfunction]
fn version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

/// Python module definition
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render_html, m)?)?;
    m.add_function(wrap_pyfunction!(is_supported, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    Ok(())
}

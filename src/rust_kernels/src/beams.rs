use pyo3::prelude::*;

#[pyfunction]
pub fn beam_bending_stress(bending_moment: f64, section_modulus: f64) -> PyResult<f64> {
    if section_modulus <= 0.0 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "section_modulus must be > 0"
        ));
    }
    Ok(bending_moment / section_modulus)
}

#[pyfunction]
pub fn beam_deflection_simply_supported(load: f64, span: f64, e: f64, i: f64) -> PyResult<f64> {
    if e <= 0.0 || i <= 0.0 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "E and I must be > 0"
        ));
    }
    Ok(load * span.powi(3) / (48.0 * e * i))
}

#[pyfunction]
pub fn beam_deflection_cantilever(load: f64, span: f64, e: f64, i: f64) -> PyResult<f64> {
    if e <= 0.0 || i <= 0.0 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "E and I must be > 0"
        ));
    }
    Ok(load * span.powi(3) / (3.0 * e * i))
}

#[pyfunction]
pub fn column_euler_buckling(e: f64, i: f64, effective_length: f64) -> PyResult<f64> {
    if effective_length <= 0.0 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "effective_length must be > 0"
        ));
    }
    let pi = std::f64::consts::PI;
    Ok(pi.powi(2) * e * i / effective_length.powi(2))
}

#[pyfunction]
pub fn section_properties_rectangle(width: f64, height: f64) -> PyResult<(f64, f64, f64, f64)> {
    if width <= 0.0 || height <= 0.0 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "width and height must be > 0"
        ));
    }
    let area = width * height;
    let ixx = width * height.powi(3) / 12.0;
    let iyy = height * width.powi(3) / 12.0;
    let sxx = width * height.powi(2) / 6.0;
    Ok((area, ixx, iyy, sxx))
}

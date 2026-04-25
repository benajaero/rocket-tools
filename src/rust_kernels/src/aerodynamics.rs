use pyo3::prelude::*;

#[pyfunction]
fn reynolds_number(velocity: f64, length: f64, kinematic_viscosity: f64) -> PyResult<f64> {
    if kinematic_viscosity <= 0.0 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "kinematic_viscosity must be > 0"
        ));
    }
    Ok(velocity * length / kinematic_viscosity)
}

#[pyfunction]
fn mach_number(velocity: f64, speed_of_sound: f64) -> PyResult<f64> {
    if speed_of_sound <= 0.0 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "speed_of_sound must be > 0"
        ));
    }
    Ok(velocity / speed_of_sound)
}

#[pyfunction]
fn lift_from_coefficient(cl: f64, dynamic_pressure: f64, area: f64) -> PyResult<f64> {
    Ok(cl * dynamic_pressure * area)
}

#[pyfunction]
fn drag_polar_estimate(cd0: f64, k: f64, cl: f64) -> PyResult<(f64, f64)> {
    let cd = cd0 + k * cl.powi(2);
    let ld = if cd.abs() < 1e-12 { f64::INFINITY } else { cl / cd };
    Ok((cd, ld))
}

use pyo3::prelude::*;

mod beams;
mod isa;
mod aerodynamics;

#[pymodule]
fn _rust_kernels(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(beams::beam_bending_stress, m)?)?;
    m.add_function(wrap_pyfunction!(beams::beam_deflection_simply_supported, m)?)?;
    m.add_function(wrap_pyfunction!(beams::beam_deflection_cantilever, m)?)?;
    m.add_function(wrap_pyfunction!(beams::column_euler_buckling, m)?)?;
    m.add_function(wrap_pyfunction!(beams::section_properties_rectangle, m)?)?;
    m.add_function(wrap_pyfunction!(isa::isa_atmosphere_lookup, m)?)?;
    m.add_function(wrap_pyfunction!(aerodynamics::reynolds_number, m)?)?;
    m.add_function(wrap_pyfunction!(aerodynamics::mach_number, m)?)?;
    m.add_function(wrap_pyfunction!(aerodynamics::lift_from_coefficient, m)?)?;
    m.add_function(wrap_pyfunction!(aerodynamics::drag_polar_estimate, m)?)?;
    Ok(())
}

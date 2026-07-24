use pyo3::prelude::*;

const G_STD: f64 = 9.80665;
const R_AIR: f64 = 287.05;
const T0: f64 = 288.15;
const P0: f64 = 101325.0;

#[pyfunction]
pub fn isa_atmosphere_lookup(altitude_m: f64) -> PyResult<(f64, f64, f64, f64)> {
    if !(0.0..=25000.0).contains(&altitude_m) {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Altitude must be 0-25000 m"
        ));
    }

    let (temperature, pressure) = if altitude_m <= 11000.0 {
        let lapse = -0.0065;
        let t = T0 + lapse * altitude_m;
        let p = P0 * (t / T0).powf(-G_STD / (lapse * R_AIR));
        (t, p)
    } else if altitude_m <= 20000.0 {
        let t = 216.65;
        let p11 = 22632.0;
        let p = p11 * (-G_STD * (altitude_m - 11000.0) / (R_AIR * t)).exp();
        (t, p)
    } else {
        let lapse = 0.001;
        let t = 216.65 + lapse * (altitude_m - 20000.0);
        let p20 = 5474.9;
        let p = p20 * (t / 216.65).powf(-G_STD / (lapse * R_AIR));
        (t, p)
    };

    let density = pressure / (R_AIR * temperature);
    let speed_of_sound = (1.4 * R_AIR * temperature).sqrt();

    Ok((temperature, pressure, density, speed_of_sound))
}

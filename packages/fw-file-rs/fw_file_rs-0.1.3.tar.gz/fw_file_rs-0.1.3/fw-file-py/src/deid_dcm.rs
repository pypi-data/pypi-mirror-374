use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use fw_file::deid_dcm::DeidProfile;

#[pyclass]
pub struct PyDeidProfile {
    inner: DeidProfile,
}

#[pymethods]
impl PyDeidProfile {
    #[staticmethod]
    pub fn from_yaml(yaml: &str) -> PyResult<Self> {
        match DeidProfile::from_yaml(yaml) {
            Ok(p) => Ok(Self { inner: p }),
            Err(e) => Err(PyValueError::new_err(e.to_string())),
        }
    }

    pub fn deid_dcm(&self, bytes: &[u8]) -> PyResult<Vec<u8>> {
        match self.inner.deid_dcm(bytes) {
            Ok(new_bytes) => Ok(new_bytes),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }
}

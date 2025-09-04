mod deid_dcm;
mod grouping;
mod testing;

use std::collections::HashMap;
use std::fs::File;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use fw_file::utils::read_until_pixel_data as internal_read_until_pixel_data;
use fw_file::{get_dcm_meta as internal_get_dcm_meta, DicomValue};

#[derive(Debug, IntoPyObject, FromPyObject)]
pub enum PyDicomValue {
    Int(i64),
    Float(f64),
    Str(String),
    Strings(Vec<String>),
    Ints(Vec<i64>),
    Floats(Vec<f64>),
    Unsupported(String),
}

impl From<DicomValue> for PyDicomValue {
    fn from(v: DicomValue) -> Self {
        match v {
            DicomValue::Int(i) => Self::Int(i),
            DicomValue::Float(f) => Self::Float(f),
            DicomValue::Str(s) => Self::Str(s),
            DicomValue::Strings(v) => Self::Strings(v),
            DicomValue::Ints(v) => Self::Ints(v),
            DicomValue::Floats(v) => Self::Floats(v),
            DicomValue::Unsupported(s) => Self::Unsupported(s),
        }
    }
}

#[pyfunction]
fn read_until_pixel_data<'py>(py: Python<'py>, path: &str) -> PyResult<Py<PyBytes>> {
    let mut file = File::open(path)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Could not open file: {}", e)))?;

    let data = internal_read_until_pixel_data(&mut file)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))?;

    Ok(PyBytes::new(py, &data).into())
}

#[pyfunction]
fn get_dcm_meta(
    _py: Python,
    bytes: &[u8],
    tags: Vec<String>,
) -> PyResult<HashMap<String, PyDicomValue>> {
    let tag_refs: Vec<&str> = tags.iter().map(String::as_str).collect();
    let result = internal_get_dcm_meta(bytes, &tag_refs)
        .map_err(|e| PyValueError::new_err(format!("get_dcm_meta failed: {}", e)))?;
    let py_map: HashMap<String, PyDicomValue> = result
        .into_iter()
        .map(|(k, v)| (k, PyDicomValue::from(v)))
        .collect();

    Ok(py_map)
}

#[pymodule]
fn fw_file_rs(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_dcm_meta, m)?)?;
    m.add_function(wrap_pyfunction!(read_until_pixel_data, m)?)?;
    m.add_function(wrap_pyfunction!(grouping::group_dcm_meta, m)?)?;
    m.add_function(wrap_pyfunction!(testing::create_dcm_as_bytes, m)?)?;
    m.add_class::<deid_dcm::PyDeidProfile>()?;
    Ok(())
}

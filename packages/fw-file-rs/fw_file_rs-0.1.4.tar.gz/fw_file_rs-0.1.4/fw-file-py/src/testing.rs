use pyo3::prelude::*;
use pyo3::types::PyBytes;
use smallvec::SmallVec;
use std::collections::HashMap;

use fw_file::testing::create_dcm_as_bytes as internal_create_dcm_as_bytes;
use fw_file::PrimitiveValue;

use crate::PyDicomValue;

#[pyfunction]
pub fn create_dcm_as_bytes(tags: HashMap<String, PyDicomValue>) -> PyResult<Py<PyBytes>> {
    let tags_ref: HashMap<&str, PrimitiveValue> = tags
        .iter()
        .map(|(k, v)| {
            (
                k.as_str(),
                match v {
                    PyDicomValue::Int(i) => PrimitiveValue::from(*i),
                    PyDicomValue::Float(f) => PrimitiveValue::from(*f),
                    PyDicomValue::Str(s) => PrimitiveValue::from(s.clone()),
                    PyDicomValue::Strings(v) => PrimitiveValue::Strs(SmallVec::from_vec(v.clone())),
                    PyDicomValue::Ints(v) => PrimitiveValue::I64(SmallVec::from_slice(v)),
                    PyDicomValue::Floats(v) => PrimitiveValue::F64(SmallVec::from_slice(v)),
                    PyDicomValue::Unsupported(_) => PrimitiveValue::Empty,
                },
            )
        })
        .collect();

    let cursor = internal_create_dcm_as_bytes(tags_ref).map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create DCM: {:?}", e))
    })?;

    let py = unsafe { Python::assume_gil_acquired() }; // acquire Python GIL
    Ok(PyBytes::new(py, &cursor.into_inner()).into())
}

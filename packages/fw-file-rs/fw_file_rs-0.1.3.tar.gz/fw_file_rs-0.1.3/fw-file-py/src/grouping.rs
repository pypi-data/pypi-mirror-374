use pyo3::prelude::*;
use std::collections::HashMap;

use fw_file::grouping;
use fw_file::grouping::DCMGroup;
use fw_file::DicomValue;

use crate::PyDicomValue;

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyDCMGroup {
    #[pyo3(get)]
    paths: Vec<String>,
    #[pyo3(get)]
    is_localizer: bool,
}

impl From<DCMGroup> for PyDCMGroup {
    fn from(group: DCMGroup) -> Self {
        PyDCMGroup {
            paths: group.paths,
            is_localizer: group.is_localizer,
        }
    }
}

#[pyfunction]
pub fn group_dcm_meta(
    py: Python<'_>,
    metas: Vec<(String, HashMap<String, PyDicomValue>)>,
    group_by_tags: Vec<String>,
    split_localizer: bool,
) -> PyResult<Vec<Py<PyDCMGroup>>> {
    let metas: Vec<(String, HashMap<String, DicomValue>)> = metas
        .iter()
        .map(|(path, meta)| {
            (
                path.clone(),
                meta.iter()
                    .map(|(k, v)| {
                        let value = match v {
                            PyDicomValue::Int(i) => DicomValue::Int(*i),
                            PyDicomValue::Float(f) => DicomValue::Float(*f),
                            PyDicomValue::Str(s) => DicomValue::Str(s.clone()),
                            PyDicomValue::Strings(v) => DicomValue::Strings(v.clone()),
                            PyDicomValue::Ints(v) => DicomValue::Ints(v.clone()),
                            PyDicomValue::Floats(v) => DicomValue::Floats(v.clone()),
                            _ => DicomValue::Unsupported("".to_string()),
                        };
                        (k.to_string(), value)
                    })
                    .collect(),
            )
        })
        .collect();

    let groups = grouping::group_dcm_meta(&metas, &group_by_tags, split_localizer);
    Ok(groups
        .into_iter()
        .map(|g| Py::new(py, PyDCMGroup::from(g)).unwrap())
        .collect())
}

pub mod deid_dcm;
pub mod grouping;
pub mod testing;
pub mod utils;

use std::collections::HashMap;
use std::fmt;

use dicom_core::DataDictionary;
use dicom_core::header::Header;
pub use dicom_core::value::PrimitiveValue;
use dicom_dictionary_std::StandardDataDictionary;
use dicom_object::{DefaultDicomObject, from_reader};
use serde::ser::{Serialize, Serializer};

#[derive(Clone, Debug, PartialEq)]
pub enum DicomValue {
    Int(i64),
    Float(f64),
    Str(String),
    Strings(Vec<String>),
    Ints(Vec<i64>),
    Floats(Vec<f64>),
    Unsupported(String),
}

impl Serialize for DicomValue {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        match self {
            DicomValue::Int(i) => serializer.serialize_i64(*i),
            DicomValue::Float(f) => serializer.serialize_f64(*f),
            DicomValue::Str(s) => serializer.serialize_str(s),
            DicomValue::Strings(v) => v.serialize(serializer),
            DicomValue::Ints(v) => v.serialize(serializer),
            DicomValue::Floats(v) => v.serialize(serializer),
            DicomValue::Unsupported(msg) => {
                serializer.serialize_str(&format!("[unsupported: {msg}]"))
            }
        }
    }
}

impl fmt::Display for DicomValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        use DicomValue::*;
        match self {
            Int(v) => write!(f, "{}", v),
            Float(v) => write!(f, "{}", v),
            Str(s) => write!(f, "{}", s),
            Strings(vec) => write!(f, "[{}]", vec.join(", ")),
            Ints(vec) => write!(
                f,
                "[{}]",
                vec.iter()
                    .map(|v| v.to_string())
                    .collect::<Vec<_>>()
                    .join(", ")
            ),
            Floats(vec) => write!(
                f,
                "[{}]",
                vec.iter()
                    .map(|v| v.to_string())
                    .collect::<Vec<_>>()
                    .join(", ")
            ),
            Unsupported(s) => write!(f, "Unsupported({})", s),
        }
    }
}

pub fn get_dcm_meta(bytes: &[u8], tags: &[&str]) -> Result<HashMap<String, DicomValue>, String> {
    let cursor = std::io::Cursor::new(bytes);
    let obj: DefaultDicomObject = from_reader(cursor).map_err(|e| format!("Parse error: {e}"))?;
    let mut map = HashMap::new();

    for tag in tags {
        if let Ok((key, value)) = extract_dcm_values(&obj, tag) {
            map.insert(key, value);
        }
    }

    Ok(map)
}

fn extract_dcm_values(
    obj: &DefaultDicomObject,
    tag_name: &str,
) -> Result<(String, DicomValue), String> {
    // TODO custom error type
    // TODO lower-case tag name support
    // TODO flexible numeric tag support (parens, brackets, space, comma, comma+space, etc.)
    // TODO advanced private tag support (creator + XX)
    let tag = StandardDataDictionary
        .parse_tag(tag_name)
        .ok_or_else(|| format!("Invalid tag name: {tag_name}"))?;

    let elem = obj
        .element(tag)
        .map_err(|e| format!("Missing element: {e}"))?;

    let value = match elem.vr().to_string() {
        "IS" | "SL" | "SS" | "UL" | "US" => match elem.to_multi_int::<i64>() {
            Ok(vs) => {
                if vs.len() == 1 {
                    DicomValue::Int(vs[0])
                } else {
                    DicomValue::Ints(vs)
                }
            }
            Err(_) => DicomValue::Unsupported("Invalid int value".to_string()),
        },
        "FL" | "FD" | "DS" => match elem.to_multi_float64() {
            Ok(vs) => {
                if vs.len() == 1 {
                    DicomValue::Float(vs[0])
                } else {
                    DicomValue::Floats(vs)
                }
            }
            Err(_) => DicomValue::Unsupported("Invalid float value".to_string()),
        },
        "SQ" => DicomValue::Unsupported("Sequence not supported".to_string()),
        _ => match elem.to_multi_str() {
            Ok(vs) => {
                let strings: Vec<String> = vs.iter().map(|s| s.to_string()).collect();
                if strings.len() == 1 {
                    DicomValue::Str(strings[0].clone())
                } else {
                    DicomValue::Strings(strings)
                }
            }
            Err(_) => DicomValue::Unsupported("Invalid string value".to_string()),
        },
    };

    let tag_name_str = match StandardDataDictionary.by_tag(elem.tag()) {
        Some(dict_entry) => dict_entry.alias.to_string(),
        None => tag_name.to_string(),
    };
    Ok((tag_name_str, value))
}

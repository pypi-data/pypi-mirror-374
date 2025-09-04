use serde::Deserialize;
use serde_yaml::Value;
use thiserror::Error;

use chrono::{NaiveDate, NaiveDateTime, NaiveTime};
use dicom_core::DataDictionary;
use dicom_core::Tag;
use dicom_core::VR;
use dicom_core::dictionary::DataDictionaryEntry;
use dicom_dictionary_std::StandardDataDictionary;
use dicom_object::mem::InMemDicomObject;

#[derive(Debug, Error)]
pub enum ProfileParseError {
    #[error("YAML parse error: {0}")]
    YamlError(String),

    #[error("Profile validation failed: {0:?}")]
    ValidationError(Vec<String>),

    #[error("Unsupported profile version: {0}")]
    UnsupportedVersion(u32),
}

#[derive(Debug)]
pub enum DeidProfile {
    V1(DeidProfileV1),
}

impl DeidProfile {
    pub fn from_yaml(yaml_data: &str) -> Result<DeidProfile, ProfileParseError> {
        let raw: Value = serde_yaml::from_str(yaml_data)
            .map_err(|e| ProfileParseError::YamlError(e.to_string()))?;
        let version = raw.get("version").and_then(|v| v.as_u64()).unwrap_or(1);
        match version {
            1 => {
                let v1: DeidProfileV1 = serde_yaml::from_value(raw)
                    .map_err(|e| ProfileParseError::YamlError(e.to_string()))?;
                Ok(DeidProfile::V1(v1))
            }
            v => Err(ProfileParseError::UnsupportedVersion(v as u32)),
        }
    }

    pub fn deid_dcm(&self, dcm: &[u8]) -> Result<Vec<u8>, String> {
        match self {
            DeidProfile::V1(profile) => profile.deid(dcm),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct DeidProfileV1 {
    pub name: Option<String>,
    pub dicom: Option<DicomSectionV1>,
}

impl DeidProfileV1 {
    pub fn deid(&self, dcm: &[u8]) -> Result<Vec<u8>, String> {
        match self.dicom {
            Some(ref dicom) => dicom.deid(dcm),
            None => Ok(dcm.to_vec()),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct DicomSectionV1 {
    pub fields: Option<Vec<FieldSpecV1>>,
}

impl DicomSectionV1 {
    pub fn deid(&self, dcm: &[u8]) -> Result<Vec<u8>, String> {
        // TODO collect errors and return them all at once
        let mut obj =
            dicom_object::from_reader(dcm).map_err(|e| format!("Failed to parse DICOM: {e}"))?;

        if let Some(ref fields) = self.fields {
            for field in fields {
                if let Some(name) = &field.name {
                    let tag = StandardDataDictionary
                        .parse_tag(name)
                        .ok_or_else(|| format!("Invalid tag name: {name}"))?;

                    if field.remove.unwrap_or(false) {
                        obj.remove_element(tag);
                    } else if let Some(ref val) = field.replace_with {
                        apply_replace_with(&mut obj, tag, val)
                            .map_err(|e| format!("Failed apply replace-with action: {e}"))?;
                    }
                }
            }
        }

        let mut out = Vec::new();
        obj.write_all(&mut out)
            .map_err(|e| format!("Failed to write DICOM: {e}"))?;
        Ok(out)
    }
}

#[derive(Debug, Deserialize)]
pub struct FieldSpecV1 {
    pub name: Option<String>,
    #[serde(rename = "replace-with")]
    pub replace_with: Option<String>,
    pub remove: Option<bool>,
}

fn validate_vr_value(vr: VR, value: &str) -> Result<(), String> {
    if value.is_empty() {
        return Ok(());
    }
    match vr {
        VR::DA => {
            NaiveDate::parse_from_str(value, "%Y%m%d")
                .map_err(|_| format!("{value} cannot be parsed as DA"))?;
        }
        VR::TM => {
            let fmts = ["%H", "%H%M", "%H%M%S", "%H%M%S%.f"];
            if !fmts
                .iter()
                .any(|f| NaiveTime::parse_from_str(value, f).is_ok())
            {
                return Err(format!("{value} cannot be parsed as TM"));
            }
        }
        VR::DT => {
            let fmts = [
                "%Y%m%d%H%M%S",
                "%Y%m%d%H%M%S%.f",
                "%Y%m%d%H%M",
                "%Y%m%d%H",
                "%Y%m%d",
            ];
            if !fmts
                .iter()
                .any(|f| NaiveDateTime::parse_from_str(value, f).is_ok())
            {
                return Err(format!("{value} cannot be parsed as DT"));
            }
        }
        VR::DS | VR::FL | VR::FD => {
            if value.split('\\').any(|v| v.trim().parse::<f64>().is_err()) {
                return Err(format!("{value} cannot be parsed as {vr:?}"));
            }
        }
        VR::IS | VR::SL | VR::SS | VR::UL | VR::US => {
            if value.split('\\').any(|v| v.trim().parse::<i64>().is_err()) {
                return Err(format!("{value} cannot be parsed as {vr:?}"));
            }
        }
        _ => {}
    }
    Ok(())
}

pub fn apply_replace_with(
    obj: &mut InMemDicomObject,
    tag: Tag,
    new_text: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    let vr = match obj.element(tag) {
        Ok(el) => el.header().vr(),
        Err(_) => resolve_vr(tag),
    };
    validate_vr_value(vr, new_text).map_err(|e| format!("{tag}: {e}"))?;
    // TODO put_str returns previous value so we can use it tracking changes
    obj.put_str(tag, vr, new_text);
    Ok(())
}

fn resolve_vr(tag: Tag) -> VR {
    if let Some(entry) = StandardDataDictionary.by_tag(tag) {
        let vvr = entry.vr();
        vvr.exact().unwrap_or_else(|| vvr.relaxed())
    } else {
        VR::UN
    }
}

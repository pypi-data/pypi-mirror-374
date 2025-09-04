use dicom_core::value::PrimitiveValue;
use std::collections::HashMap;

use fw_file::deid_dcm::{DeidProfile, DicomSectionV1, FieldSpecV1, ProfileParseError};
use fw_file::testing::create_dcm_as_bytes;

#[test]
fn test_deid_replace_with_valid_date() {
    let tags = HashMap::from([
        ("PatientName", PrimitiveValue::from("Test^Patient")),
        ("StudyDate", PrimitiveValue::from("20000101")),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let spec = FieldSpecV1 {
        name: Some("StudyDate".into()),
        replace_with: Some("20220101".into()),
        remove: None,
    };
    let section = DicomSectionV1 {
        fields: Some(vec![spec]),
    };
    let result = section.deid(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    assert_eq!(val, "20220101");
}

#[test]
fn test_deid_remove_field() {
    let tags = HashMap::from([
        ("PatientName", PrimitiveValue::from("Test^Patient")),
        ("PatientID", PrimitiveValue::from("123456")),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: PatientID
      remove: true
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    assert!(obj.element_by_name("PatientID").is_err());
    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Test^Patient");
}

#[test]
fn test_validate_vr_date_invalid() {
    let tags = HashMap::from([("StudyDate", PrimitiveValue::from("20000101"))]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: StudyDate
      replace-with: "notadate"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let err = profile.deid_dcm(&dcm).unwrap_err();
    assert!(err.contains("cannot be parsed as DA"));
}

#[test]
fn test_deid_replace_patient_name() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;

    let tags = HashMap::from([("PatientName", PrimitiveValue::from("Test^Patient"))]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Anon^Patient");
}

#[test]
fn test_profile_unsupported_version() {
    let yaml = r#"
version: 99
name: test
dicom: {}
"#;

    let err = DeidProfile::from_yaml(yaml).unwrap_err();
    match err {
        ProfileParseError::UnsupportedVersion(v) => assert_eq!(v, 99),
        e => panic!("Expected UnsupportedVersion, got {e:?}"),
    }
}

use std::collections::HashMap;

use fw_file::testing::create_dcm_as_bytes;
use fw_file::{DicomValue, PrimitiveValue, get_dcm_meta};

#[test]
fn test_get_dcm_meta() {
    let tags = HashMap::from([
        ("PatientName", PrimitiveValue::from("Test^Patient")),
        ("PatientID", PrimitiveValue::from("123456")),
    ]);

    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let bytes = buffer.get_ref();

    let meta = get_dcm_meta(bytes, &["PatientName"]).expect("Failed to get DICOM meta");
    let patient_name = meta.get("PatientName").expect("Missing PatientName");

    assert_eq!(
        patient_name,
        &DicomValue::Str("Test^Patient".to_string()),
        "Unexpected PatientName value"
    );
}

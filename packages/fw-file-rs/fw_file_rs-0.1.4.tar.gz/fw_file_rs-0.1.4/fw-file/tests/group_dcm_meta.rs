use std::collections::HashMap;

use fw_file::DicomValue;
use fw_file::grouping::group_dcm_meta;

#[test]
fn test_group_dcm_meta_with_localizer() {
    let mut metas = vec![];

    for i in 1..=6 {
        metas.push((
            format!("f{i}"),
            HashMap::from([
                (
                    "StudyInstanceUID".to_string(),
                    DicomValue::Str("1".to_string()),
                ),
                (
                    "SeriesInstanceUID".to_string(),
                    DicomValue::Str("1.2".to_string()),
                ),
                ("InstanceNumber".to_string(), DicomValue::Int(i)),
                (
                    "ImageOrientationPatient".to_string(),
                    DicomValue::Floats(vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                ),
                (
                    "ImagePositionPatient".to_string(),
                    DicomValue::Floats(vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                ),
                ("Rows".to_string(), DicomValue::Int(256)),
                ("Columns".to_string(), DicomValue::Int(256)),
            ]),
        ));
    }

    for i in 7..=11 {
        metas.push((
            format!("f{i}"),
            HashMap::from([
                (
                    "StudyInstanceUID".to_string(),
                    DicomValue::Str("1".to_string()),
                ),
                (
                    "SeriesInstanceUID".to_string(),
                    DicomValue::Str("1.2".to_string()),
                ),
                ("InstanceNumber".to_string(), DicomValue::Int(i)),
                (
                    "ImageOrientationPatient".to_string(),
                    DicomValue::Floats(vec![0.0, 1.0, 0.0, 0.0, 0.0, 0.0]),
                ),
                (
                    "ImagePositionPatient".to_string(),
                    DicomValue::Floats(vec![0.0, 1.0, 0.0, 0.0, 0.0, 0.0]),
                ),
                ("Rows".to_string(), DicomValue::Int(256)),
                ("Columns".to_string(), DicomValue::Int(256)),
            ]),
        ));
    }

    let group_by_tags = vec!["StudyInstanceUID".into(), "SeriesInstanceUID".into()];
    let groups = group_dcm_meta(&metas, &group_by_tags, true);

    assert!(groups.len() == 2);
    for group in &groups {
        if !group.is_localizer {
            assert_eq!(group.paths, vec!["f1", "f2", "f3", "f4", "f5", "f6"]);
        } else {
            assert_eq!(group.paths, vec!["f7", "f8", "f9", "f10", "f11"]);
        }
    }
}

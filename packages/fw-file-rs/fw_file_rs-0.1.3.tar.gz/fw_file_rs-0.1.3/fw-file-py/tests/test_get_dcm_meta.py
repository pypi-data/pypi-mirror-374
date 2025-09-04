from fw_file_rs import create_dcm_as_bytes, get_dcm_meta


def test_get_dcm_meta():
    dcm_bytes = create_dcm_as_bytes(
        {"PatientID": "test", "ImageOrientationPatient": [1, 0, 0, 0, 1, 0]}
    )
    meta = get_dcm_meta(dcm_bytes, ["PatientID", "ImageOrientationPatient"])
    assert meta == {"PatientID": "test", "ImageOrientationPatient": [1, 0, 0, 0, 1, 0]}

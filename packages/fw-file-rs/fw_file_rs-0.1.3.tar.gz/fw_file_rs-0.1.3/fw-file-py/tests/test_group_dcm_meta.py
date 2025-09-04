from fw_file_rs import group_dcm_meta

def test_group_dcm_meta():
    metas = []
    for i in range(6):
        metas.append((f"f{i+1}", {
            "StudyInstanceUID": "1",
            "SeriesInstanceUID": "1.2",
            "InstanceNumber": i + 1,
            "ImageOrientationPatient": [1, 0, 0, 0, 0, 0],
            "ImagePositionPatient": [1, 0, 0, 0, 0, 0],
            "Rows": 256,
            "Columns": 256,
        }))
    for i in range(6, 11):
        metas.append((f"f{i+1}", {
            "StudyInstanceUID": "1",
            "SeriesInstanceUID": "1.2",
            "InstanceNumber": i + 1,
            "ImageOrientationPatient": [0, 1, 0, 0, 0, 0],
            "ImagePositionPatient": [0, 1, 0, 0, 0, 0],
            "Rows": 256,
            "Columns": 256,
        }))
    groups = group_dcm_meta(metas, ["StudyInstanceUID", "SeriesInstanceUID"], True)
    assert len(groups) == 2
    assert not groups[0].is_localizer
    assert groups[0].paths == ["f1", "f2", "f3", "f4", "f5", "f6"]
    assert groups[1].is_localizer
    assert groups[1].paths == ["f7", "f8", "f9", "f10", "f11"]

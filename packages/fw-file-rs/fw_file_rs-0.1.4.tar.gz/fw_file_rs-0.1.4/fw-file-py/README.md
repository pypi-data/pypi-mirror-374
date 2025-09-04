# fw-file-rs

Python bindings for the [fw-file-rs][fw-file-rs-repo] Rust library.

## Usage

```py
from fw_file_rs import PyDeidProfile, get_dcm_meta

dcm_bytes = read_until_pixel_data("/path/to/dicom/file.dcm")
# extract metadata from a DICOM file
tags = [
    "StudyInstanceUID",
    "SeriesInstanceUID",
    # tags below are needed for splitting localizer
    "InstanceNumber",
    "ImagePositionPatient",
    "ImageOrientationPatient",
    "Rows",
    "Columns",
]
meta = get_dcm_meta(dcm_bytes, tags)
# group DICOM files by StudyInstanceUID and SeriesInstanceUID and split localizer
metas = [meta]  # multiple meta
groups = group_dcm_meta(metas, ["StudyInstanceUID", "SeriesInstanceUID"], True)

# de-identify a DICOM file using a YAML profile
yaml = """
version: 1
name: profile
dicom:
fields:
- name: PatientName
  replace-with: REDACTED
"""
profile = PyDeidProfile.from_yaml(dcm_bytes)
result = profile.deid_dcm(dcm)
```

[fw-file-rs-repo]: https://gitlab.com/flywheel-io/tools/lib/fw-file-rs

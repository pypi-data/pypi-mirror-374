use std::collections::HashMap;
use std::io::{Cursor, Error, ErrorKind, Result, Write};

use dicom_core::DataDictionary;
use dicom_core::header::{DataElement, VR};
use dicom_core::value::PrimitiveValue;
use dicom_dictionary_std::StandardDataDictionary;
use dicom_object::FileMetaTableBuilder;
use dicom_object::mem::InMemDicomObject;
use dicom_transfer_syntax_registry::entries::EXPLICIT_VR_LITTLE_ENDIAN;

pub fn create_dcm_as_bytes(tags: HashMap<&str, PrimitiveValue>) -> Result<Cursor<Vec<u8>>> {
    // TODO support setting VR explicitly
    let mut obj = InMemDicomObject::new_empty();

    for (tag_name, value) in tags {
        let tag = StandardDataDictionary.parse_tag(&tag_name).unwrap();
        let virtual_vr = StandardDataDictionary
            .by_tag(tag)
            .map(|entry| entry.vr)
            .unwrap_or(dicom_core::dictionary::VirtualVr::Exact(VR::UN));
        let vr = match virtual_vr {
            dicom_core::dictionary::VirtualVr::Exact(vr) => vr,
            _ => VR::UN,
        };
        obj.put(DataElement::new(tag, vr, value));
    }

    let ts = EXPLICIT_VR_LITTLE_ENDIAN.erased();
    let file_meta = FileMetaTableBuilder::new()
        .media_storage_sop_class_uid("1.2.840.10008.5.1.4.1.1.2")
        .media_storage_sop_instance_uid("1.2.3.4.5.6.7.8.9")
        .transfer_syntax(EXPLICIT_VR_LITTLE_ENDIAN.uid())
        .implementation_class_uid("1.2.3.4.5.6.7.8.9.10")
        .build()
        .map_err(|e| Error::new(ErrorKind::Other, e.to_string()))?;

    let mut buffer = Cursor::new(Vec::new());
    buffer.write(&[0u8; 128])?;
    buffer.write(b"DICM")?;
    file_meta
        .write(&mut buffer)
        .map_err(|e| Error::new(ErrorKind::Other, e.to_string()))?;

    obj.write_dataset_with_ts(&mut buffer, &ts)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("Write error: {e}")))?;

    buffer.set_position(0);
    Ok(buffer)
}

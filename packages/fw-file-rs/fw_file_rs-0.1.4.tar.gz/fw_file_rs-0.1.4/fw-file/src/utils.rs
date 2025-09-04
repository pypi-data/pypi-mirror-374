use std::fs::File;
use std::io::{self, Read, Seek, SeekFrom};

pub fn read_until_pixel_data(file: &mut File) -> Result<Vec<u8>, String> {
    let tags_to_stop = &[
        (0x7FE0, 0x0008),
        (0x7FE0, 0x0009),
        (0x7FE0, 0x0010),
        (0x0067, 0x1018),
    ];
    let result = find_tag_offset(file, 10_000_000, tags_to_stop)
        .map_err(|e| format!("Error finding pixel data: {}", e))?;
    if let Some((_, before_bytes)) = result {
        return Ok(before_bytes);
    }
    Ok(Vec::new())
}

pub fn find_tag_offset(
    file: &mut File,
    chunk_size: usize,
    stop_tags: &[(u16, u16)],
) -> io::Result<Option<(u64, Vec<u8>)>> {
    let meta = read_bytes(file, 0, 2048)?;
    let ts_uid = detect_transfer_syntax(&meta)?;
    let big_endian = ts_uid == "1.2.840.10008.1.2.2";

    let patterns: Vec<[u8; 4]> = stop_tags
        .iter()
        .map(|&tag| {
            let (le, be) = make_tag_patterns(tag);
            if big_endian { be } else { le }
        })
        .collect();

    let mut offset: u64 = 0;
    let mut prev_tail: Vec<u8> = Vec::new();
    let mut collected: Vec<u8> = Vec::new();
    let file_size = file.metadata()?.len();

    while offset < file_size {
        let mut chunk = read_bytes(file, offset, chunk_size)?;
        if !prev_tail.is_empty() {
            let mut combined = prev_tail.clone();
            combined.extend_from_slice(&chunk);
            chunk = combined;
        }

        if let Some(pos) = find_any_tag_in_buffer(&chunk, &patterns) {
            let absolute_pos = offset.saturating_sub(prev_tail.len() as u64) + pos as u64;
            collected.extend_from_slice(&chunk[..pos]);
            return Ok(Some((absolute_pos, collected)));
        }

        if chunk.len() > 3 {
            collected.extend_from_slice(&chunk[..chunk.len() - 3]);
            prev_tail = chunk[chunk.len() - 3..].to_vec();
        } else {
            prev_tail = chunk;
        }

        offset += chunk_size as u64;
    }

    Ok(None)
}

fn read_bytes(file: &mut File, offset: u64, length: usize) -> io::Result<Vec<u8>> {
    file.seek(SeekFrom::Start(offset))?;
    let mut buffer = vec![0u8; length];
    let bytes_read = file.read(&mut buffer)?;
    buffer.truncate(bytes_read);
    Ok(buffer)
}

pub fn detect_transfer_syntax(meta: &[u8]) -> io::Result<String> {
    let ts_tag = [0x02, 0x00, 0x10, 0x00];
    if let Some(pos) = meta.windows(4).position(|w| w == ts_tag) {
        let len_pos = pos + 6;
        let len = u16::from_le_bytes([meta[len_pos], meta[len_pos + 1]]) as usize;
        let value_pos = len_pos + 2;
        if value_pos + len <= meta.len() {
            let raw_uid = &meta[value_pos..value_pos + len];
            return Ok(String::from_utf8_lossy(raw_uid)
                .trim_end_matches('\0')
                .to_string());
        }
    }
    Err(io::Error::new(
        io::ErrorKind::Other,
        "Could not detect Transfer Syntax UID",
    ))
}

pub fn make_tag_patterns(tag: (u16, u16)) -> ([u8; 4], [u8; 4]) {
    let (group, element) = tag;
    let g_le = group.to_le_bytes();
    let e_le = element.to_le_bytes();
    let le = [g_le[0], g_le[1], e_le[0], e_le[1]];
    let g_be = group.to_be_bytes();
    let e_be = element.to_be_bytes();
    let be = [g_be[0], g_be[1], e_be[0], e_be[1]];
    (le, be)
}

pub fn find_any_tag_in_buffer(buf: &[u8], patterns: &[[u8; 4]]) -> Option<usize> {
    for pattern in patterns {
        if let Some(pos) = buf.windows(4).position(|w| w == pattern) {
            return Some(pos);
        }
    }
    None
}

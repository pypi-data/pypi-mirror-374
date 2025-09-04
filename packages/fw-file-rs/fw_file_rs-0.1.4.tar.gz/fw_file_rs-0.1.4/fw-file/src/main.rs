use std::env;
use std::fs::File;
use std::process;

use fw_file::get_dcm_meta;
use fw_file::utils::read_until_pixel_data;

fn main() {
    let args: Vec<String> = env::args().collect();
    let file_path = &args[1];
    let mut file = File::open(file_path).unwrap();
    let bytes = read_until_pixel_data(&mut file).unwrap();
    let tags: Vec<&str> = args.iter().skip(2).map(|s| s.as_str()).collect();
    match get_dcm_meta(&bytes, &tags) {
        Ok(meta) => {
            println!("Parsed metadata:");
            for (key, value) in meta {
                println!("{key}: {value:?}");
            }
        }
        Err(err) => {
            eprintln!("Error parsing DICOM: {err}");
            process::exit(1);
        }
    }
}

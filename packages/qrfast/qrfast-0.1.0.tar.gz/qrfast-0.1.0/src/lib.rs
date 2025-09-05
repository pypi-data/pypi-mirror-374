use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use rxing::{DecodeHintType, DecodingHintDictionary, Exceptions};

#[pyfunction]
fn decode_qr(file_path: &str, try_harder: Option<bool>) -> PyResult<Option<String>> {
    let mut hints = DecodingHintDictionary::new();
    if try_harder.unwrap_or(true) {
        hints.insert(
            DecodeHintType::TRY_HARDER,
            rxing::DecodeHintValue::TryHarder(true),
        );
    }

    let res = rxing::helpers::detect_multiple_in_file_with_hints(file_path, &mut hints);

    match res {
        Ok(mut codes) if !codes.is_empty() => {
            let text = codes.remove(0).getText().to_string();
            Ok(Some(text))
        }
        Ok(_) => Ok(None),

        Err(Exceptions::NotFoundException(_)) => Ok(None),
        Err(e) => Err(PyRuntimeError::new_err(format!("QR decode error: {e:?}"))),
    }
}

#[pyfunction]
fn decode_qr_bytes(
    file_bytes: &[u8],
    width: u32,
    height: u32,
    try_harder: Option<bool>,
) -> PyResult<Option<String>> {
    let mut hints = DecodingHintDictionary::new();
    if try_harder.unwrap_or(true) {
        hints.insert(
            DecodeHintType::TRY_HARDER,
            rxing::DecodeHintValue::TryHarder(true),
        );
    }

    let file_bytes = file_bytes.to_vec();

    let res =
        rxing::helpers::detect_multiple_in_luma_with_hints(file_bytes, width, height, &mut hints);

    match res {
        Ok(mut codes) if !codes.is_empty() => {
            let text = codes.remove(0).getText().to_string();
            Ok(Some(text))
        }
        Ok(_) => Ok(None),

        Err(Exceptions::NotFoundException(_)) => Ok(None),
        Err(e) => Err(PyRuntimeError::new_err(format!("QR decode error: {e:?}"))),
    }
}

#[pymodule]
fn qrfast(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(decode_qr, m)?)?;
    m.add_function(wrap_pyfunction!(decode_qr_bytes, m)?)?;
    Ok(())
}

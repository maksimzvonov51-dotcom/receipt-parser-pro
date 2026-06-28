from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from receipt_parser.parser import parse_receipt_text
from receipt_parser.text_extractor import extract_text
from receipt_parser.exporter import export_to_csv_bytes, export_to_excel_bytes

st.set_page_config(page_title="Receipt Parser Pro", page_icon="🧾", layout="wide")
st.title("Receipt Parser Pro")
st.write("Upload PDF or image receipts. The app extracts vendor, date, total, VAT and currency.")

ocr_lang = st.text_input("OCR language", value="eng+deu", help="Examples: eng, deu, eng+deu. Requires installed Tesseract language packs.")
uploaded_files = st.file_uploader(
    "Receipts / invoices",
    type=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"],
    accept_multiple_files=True,
)

if uploaded_files:
    rows = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded in uploaded_files:
            path = Path(temp_dir) / uploaded.name
            path.write_bytes(uploaded.getbuffer())
            try:
                text = extract_text(path, ocr_lang=ocr_lang)
                data = parse_receipt_text(text, source_path=path)
                rows.append(data.to_dict())
            except Exception as exc:
                rows.append({
                    "file_name": uploaded.name,
                    "vendor": None,
                    "date": None,
                    "total": None,
                    "vat": None,
                    "currency": None,
                    "raw_text": f"ERROR: {exc}",
                })
    df = pd.DataFrame(rows)
    st.subheader("Results")
    st.dataframe(df.drop(columns=["raw_text"]), use_container_width=True)

    export_rows = df.drop(columns=["raw_text"]).to_dict(orient="records")

    csv_data = export_to_csv_bytes(export_rows)
    st.download_button(
        "Download CSV",
        csv_data,
        "receipts.csv",
        "text/csv",
    )

    excel_data = export_to_excel_bytes(export_rows)
    st.download_button(
        "Download Excel",
        excel_data,
        "receipts.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("Raw OCR text")
    for row in rows:
        with st.expander(row["file_name"]):
            st.text(row.get("raw_text") or "")
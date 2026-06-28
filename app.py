from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from receipt_parser.parser import parse_receipt_text
from receipt_parser.text_extractor import extract_text
from receipt_parser.exporter import export_to_csv_bytes, export_to_excel_bytes


st.set_page_config(
    page_title="Receipt Parser Pro",
    page_icon="🧾",
    layout="wide",
)


def is_successful_row(row: dict) -> bool:
    """
    A file is counted as successfully parsed if there was no technical error
    and at least one important business field was detected.
    """
    if row.get("status") != "success":
        return False

    important_fields = [
        row.get("vendor"),
        row.get("date"),
        row.get("total"),
        row.get("vat"),
        row.get("currency"),
    ]

    return any(value not in [None, "", "None"] for value in important_fields)


def build_summary(rows: list[dict]) -> dict:
    total_files = len(rows)
    successfully_parsed = sum(1 for row in rows if is_successful_row(row))
    failed = total_files - successfully_parsed

    total_amount = sum(
        row.get("total") or 0
        for row in rows
        if isinstance(row.get("total"), (int, float))
    )

    total_vat = sum(
        row.get("vat") or 0
        for row in rows
        if isinstance(row.get("vat"), (int, float))
    )

    return {
        "total_files": total_files,
        "successfully_parsed": successfully_parsed,
        "failed": failed,
        "total_amount": round(total_amount, 2),
        "total_vat": round(total_vat, 2),
    }


st.title("Receipt Parser Pro")
st.write(
    "Upload receipts or invoices as PDF/images. "
    "The app extracts vendor, date, total amount, VAT and currency."
)

ocr_lang = st.text_input(
    "OCR language",
    value="eng+deu",
    help="Examples: eng, deu, eng+deu. Requires installed Tesseract language packs.",
)

uploaded_files = st.file_uploader(
    "Receipts / invoices",
    type=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"],
    accept_multiple_files=True,
)

if not uploaded_files:
    st.info("Upload one or more receipt or invoice files to start parsing.")

if uploaded_files:
    rows = []

    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded in uploaded_files:
            path = Path(temp_dir) / uploaded.name
            path.write_bytes(uploaded.getbuffer())

            try:
                text = extract_text(path, ocr_lang=ocr_lang)
                data = parse_receipt_text(text, source_path=path)
                row = data.to_dict()

                row["status"] = "success"
                row["error"] = ""
                rows.append(row)

            except Exception as exc:
                rows.append(
                    {
                        "file_name": uploaded.name,
                        "vendor": None,
                        "date": None,
                        "total": None,
                        "vat": None,
                        "currency": None,
                        "status": "error",
                        "error": str(exc),
                        "raw_text": "",
                    }
                )

    summary = build_summary(rows)

    st.subheader("Summary dashboard")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total files", summary["total_files"])
    col2.metric("Successfully parsed", summary["successfully_parsed"])
    col3.metric("Failed", summary["failed"])
    col4.metric("Total amount", f'{summary["total_amount"]:.2f}')
    col5.metric("Total VAT", f'{summary["total_vat"]:.2f}')

    if summary["failed"] > 0:
        st.warning(
            "Some files could not be parsed completely. "
            "Check the error details and raw OCR text below."
        )
    else:
        st.success("All uploaded files were processed successfully.")

    st.subheader("Results")

    df = pd.DataFrame(rows)

    display_columns = [
        "file_name",
        "status",
        "vendor",
        "date",
        "total",
        "vat",
        "currency",
        "error",
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
    )

    export_columns = [
        "file_name",
        "status",
        "vendor",
        "date",
        "total",
        "vat",
        "currency",
        "error",
    ]

    export_rows = df[export_columns].to_dict(orient="records")

    col_csv, col_excel = st.columns(2)

    with col_csv:
        csv_data = export_to_csv_bytes(export_rows)
        st.download_button(
            "Download CSV",
            csv_data,
            "receipts.csv",
            "text/csv",
        )

    with col_excel:
        excel_data = export_to_excel_bytes(export_rows)
        st.download_button(
            "Download Excel",
            excel_data,
            "receipts.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.subheader("Errors")

    error_rows = [row for row in rows if row.get("status") == "error"]

    if error_rows:
        for row in error_rows:
            with st.expander(row["file_name"]):
                st.error(row["error"])
    else:
        st.write("No technical errors detected.")

    st.subheader("Raw OCR text")

    for row in rows:
        with st.expander(row["file_name"]):
            raw_text = row.get("raw_text") or ""

            if raw_text:
                st.text(raw_text)
            else:
                st.write("No OCR text available.")
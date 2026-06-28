from io import BytesIO

import pandas as pd


def export_to_csv_bytes(data: list[dict]) -> bytes:
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode("utf-8")


def export_to_excel_bytes(data: list[dict]) -> bytes:
    output = BytesIO()
    df = pd.DataFrame(data)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Receipts")

        worksheet = writer.sheets["Receipts"]

        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:
                value = cell.value
                if value is not None:
                    max_length = max(max_length, len(str(value)))

            worksheet.column_dimensions[column_letter].width = max_length + 2

    output.seek(0)
    return output.getvalue()
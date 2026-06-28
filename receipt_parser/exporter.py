from pathlib import Path
from typing import Iterable

import pandas as pd

from .models import ReceiptData


def export_results(receipts: Iterable[ReceiptData], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    rows = [receipt.to_dict() for receipt in receipts]
    df = pd.DataFrame(rows, columns=["file_name", "vendor", "date", "total", "vat", "currency", "raw_text"])

    if output.suffix.lower() == ".csv":
        df.to_csv(output, index=False, encoding="utf-8-sig")
    elif output.suffix.lower() in {".xlsx", ".xls"}:
        df.to_excel(output, index=False)
    else:
        raise ValueError("Output must be .csv or .xlsx")

    return output

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .exporter import export_results
from .parser import parse_receipt_text
from .text_extractor import iter_supported_files, extract_text

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="receipt-parser",
        description="Extract vendor, date, total, VAT and currency from receipts/invoices into CSV or Excel.",
    )
    parser.add_argument("input", help="File or folder with PDF/image receipts")
    parser.add_argument("-o", "--output", default="output/receipts.xlsx", help="Output .xlsx or .csv path")
    parser.add_argument("--ocr-lang", default="eng+deu", help="Tesseract language pack, e.g. eng, deu, eng+deu")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    files = list(iter_supported_files(args.input))

    if not files:
        console.print("[red]No supported files found.[/red]")
        raise SystemExit(1)

    receipts = []
    for path in files:
        console.print(f"Processing: {path}")
        try:
            text = extract_text(path, ocr_lang=args.ocr_lang)
            receipts.append(parse_receipt_text(text, source_path=path))
        except Exception as exc:
            console.print(f"[red]Failed: {path.name}: {exc}[/red]")

    if not receipts:
        console.print("[red]No receipts parsed.[/red]")
        raise SystemExit(1)

    output = export_results(receipts, args.output)
    _print_table(receipts)
    console.print(f"\n[green]Saved:[/green] {output}")


def _print_table(receipts) -> None:
    table = Table(title="Parsed receipts")
    table.add_column("File")
    table.add_column("Vendor")
    table.add_column("Date")
    table.add_column("Total")
    table.add_column("VAT")
    table.add_column("Currency")

    for receipt in receipts:
        table.add_row(
            receipt.file_name,
            receipt.vendor or "",
            receipt.date or "",
            str(receipt.total or ""),
            str(receipt.vat or ""),
            receipt.currency or "",
        )
    console.print(table)


if __name__ == "__main__":
    main()

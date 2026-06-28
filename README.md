# Receipt Parser Pro

Receipt Parser Pro extracts useful data from receipts and invoices and exports it to CSV or Excel.

It can process PDF files and image files such as PNG, JPG, TIFF, BMP and WEBP.

## Features

- Extract vendor name
- Extract date
- Extract total amount
- Extract VAT / tax amount
- Detect common currencies: EUR, USD, GBP, RUB
- Export to `.xlsx` or `.csv`
- Command line interface
- Optional Streamlit web interface

## Tech stack

- Python
- pdfplumber
- pytesseract
- pandas
- openpyxl
- Streamlit

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/receipt-parser-pro.git
cd receipt-parser-pro
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Install Tesseract OCR

This project uses Tesseract OCR for images and scanned PDFs.

Windows:

Install Tesseract from the official UB Mannheim Windows builds, then add the Tesseract folder to your PATH.

macOS:

```bash
brew install tesseract
```

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu
```

## Usage: command line

Process one file:

```bash
python -m receipt_parser.cli examples/receipt.pdf -o output/receipts.xlsx
```

Process a full folder:

```bash
python -m receipt_parser.cli ./my_receipts -o output/receipts.csv
```

Use a specific OCR language:

```bash
python -m receipt_parser.cli ./my_receipts -o output/receipts.xlsx --ocr-lang eng+deu
```

## Usage: web interface

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Output columns

| Column | Meaning |
|---|---|
| file_name | Source file name |
| vendor | Detected vendor / shop / company |
| date | Detected receipt date |
| total | Detected total amount |
| vat | Detected VAT / tax amount |
| currency | Detected currency |
| raw_text | Extracted OCR/text layer content |

## Limitations

This is a heuristic parser, not a certified accounting system. OCR quality depends on image quality, language packs and receipt layout. Always verify extracted values before using them for accounting or tax filings.

## Monetization idea

Free version:

- Manual upload
- CSV export
- Basic parsing

Paid version:

- Batch processing
- Excel export
- Custom templates
- Better vendor detection
- Cloud storage integration
- Accounting software export

## License

MIT
## Screenshot
![Receipt Parser Pro screenshot](assets/screenshot.png)
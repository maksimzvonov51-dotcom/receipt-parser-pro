from receipt_parser.parser import parse_receipt_text


def test_parse_simple_receipt():
    text = """
    Coffee Shop GmbH
    Rechnung
    Datum: 12.05.2026
    MwSt 1,90
    Gesamt 11,90 EUR
    """
    data = parse_receipt_text(text, "receipt.pdf")
    assert data.vendor == "Coffee Shop GmbH"
    assert data.date == "12.05.2026"
    assert data.total == 11.90
    assert data.vat == 1.90
    assert data.currency == "EUR"

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


def test_parse_german_receipt_with_euro_symbol():
    text = """
    Test Bäckerei GmbH
    Kassenbon
    Belegdatum: 28.06.2026
    Summe 24,99 €
    MwSt 4,75 €
    """

    data = parse_receipt_text(text, "german_receipt.png")

    assert data.vendor == "Test Bäckerei GmbH"
    assert data.date == "28.06.2026"
    assert data.total == 24.99
    assert data.vat == 4.75
    assert data.currency == "EUR"


def test_parse_german_invoice_with_thousand_separator():
    text = """
    Musterfirma GmbH
    Rechnung
    Rechnungsdatum: 28.06.2026
    Nettobetrag 1.000,00 €
    Umsatzsteuer 190,00 €
    Gesamtbetrag 1.190,00 €
    """

    data = parse_receipt_text(text, "invoice.pdf")

    assert data.vendor == "Musterfirma GmbH"
    assert data.date == "28.06.2026"
    assert data.total == 1190.00
    assert data.vat == 190.00
    assert data.currency == "EUR"
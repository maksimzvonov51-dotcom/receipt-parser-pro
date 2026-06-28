from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class ReceiptData:
    file_name: str
    vendor: Optional[str] = None
    date: Optional[str] = None
    total: Optional[float] = None
    vat: Optional[float] = None
    currency: Optional[str] = None
    raw_text: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["raw_text"] = self.raw_text[:5000]
        return data


def file_name(path: str | Path) -> str:
    return Path(path).name

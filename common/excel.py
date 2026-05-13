import pandas as pd
from typing import Optional, List
from dataclasses import dataclass
from io import BytesIO


@dataclass
class ExcelExportOptions:
    sheet_name: str = "Sheet1"
    include_index: bool = False
    freeze_panes: Optional[str] = None
    column_widths: Optional[dict] = None


def export_to_excel(data: List[dict], options: ExcelExportOptions = None) -> BytesIO:
    if options is None:
        options = ExcelExportOptions()
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=options.sheet_name, index=options.include_index)
        if options.freeze_panes:
            writer.sheets[options.sheet_name].freeze_panes = options.freeze_panes
    output.seek(0)
    return output


def export_multiple_sheets(sheets: dict, options: ExcelExportOptions = None) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, data in sheets.items():
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    output.seek(0)
    return output

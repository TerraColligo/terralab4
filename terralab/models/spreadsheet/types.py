# -*- coding: utf-8 -*-
# Spreadsheet related Python typings
from typing import Any, Dict, List, Union
try:
    from typing import TypedDict # type: ignore
except:
    from typing_extensions import TypedDict

Spreadsheets = Any
SpreadsheetRow = List[Union[str, float, int]]
SpreadsheetRows = List[SpreadsheetRow]
SpreadsheetValueRange = Dict[str, SpreadsheetRows] # map 'values' => SpreadsheetRows
SpreadsheetValueRanges = List[SpreadsheetValueRange]
SpreadsheetColMapping = Dict[str, int]

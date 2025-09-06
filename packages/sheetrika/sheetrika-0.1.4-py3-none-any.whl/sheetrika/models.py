import csv
import yaml

from io import StringIO
from typing import Any, Generator, Callable, Dict, List, Literal, Optional, Tuple


class BaseYmData:
    """Base container for parsed Metrica data."""

    def __init__(self, raw: Any, schema: Optional[List[str]] = None):
        self.raw = raw
        self.schema = tuple(schema) if schema else ()
        self.row_count = 0

    @property
    def headers(self) -> List[str]:
        return ()

    @property
    def values(self) -> List[Tuple[Any, ...]]:
        return ()

    @property
    def is_empty(self) -> bool:
        return self.row_count == 0


class YmJsonData(BaseYmData):
    """Parsed Ym JSON data (stub)."""

    pass


class YmCsvData(BaseYmData):
    """Parses and filters Ym CSV data."""

    def __init__(
        self,
        raw: str,
        schema: Optional[List[str]] = None,
        filters: Optional[List[Callable[[Dict[str, str]], Optional[Dict[str, str]]]]] = None,
    ):
        super().__init__(raw, schema)
        self.filters = filters or []
        self.parsed: Dict[str, Tuple[str, ...]] = {}
        self._headers = None
        self._parse()

    def _parse(self):
        csv_content = self.raw.replace('\ufeff', '')  # Remove BOM
        rows = list(csv.reader(StringIO(csv_content)))
        if not rows:
            return

        headers, *data = rows
        filtered_rows = list(self._filter_rows(headers, data))

        if not filtered_rows:
            self.parsed = {col: () for col in headers}
            return

        for i, column in enumerate(zip(*filtered_rows)):
            self.parsed[headers[i]] = column

        self.row_count = len(filtered_rows)
        self._headers = tuple(headers)

    def _filter_rows(self, headers: List[str], rows: List[List[str]]) -> Generator[Tuple[str], None, None]:
        for row in rows:
            if len(row) < len(headers):
                continue
            mapped = dict(zip(headers, row))
            for f in self.filters:
                mapped = f(mapped)
                if not mapped:
                    break
            if mapped:
                yield tuple(mapped.values())

    @property
    def headers(self) -> Tuple[str]:
        return self.schema or self._headers

    @property
    def headers_raw(self) -> Tuple[str]:
        return self._headers

    @property
    def values(self) -> List[Tuple[str, ...]]:
        if not self.row_count:
            return []

        columns = [self.parsed.get(col, ('',) * self.row_count) for col in self.headers]
        return list(zip(*columns))

    @property
    def column_count(self) -> int:
        return len(self.parsed)

    @property
    def pk(self) -> str:
        return self.headers[0]

    @property
    def pk_values(self) -> str:
        return self.parsed[self.pk]


class YmQuery:
    def __init__(
        self,
        url: str,
        params: Dict[str, Any],
        schema: Optional[List[str]] = None,
        dtype: Optional[Literal['csv', 'json']] = None,
    ):
        self.url = url
        self.params = params
        self.schema = schema
        self.dtype = dtype if dtype else ('csv' if self.url.endswith('.csv') else 'json')


class GooSheetCell:
    def __init__(self, name):
        self.name: str = name
        self.column: str = self._letters(name)
        self.column_id = self._column_id(self.column)
        self.row: str = self._digits(name)
        self.row_id: int = self._row_id(self.row)

    @staticmethod
    def _digits(s: str) -> str:
        return ''.join(i for i in s if i.isdigit())

    @staticmethod
    def _letters(s: str) -> str:
        return ''.join(i for i in s if i.isalpha())

    @staticmethod
    def _column_id(s: str) -> int:
        if not s:
            return -1
        ans = 0
        for i, v in enumerate(s):
            ans += 26 * i + ord(v) - ord('A')
        return ans

    @staticmethod
    def _row_id(s: str) -> int:
        return int(s) - 1 if s else -1

    @property
    def pk_values_range(self) -> str:
        return f'{self.column}{self.row}:{self.column}' if self.column else ''

    def apply_r1c1(self, row_id: int, column_id: int):
        column = chr(ord('A') + column_id)
        self.__init__(f'{column}{row_id}')


class GooSheetRange:
    max_rows = 1_000_000

    def __init__(self, name):
        self.name = name
        cells = name.split(':', 1)
        self.left = GooSheetCell(cells[0])
        self.right = GooSheetCell(cells[1]) if len(cells) > 1 else GooSheetCell('')

    def __eq__(self, value):
        return self.name == value

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def tune(self, data: YmCsvData):
        self.right.apply_r1c1(
            row_id=self.max_rows,
            column_id=self.left.column_id + data.column_count - 1,
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            'startRowIndex': self.left.row_id,
            'endRowIndex': self.max_rows,
            'startColumnIndex': self.left.column_id,
            'endColumnIndex': self.right.column_id + 1,
        }


class GooSheet:
    def __init__(
        self,
        spreadsheet_id: str,
        name: str,
        range: str,
        wtype: Literal['snapshot', 'append', 'merge'] = 'snapshot',
    ):
        self.spreadsheet_id = spreadsheet_id
        self.name = name
        self.range = GooSheetRange(range)
        self.wtype = wtype

    @property
    def sheet_range(self) -> str:
        ans = self.name
        if self.range.name:
            ans += f'!{self.range.name}'
        return ans

    def copy(self, **kwargs) -> 'GooSheet':
        new_data = {
            'spreadsheet_id': self.spreadsheet_id,
            'name': self.name,
            'range': self.range,
            'wtype': self.wtype,
            **kwargs,
        }
        return GooSheet(**new_data)


class SheetrikaTaskConfig:
    def __init__(self, name: str, query: Dict[str, Any], sheet: Dict[str, Any]):
        self.name = name
        self.query = YmQuery(**query)
        self.sheet = GooSheet(**sheet)


class SheetrikaConfig:
    def __init__(self, tasks: List[Dict[str, Any]]):
        self.tasks = [SheetrikaTaskConfig(**task) for task in tasks]
        self._task_map = {task.name: task for task in self.tasks}

    def get_task(self, name: str) -> SheetrikaTaskConfig:
        return self._task_map.get(name)

    @staticmethod
    def from_yaml(path: str) -> 'SheetrikaConfig':
        with open(path, 'r') as file:
            data = yaml.safe_load(file)
        return SheetrikaConfig(**data)

import base64
import json
from typing import Any, Dict, List

from google.oauth2 import service_account
from googleapiclient.discovery import build

from sheetrika.errors import ClientInternalError
from sheetrika.models import GooSheet, YmCsvData


class GooSheetsClient:
    """Wrapper around G-Sheets API."""

    def __init__(self, token: str):
        self.token = token
        if not token:
            raise ValueError('Token cannot be empty.')
        self.service = self._init_service()
        self._sheet_meta = {}

    def _init_service(self):
        creds_info = json.loads(base64.b64decode(self.token))
        creds = service_account.Credentials.from_service_account_info(creds_info)
        return build('sheets', 'v4', credentials=creds).spreadsheets()

    def _call_api(self, method: str, sheet: GooSheet, **kwargs) -> Dict[str, Any]:
        if method == 'batch':
            func = self.service.batchUpdate(
                spreadsheetId=sheet.spreadsheet_id,
                **kwargs,
            )
        elif method == 'describe':
            func = self.service.get(
                spreadsheetId=sheet.spreadsheet_id,
                fields='sheets(properties(sheetId,title))',
            )
        else:
            func = getattr(self.service.values(), method)(
                spreadsheetId=sheet.spreadsheet_id,
                range=sheet.sheet_range,
                **kwargs,
            )
        return func.execute()

    def _describe(self, sheet: GooSheet) -> Dict[str, Any]:
        meta = self._call_api('describe', sheet)
        for s in meta['sheets']:
            self._sheet_meta[s['properties']['title']] = s['properties']['sheetId']

    def read(self, sheet: GooSheet) -> List[List[str]]:
        return self._call_api('get', sheet).get('values', [])

    def clear(self, sheet: GooSheet) -> Dict[str, Any]:
        return self._call_api('clear', sheet)

    def sort(self, sheet: GooSheet, asc=True) -> Dict[str, Any]:
        if not self._sheet_meta:
            self._describe(sheet)

        sort_order = {True: 'ASCENDING', False: 'DESCENDING'}[asc]

        request_body = {
            'requests': [
                {
                    'sortRange': {
                        'range': {
                            'sheetId': self._sheet_meta[sheet.name],
                            **sheet.range.to_json(),
                        },
                        'sortSpecs': [
                            {'dimensionIndex': 0, 'sortOrder': sort_order},
                        ],
                    }
                }
            ]
        }
        return self._call_api('batch', sheet, body=request_body)

    def _write(self, sheet: GooSheet, data: YmCsvData) -> Dict[str, Any]:
        return self._call_api('update', sheet, valueInputOption='USER_ENTERED', body={'values': data.values})

    def write(self, sheet: GooSheet, data: YmCsvData) -> Dict[str, Any]:
        if data.is_empty:
            return {}

        sheet.range.tune(data)

        writers = {
            'snapshot': self._write_snapshot,
            'append': self._write_append,
            'merge': self._write_merge,
        }

        if sheet.wtype not in writers:
            return {}
        return writers[sheet.wtype](sheet, data)

    def _write_snapshot(self, sheet: GooSheet, data: YmCsvData) -> Dict[str, Any]:
        clear_range = sheet.copy(range=f'{sheet.range.left.row}:{sheet.range.max_rows}')

        self.clear(clear_range)
        return self._write(sheet, data)

    def _write_append(self, sheet: GooSheet, data: YmCsvData) -> Dict[str, Any]:
        last_row = self._find_last_row(sheet)
        new_data_range = sheet.copy(range=f'{sheet.range.left.column}{last_row}')

        return self._write(new_data_range, data)

    def _write_merge(self, sheet: GooSheet, data: YmCsvData) -> Dict[str, Any]:
        self.sort(sheet)

        last_row = self._find_last_row(sheet, min(data.pk_values))
        clear_range = sheet.copy(range=f'{last_row}:{sheet.range.max_rows}')
        new_data_range = sheet.copy(range=f'{sheet.range.left.column}{last_row}')

        self.clear(clear_range)
        return self._write(new_data_range, data)

    def _find_last_row(self, sheet: GooSheet, min_value: str = None) -> int:
        pk_values = self._get_primary_key_values(sheet)
        if pk_values != sorted(pk_values):
            raise ClientInternalError(f'Data not sorted {sheet.name}, {pk_values=}')
        last_row = len(pk_values)
        if len(pk_values) > 1 and min_value:
            last_row = self._first_after_min(pk_values, min_value)
        return last_row + sheet.range.left.row_id + 1

    def _get_primary_key_values(self, sheet: GooSheet) -> List[Any]:
        values = self.read(sheet.copy(range=sheet.range.left.pk_values_range))
        return [i[0] for i in values]

    @staticmethod
    def _first_after_min(values: List[int], min_val: str) -> int:
        for i, v in enumerate(values):
            if v >= min_val:
                return i
        return len(values)

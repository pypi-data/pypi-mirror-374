import requests

from typing import Any, Callable, Dict, List, Optional, Union

from sheetrika.models import YmCsvData, YmJsonData, YmQuery


class YmClient:
    """Client to request Metrica reports."""

    def __init__(self, token: str):
        if not token:
            raise ValueError('Token cannot be empty.')
        self.token = token

    def fetch(self, url: str, params: Dict[str, Any]) -> requests.Response:
        response = requests.get(url, params=params, headers={'Authorization': self.token})
        response.raise_for_status()
        return response

    def get_data(
        self,
        query: 'YmQuery',
        filters: Optional[List[Callable[[Dict[str, str]], Optional[Dict[str, str]]]]] = None,
    ) -> Union[YmCsvData, YmJsonData]:
        response = self.fetch(query.url, query.params)
        if query.dtype == 'csv':
            return YmCsvData(response.text, query.schema, filters)
        return YmJsonData(response.json(), query.schema)

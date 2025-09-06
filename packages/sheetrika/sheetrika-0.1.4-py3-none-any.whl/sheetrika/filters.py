import re

from typing import Callable, Dict, Optional


class YmFilters:
    """Common filter utilities for Metrica data."""

    re_date: str = r'\d{4}(-\d{2}){2}'

    @staticmethod
    def regexp_like(column: str, pattern: str) -> Callable[[Dict[str, str]], Optional[Dict[str, str]]]:
        """Return rows where column matches regex."""
        regex = re.compile(pattern)

        def _filter(row: Dict[str, str]) -> Optional[Dict[str, str]]:
            val = row.get(column)
            return row if val and regex.match(val) else None

        return _filter

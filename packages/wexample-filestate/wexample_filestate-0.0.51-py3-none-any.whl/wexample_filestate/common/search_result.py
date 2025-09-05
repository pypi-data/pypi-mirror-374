from __future__ import annotations

from pydantic import Field
from wexample_filestate.item.item_target_file import ItemTargetFile
from wexample_helpers.classes.extended_base_model import ExtendedBaseModel


class SearchResult(ExtendedBaseModel):
    item: ItemTargetFile = Field(description="The target file that was searched.")
    searched: str = Field(description="The search string used to find matches.")
    line: int = Field(description="1-based line number where the match starts.")
    column: int = Field(description="1-based column number where the match starts.")

    @staticmethod
    def _compute_line_col(content: str, idx: int) -> tuple[int, int]:
        """Return 1-based (line, column) for a 0-based index in content."""
        line = content.count("\n", 0, idx) + 1
        last_nl = content.rfind("\n", 0, idx)
        column = (idx - last_nl) if last_nl != -1 else (idx + 1)
        return line, column

    @classmethod
    def create_one_if_match(
        cls,
        search: str,
        item: ItemTargetFile,
        *,
        regex: bool = False,
        flags: int = 0,
    ) -> SearchResult | None:
        """Return the first match as a SearchResult or None.

        Supports literal substring search by default. If ``regex=True``,
        interprets ``search`` as a regular expression and applies ``flags``
        (e.g., ``re.MULTILINE``). Line and column are 1-based.
        """
        if not search:
            return None

        content = item.read()
        if regex:
            import re

            m = re.search(search, content, flags)
            if not m:
                return None
            idx = m.start()
        else:
            idx = content.find(search)
            if idx == -1:
                return None

        line, column = cls._compute_line_col(content, idx)
        return cls(item=item, searched=search, line=line, column=column)

    @classmethod
    def create_for_all_matches(
        cls,
        search: str,
        item: ItemTargetFile,
        *,
        regex: bool = False,
        flags: int = 0,
    ) -> list[SearchResult]:
        """Return all matches as a list of SearchResult.

        By default performs literal, non-overlapping substring matches using
        ``str.find``. With ``regex=True``, uses ``re.finditer`` to collect all
        matches (including overlapping if your pattern allows via lookahead).
        Line and column are 1-based.
        """
        if not search:
            return []

        content = item.read_text()
        results: list[SearchResult] = []
        if regex:
            import re

            for m in re.finditer(search, content, flags):
                idx = m.start()
                line, column = cls._compute_line_col(content, idx)
                results.append(
                    cls(item=item, searched=search, line=line, column=column)
                )
            return results
        else:
            start = 0
            while True:
                idx = content.find(search, start)
                if idx == -1:
                    break
                line, column = cls._compute_line_col(content, idx)
                results.append(
                    cls(item=item, searched=search, line=line, column=column)
                )
                start = idx + len(search)
            return results

    # Backward-compatibility alias (deprecated)
    @classmethod
    def create_if_match(cls, search: str, item: ItemTargetFile) -> SearchResult | None:
        """Deprecated: use create_one_if_match. Kept for compatibility."""
        return cls.create_one_if_match(search, item)

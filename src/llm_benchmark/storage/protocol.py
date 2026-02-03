from typing import Any, Protocol

from llm_benchmark.benchmark.report import Report


class ResultStorage(Protocol):
    def save(self, report: Report, name: str) -> str:
        """
        Saves a report and returns its identifier.
        """
        ...

    def load(self, identifier: str) -> Report:
        """
        Loads a report by its identifier.
        """
        ...

    def list_reports(self) -> list[dict[str, Any]]:
        """
        Returns metadata for all stored reports.
        """
        ...

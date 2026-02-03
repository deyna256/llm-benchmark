import json
from datetime import datetime
from typing import Any

from llm_benchmark.benchmark.report import Report
from llm_benchmark.serialization.base import BaseSerializer


class JSONSerializer(BaseSerializer):
    def __init__(self, indent: int = 2):
        self.indent = indent

    def serialize(self, report: Report) -> str:
        data = {
            "metadata": report.metadata,
            "summary": report.get_summary(),
            "results": [self._serialize_result(r) for r in report.results],
        }
        return json.dumps(data, indent=self.indent, default=self._json_default)

    def get_file_extension(self) -> str:
        return "json"

    @staticmethod
    def _json_default(obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

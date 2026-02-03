
import yaml

from llm_benchmark.benchmark.report import Report
from llm_benchmark.serialization.base import BaseSerializer


class YAMLSerializer(BaseSerializer):
    def serialize(self, report: Report) -> str:
        data = {
            "metadata": report.metadata,
            "summary": report.get_summary(),
            "results": [self._serialize_result(r) for r in report.results],
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    def get_file_extension(self) -> str:
        return "yaml"

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from llm_benchmark.benchmark.report import Report
from llm_benchmark.core.metrics import Metrics
from llm_benchmark.core.result import TestResult
from llm_benchmark.core.test_case import TestCase
from llm_benchmark.validation.validators import CustomValidator


class FileStorage:
    def __init__(self, base_dir: str = "results"):
        self.base_dir = Path(base_dir)
        self.reports_dir = self.base_dir / "reports"
        self.metadata_file = self.base_dir / "metadata.json"

        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save(self, report: Report, name: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        identifier = f"{timestamp}_{name}"
        filename = f"{identifier}.json"
        filepath = self.reports_dir / filename

        data = self._serialize_report(report)

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, dir=self.reports_dir, suffix=".tmp"
        ) as tmp:
            json.dump(data, tmp, indent=2)
            tmp_path = Path(tmp.name)

        tmp_path.replace(filepath)

        self._update_metadata(identifier, name, str(filepath))

        return identifier

    def load(self, identifier: str) -> Report:
        filepath = self.reports_dir / f"{identifier}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"Report not found: {identifier}")

        with open(filepath) as f:
            data = json.load(f)

        return self._deserialize_report(data)

    def list_reports(self) -> list[dict[str, Any]]:
        if not self.metadata_file.exists():
            return []

        with open(self.metadata_file) as f:
            return json.load(f)

    def _update_metadata(self, identifier: str, name: str, path: str) -> None:
        metadata = self.list_reports()

        metadata.append(
            {
                "id": identifier,
                "name": name,
                "path": path,
                "timestamp": datetime.now().isoformat(),
            }
        )

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, dir=self.base_dir, suffix=".tmp"
        ) as tmp:
            json.dump(metadata, tmp, indent=2)
            tmp_path = Path(tmp.name)

        tmp_path.replace(self.metadata_file)

    @staticmethod
    def _serialize_report(report: Report) -> dict[str, Any]:
        return {
            "metadata": report.metadata,
            "results": [
                {
                    "test_case": {
                        "name": r.test_case.name,
                        "prompt": r.test_case.prompt,
                        "model": r.test_case.model,
                        "tags": list(r.test_case.tags),
                        "system_prompt": r.test_case.system_prompt,
                        "temperature": r.test_case.temperature,
                        "max_tokens": r.test_case.max_tokens,
                        "metadata": r.test_case.metadata,
                        "validator_description": r.test_case.validator.describe(),
                    },
                    "response": r.response,
                    "passed": r.passed,
                    "metrics": {
                        "latency_ms": r.metrics.latency_ms,
                        "prompt_tokens": r.metrics.prompt_tokens,
                        "completion_tokens": r.metrics.completion_tokens,
                        "total_tokens": r.metrics.total_tokens,
                        "cost_usd": r.metrics.cost_usd,
                        "retry_delays": list(r.metrics.retry_delays),
                    }
                    if r.metrics
                    else None,
                    "validation_details": r.validation_details,
                    "execution_error": r.execution_error,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in report.results
            ],
        }

    @staticmethod
    def _deserialize_report(data: dict[str, Any]) -> Report:
        def placeholder_validator(_: str) -> bool:
            return True

        results = []
        for r in data["results"]:
            test_case = TestCase(
                name=r["test_case"]["name"],
                prompt=r["test_case"]["prompt"],
                model=r["test_case"]["model"],
                validator=CustomValidator(
                    func=placeholder_validator,
                    description=r["test_case"]["validator_description"],
                ),
                tags=tuple(r["test_case"]["tags"]),
                system_prompt=r["test_case"]["system_prompt"],
                temperature=r["test_case"]["temperature"],
                max_tokens=r["test_case"]["max_tokens"],
                metadata=r["test_case"]["metadata"],
            )

            metrics = None
            if r["metrics"]:
                metrics = Metrics(
                    latency_ms=r["metrics"]["latency_ms"],
                    prompt_tokens=r["metrics"]["prompt_tokens"],
                    completion_tokens=r["metrics"]["completion_tokens"],
                    total_tokens=r["metrics"]["total_tokens"],
                    cost_usd=r["metrics"]["cost_usd"],
                    retry_delays=tuple(r["metrics"]["retry_delays"]),
                )

            result = TestResult(
                test_case=test_case,
                response=r["response"],
                passed=r["passed"],
                metrics=metrics,
                validation_details=r["validation_details"],
                execution_error=r["execution_error"],
                timestamp=datetime.fromisoformat(r["timestamp"]),
            )
            results.append(result)

        return Report(results=results, metadata=data["metadata"])

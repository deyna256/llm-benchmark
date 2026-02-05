from collections.abc import Callable, Sequence
from dataclasses import dataclass

from promptum.benchmark.result import TestResult
from promptum.benchmark.summary import Summary


@dataclass(frozen=True, slots=True)
class Report:
    results: Sequence[TestResult]

    def get_summary(self) -> Summary:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)

        latencies = [r.metrics.latency_ms for r in self.results if r.metrics]
        total_cost = sum(r.metrics.cost_usd or 0 for r in self.results if r.metrics)
        total_tokens = sum(r.metrics.total_tokens or 0 for r in self.results if r.metrics)

        return Summary(
            total=total,
            passed=passed,
            failed=total - passed,
            pass_rate=passed / total if total > 0 else 0,
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
            min_latency_ms=min(latencies) if latencies else 0,
            max_latency_ms=max(latencies) if latencies else 0,
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
        )

    def filter(
        self,
        model: str | None = None,
        tags: Sequence[str] | None = None,
        passed: bool | None = None,
    ) -> "Report":
        filtered = list(self.results)

        if model:
            filtered = [r for r in filtered if r.test_case.model == model]

        if tags:
            tag_set = set(tags)
            filtered = [r for r in filtered if tag_set.intersection(r.test_case.tags)]

        if passed is not None:
            filtered = [r for r in filtered if r.passed == passed]

        return Report(results=filtered)

    def group_by(self, key: Callable[[TestResult], str]) -> dict[str, "Report"]:
        groups: dict[str, list[TestResult]] = {}

        for result in self.results:
            group_key = key(result)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(result)

        return {k: Report(results=v) for k, v in groups.items()}

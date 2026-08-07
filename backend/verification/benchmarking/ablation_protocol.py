"""
Controlled 3-Matrix Ablation Execution Engine (FR47).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
from pydantic import BaseModel, Field

from backend.verification.benchmarking.bench_runner import BenchmarkRunner, BatchEvalSummary


class AblationVariantResult(BaseModel):
    """Evaluation result for a specific variant in an ablation matrix study."""
    matrix_name: str = Field(..., description="Ablation matrix name")
    variant_id: str = Field(..., description="Variant identifier (e.g. baseline, submitted, memory_on, memory_off)")
    resolved_count: int = Field(0, description="Resolved benchmark task count")
    total_tasks: int = Field(0, description="Total benchmark task count")
    pass_rate: float = Field(0.0, description="Task pass rate ratio (0.0 to 1.0)")
    avg_token_cost_usd: float = Field(0.0, description="Average token USD cost per task")
    avg_duration_ms: float = Field(0.0, description="Average task duration in milliseconds")


class AblationMatrixReport(BaseModel):
    """Summary report for a single ablation matrix study (FR47)."""
    matrix_name: str = Field(..., description="Matrix title (e.g. Baseline vs. Submitted Harness)")
    variants: Dict[str, AblationVariantResult] = Field(default_factory=dict, description="Results keyed by variant ID")
    winner_variant: str = Field("", description="Variant ID with highest pass rate")
    delta_pass_rate: float = Field(0.0, description="Pass rate improvement delta (percentage points)")
    markdown_summary: str = Field("", description="Formatted Markdown matrix report table")


class AblationProtocolEngine:
    """
    Controlled 3-Matrix Ablation Execution Engine (FR47):
    Matrix 1: Baseline Harness vs. Submitted Harness (same model & budget)
    Matrix 2: Tiered Memory ON vs. Tiered Memory OFF
    Matrix 3: Single Agent vs. Multi-Agent Task Graph
    """

    MATRIX_DEFINITIONS = {
        "baseline_vs_submitted": {
            "title": "Matrix 1: Baseline Harness vs. Submitted Harness",
            "variants": ["baseline", "submitted"],
        },
        "tiered_memory_toggle": {
            "title": "Matrix 2: Tiered Memory ON vs. Tiered Memory OFF",
            "variants": ["memory_on", "memory_off"],
        },
        "topology_comparison": {
            "title": "Matrix 3: Single Agent vs. Multi-Agent Task Graph",
            "variants": ["single_agent", "multi_agent"],
        },
    }

    def __init__(self, benchmark_runner: Optional[BenchmarkRunner] = None):
        self.benchmark_runner = benchmark_runner or BenchmarkRunner()

    def run_ablation_matrix(
        self,
        matrix_name: str,
        issue_ids: List[str],
        harness_callback: Optional[Callable[[str, str, str], Tuple[bool, str, float]]] = None,
    ) -> AblationMatrixReport:
        """
        Executes an ablation matrix across all specified task issue IDs.
        `harness_callback` receives (workspace_path, problem_statement, variant_id) and returns (success, patch_diff, cost_usd).
        """
        if matrix_name not in self.MATRIX_DEFINITIONS:
            raise KeyError(f"Unknown ablation matrix '{matrix_name}'. Available: {list(self.MATRIX_DEFINITIONS.keys())}")

        def_info = self.MATRIX_DEFINITIONS[matrix_name]
        variant_ids = def_info["variants"]
        variant_results: Dict[str, AblationVariantResult] = {}

        for var_id in variant_ids:
            def var_harness_adapter(ws_path: str, prob_stmt: str):
                if harness_callback:
                    return harness_callback(ws_path, prob_stmt, var_id)
                # Default simulation fallback for testing ablation engine
                # Submitted, memory_on, multi_agent get slightly higher simulated accuracy
                is_improved = var_id in ("submitted", "memory_on", "multi_agent")
                cost = 0.008 if is_improved else 0.005
                return True, "--- default patch ---", cost

            batch_summary: BatchEvalSummary = self.benchmark_runner.run_batch(
                issue_ids=issue_ids,
                harness_func=var_harness_adapter,
            )

            variant_results[var_id] = AblationVariantResult(
                matrix_name=matrix_name,
                variant_id=var_id,
                resolved_count=batch_summary.resolved_tasks,
                total_tasks=batch_summary.total_tasks,
                pass_rate=batch_summary.pass_rate,
                avg_token_cost_usd=batch_summary.total_cost_usd / max(1, batch_summary.total_tasks),
                avg_duration_ms=batch_summary.avg_duration_ms,
            )

        # Winner & delta calculations
        sorted_vars = sorted(variant_results.values(), key=lambda v: v.pass_rate, reverse=True)
        winner = sorted_vars[0].variant_id if sorted_vars else ""
        delta = (sorted_vars[0].pass_rate - sorted_vars[-1].pass_rate) if len(sorted_vars) > 1 else 0.0

        # Build markdown summary table
        lines = [
            f"### {def_info['title']}",
            "| Variant | Resolved | Total | Pass Rate | Avg Cost (USD) | Avg Time (ms) |",
            "|---|---|---|---|---|---|",
        ]
        for var_res in variant_results.values():
            lines.append(
                f"| `{var_res.variant_id}` | {var_res.resolved_count} | {var_res.total_tasks} | "
                f"`{var_res.pass_rate * 100:.1f}%` | `${var_res.avg_token_cost_usd:.4f}` | `{var_res.avg_duration_ms:.1f}ms` |"
            )
        lines.append(f"\n**Winner:** `{winner}` (Delta: `+{delta * 100:.1f}%`)")
        md_table = "\n".join(lines)

        return AblationMatrixReport(
            matrix_name=def_info["title"],
            variants=variant_results,
            winner_variant=winner,
            delta_pass_rate=delta,
            markdown_summary=md_table,
        )

    def run_full_ablation_study(
        self,
        issue_ids: List[str],
        harness_callback: Optional[Callable[[str, str, str], Tuple[bool, str, float]]] = None,
    ) -> Dict[str, AblationMatrixReport]:
        """
        Runs all 3 ablation matrices sequentially and returns study reports dictionary.
        """
        full_study: Dict[str, AblationMatrixReport] = {}
        for m_name in self.MATRIX_DEFINITIONS:
            full_study[m_name] = self.run_ablation_matrix(m_name, issue_ids, harness_callback)
        return full_study

    def generate_ablation_report_markdown(self, full_study: Dict[str, AblationMatrixReport]) -> str:
        """
        Generates standardized Ablation & Performance Report markdown artifact content.
        """
        sections = [
            "# Standardized Ablation & Performance Report (FR47)",
            "Controlled 3-Matrix Evaluation Protocol across SWE-bench & Terminal-Bench Datasets",
            "",
        ]
        for m_report in full_study.values():
            sections.append(m_report.markdown_summary)
            sections.append("\n---\n")

        return "\n".join(sections)

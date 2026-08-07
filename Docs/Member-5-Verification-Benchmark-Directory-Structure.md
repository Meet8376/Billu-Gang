# Member 5 — Verification, Benchmarking & Evaluation Lead: Directory Structure & File Specification

## 1. Overview & Ownership Domain
- **Member:** Member 5
- **Primary Role:** Verification, Benchmarking & Evaluation Lead
- **Engineering Surfaces Owned:** Verification Pipeline, Benchmark Runner, Trace & Reviewer View Backend
- **Tech Stack & Tools:** Pytest, OpenTelemetry (Python SDK), Terminal-Bench, SWE-bench runner scripts, ESLint, Mypy, Ruff, `junitparser`
- **Primary Root Location:** `backend/verification/`

---

## 2. Dedicated Directory Tree

```
backend/verification/
├── __init__.py                         # Package initializer
│
├── pipeline/                           # Verification Pipeline & Quality Check Engine
│   ├── __init__.py
│   ├── runner.py                       # VerificationPipeline engine (build, lint, typecheck, test runner)
│   ├── test_parsers.py                 # Pytest XML/JSON & npm test output result parser
│   ├── static_analyzer.py              # Ruff, ESLint & Mypy static analysis integration wrapper
│   └── reviewer_engine.py              # Reviewer summary generator (completeness proof, uncertainties & rollback path)
│
├── trace/                              # Structured Event Tracing & OpenTelemetry Logger
│   ├── __init__.py
│   ├── trace_logger.py                 # Async JSONL event tracer (logs plan revisions, tool calls, test outputs)
│   └── opentelemetry_config.py         # OpenTelemetry trace collector setup & span context exporter
│
├── benchmarking/                       # Benchmark Runner & Ablation Protocol Engine
│   ├── __init__.py
│   ├── bench_runner.py                 # Terminal-Bench & SWE-bench evaluation runner scripts
│   ├── issue_loader.py                 # Benchmark problem loader & container workspace feeder
│   ├── ablation_protocol.py            # Controlled 3-matrix ablation execution engine (FR47)
│   └── evaluator_grader.py            # Hidden test injection & patch correctness grader (FR31)
│
└── tests/                              # Unit & Integration Tests for Verification & Evaluation
    ├── __init__.py
    ├── test_verification_runner.py     # Verification pipeline test suite execution unit tests
    ├── test_test_parsers.py            # Pytest and JUnit XML output parsing tests
    ├── test_trace_logger.py           # JSONL trace schema compliance & append tests
    ├── test_reviewer_engine.py         # Reviewer summary artifact generation tests
    └── test_ablation_protocol.py      # Benchmark ablation protocol matrix execution tests
```

---

## 3. Detailed File Responsibilities & Key Exports

| File Path | Purpose & Responsibilities | Key Functions / Classes / Components |
|---|---|---|
| `backend/verification/pipeline/runner.py` | Runs builds, linter, type-checkers, and unit tests inside sandbox as sole proof of done. | `class VerificationPipeline`, `run_suite()` |
| `backend/verification/pipeline/test_parsers.py` | Parses pytest XML/JSON output and npm test stdout into typed `VerificationRun` records. | `parse_pytest_xml()`, `parse_npm_test()` |
| `backend/verification/pipeline/static_analyzer.py` | Invokes Ruff, ESLint, and Mypy inside sandbox to ensure code quality before marking done. | `run_static_analysis()` |
| `backend/verification/pipeline/reviewer_engine.py` | Builds structured Reviewer Summary: proof of completion, remaining uncertainty, and cost info. | `class ReviewerEngine`, `generate_summary()` |
| `backend/verification/trace/trace_logger.py` | Appends event records to `trace.jsonl` (plans, tool calls, test outputs, token costs). | `class TraceLogger`, `log_event()` |
| `backend/verification/trace/opentelemetry_config.py` | Configures OpenTelemetry SDK for structured distributed tracing across harness components. | `setup_opentelemetry()`, `get_tracer()` |
| `backend/verification/benchmarking/bench_runner.py` | Drives batch evaluation across Terminal-Bench and SWE-bench benchmark task sets. | `class BenchmarkRunner`, `run_batch()` |
| `backend/verification/benchmarking/issue_loader.py` | Loads dataset tasks, injects problem statements into harness, and sets up test target repo. | `load_benchmark_issue(issue_id)` |
| `backend/verification/benchmarking/ablation_protocol.py` | Controls ablation study execution matrix: baseline vs submitted, memory on/off, single vs multi-agent. | `class AblationProtocolEngine` |
| `backend/verification/benchmarking/evaluator_grader.py` | Runs hidden test suite after harness completes patch to compute ground-truth pass rate. | `grade_submission(patch, hidden_tests)` |

---

## 4. 24-Hour Phase Deliverables Schedule

```
Phase 1 (H0-H3) ──► Phase 2 (H3-H8) ──► Phase 3 (H8-H13) ──► Phase 4 (H13-H17) ──► Phase 5 (H17-H21) ──► Phase 6 (H21-H24)
  Pytest Infrastructure Verification Pipeline  Integrate Pipeline    Injected Failure      Execute Benchmark     Walkthrough & Pitch
  & JSONL Trace Schema  & TraceLogger           & Reviewer Summary    Self-Healing Demo     Ablations (FR47)      Artifacts (`walkthrough.md`)
```

1. **Phase 1 (Hours 0–3):**
   - Set up test suite for the harness project using `pytest` (`tests/`).
   - Design standard JSONL trace schema (`trace.jsonl`) for event logging (`trace/trace_logger.py`).
   - Prepare test target repositories (1 sample bug repo + 1 benchmark test issue).
2. **Phase 2 (Hours 3–8):**
   - Build `VerificationPipeline` service to trigger build, lint (Ruff/ESLint), type check (Mypy), and test runner inside sandbox.
   - Implement parser for standard test outputs (pytest XML/JSON format, npm test output) (`pipeline/test_parsers.py`).
   - Build `TraceLogger` to capture all system events asynchronously (`trace/trace_logger.py`).
3. **Phase 3 (Hours 8–13):**
   - Integrate Verification Pipeline into Orchestrator: automatically run verification suite after code modifications.
   - Build basic SWE-bench / Terminal-Bench problem loader to feed sample issue into harness (`benchmarking/issue_loader.py`).
   - Create Reviewer Summary backend engine aggregating completeness proof, uncertainties, and rollback path (`pipeline/reviewer_engine.py`).
4. **Phase 4 (Hours 13–17):**
   - Implement injected failure recovery test case for live demo (FR40).
   - Build regression test runner comparing current repo state against initial git snapshot.
   - Build evaluator grader for hidden test injection (FR31).
5. **Phase 5 (Hours 17–21):**
   - Execute Terminal-Bench and SWE-bench test sets (`benchmarking/bench_runner.py`).
   - Run controlled **ablation protocol** (FR47):
     1. Baseline Harness vs. Submitted Harness (same model & budget).
     2. Tiered Memory ON vs. Tiered Memory OFF.
     3. Single Agent vs. Multi-Agent Task Graph.
   - Generate standardized **Ablation & Performance Report** artifact.
6. **Phase 6 (Hours 21–24):**
   - Finalize final demonstration script and pitch evidence output.
   - Populate `walkthrough.md` with benchmark proof, screenshots, and ablation data.

---

## 5. Subsystem Dependencies & API Boundaries
- **Verification ↔ Sandbox:** Executes test/build commands inside Docker container via `container_exec.py`.
- **Verification ↔ Orchestrator:** Returns pass/fail `VerificationRun` results to state graph to confirm completion or trigger replanning.
- **Verification ↔ CLI:** Provides structured `ReviewerSummary` to CLI backend route for display in `<ReviewerSummaryView />`.

# Product Requirements Document
## Unified Agentic Coding Harness (AE-01)

**Document owner:** [Team Name]
**Status:** Draft v1.0
**Last updated:** August 7, 2026

---

## 1. Summary

Modern coding agents (Claude Code, OpenCode, Amp, Droid, Codex CLI, Pi) increasingly compete on model quality alone, obscuring how much of an agent's real-world performance comes from the *harness* around the model — its context construction, memory, orchestration, tooling, and verification layers. This makes it hard for teams to know whether upgrading a model or upgrading their harness will move the needle on engineering outcomes.

This product is a **model-independent, terminal-based coding harness** that takes a high-level software engineering request (a bug report, feature request, or issue) and autonomously carries it through repository understanding, planning, code changes, testing, and verified patch delivery — while producing hard evidence (traces, test results, cost/latency data, ablations) that isolates how much of the performance gain comes from the harness itself versus the underlying model.

The system is built around seven engineering surfaces treated as first-class citizens: a **model adapter layer**, **repository intelligence**, **tiered memory**, a **context manager**, a **task graph/planner**, **sandboxed execution**, and **verification-first completion** — all wrapped in an **observability layer** that makes the agent's behavior auditable without exposing raw hidden reasoning.

---

## 2. Objectives

| # | Objective | Description |
|---|---|---|
| O1 | **Prove harness value, not just model output** | Demonstrate, via controlled ablation studies, that the harness meaningfully improves task success rate and cost-efficiency versus a baseline harness using the *same* underlying model and budget. |
| O2 | **Model independence** | Support swapping the underlying LLM (e.g., different Claude models, or other providers) without changing harness logic, via a clean adapter interface. |
| O3 | **End-to-end autonomous SE loop** | Take a repository + issue as input and produce a tested, reviewable, rollback-ready patch without manual intervention for well-scoped tasks. |
| O4 | **Verification over confidence** | Never mark a task "done" based on model self-assessment; completion must be backed by build/test/lint/static-analysis evidence. |
| O5 | **Safety-bounded autonomy** | Operate strictly within sandboxed, permissioned environments — no unrestricted host access, secrets, or production authority. |
| O6 | **Auditability** | Give a human reviewer a clear account of what the agent did, what it's uncertain about, and how to undo it. |
| O7 | **Benchmark-credible performance** | Achieve competitive, reproducible results on Terminal-Bench and SWE-bench-style tasks, including on unseen repositories and hidden test suites. |

---

## 3. Success Metrics

### Primary (harness-attribution) metrics
- **Δ Pass rate (harness vs. baseline, same model/budget):** % improvement in task success rate attributable to the harness alone.
- **Cost per successful task:** total tokens + tool-call cost ÷ number of verified-complete tasks, compared against baseline.
- **Hidden-test pass rate:** performance on organizer-provided/held-out issues not seen during development (guards against overfitting/benchmark gaming).

### Secondary (system health) metrics
- **Recovery rate:** % of injected/encountered failures the agent self-diagnoses and resolves without human intervention.
- **Stale-context rate:** % of agent actions taken on outdated context (pre-refresh after code changes).
- **Tool-call failure rate:** % of tool invocations that error out or require retries.
- **Human intervention rate:** average number of manual interventions required per completed task.
- **Time-to-first-verified-patch:** wall-clock time from issue intake to a passing verification suite.
- **Safety-policy violation count:** instances of the agent attempting out-of-scope filesystem, network, or credential access (target: 0).

### Demo/qualitative metrics
- Successful reproduction of an issue + generation of an evidence item before any code change.
- Successful run on at least one **unseen repository** with a rollback-ready patch.
- Reviewer view correctly explains completeness, uncertainty, and rollback path for 100% of demo runs.

---

## 4. Target Audience

| Segment | Description |
|---|---|
| **Primary: Software engineering teams** | Developers and eng teams maintaining large, polyglot, real-world repositories who want AI assistance that goes beyond autocomplete/single-file edits into full issue-to-patch workflows. |
| **Secondary: Platform/DevTools teams** | Teams evaluating or building internal AI coding infrastructure who need to know how much of an agent's performance is "harness" vs. "model," so they can make build/buy and model-selection decisions. |
| **Tertiary: Researchers/benchmark evaluators** | Groups (e.g., hackathon judges, ML researchers) who need reproducible ablations and hidden-task evaluation to assess agent architectures fairly. |
| **Tertiary: Security/compliance reviewers** | Stakeholders who need to trust that an autonomous coding agent operates within a bounded, auditable, revocable sandbox. |

---

## 5. User Needs

### Developer / engineering team needs
- "I want to hand off a well-scoped bug or feature and get back a **tested** patch, not just a diff I have to trust blindly."
- "I need to see **why** the agent believes the task is done, and what it's still unsure about."
- "I need an easy **rollback** if the patch is wrong."
- "I don't want the agent to touch my secrets, network, or unrelated parts of the repo."
- "I want it to work across my actual polyglot, messy, real-world codebase — not just toy repos."

### Platform/DevTools team needs
- "I need to know if switching models actually helps, or if my harness is the bottleneck (or vice versa)."
- "I need cost and latency numbers I can put in a budget conversation."
- "I need the system to plug into different models without a rewrite."

### Researcher/evaluator needs
- "I need ablation studies (memory on/off, single vs multi-agent, warm vs cold memory) that isolate variables cleanly."
- "I need hidden tasks the system couldn't have gamed."
- "I need reproducible benchmark runs (Terminal-Bench/SWE-bench-style)."

### Security/compliance needs
- "I need guarantees the agent can't exfiltrate secrets or reach production."
- "I need an emergency-stop mechanism and full traceability of every command executed."

---

## 6. Functional Requirements

### 6.1 Model Adapter Layer
- FR1: Provide a standard interface (prompting, tool-calling schema, streaming) decoupling model calls from all other subsystems.
- FR2: Support swapping models with zero changes to context construction, memory, planning, or verification code.
- FR3: Log per-call model identity, token usage, and latency for cost attribution.

### 6.2 Repository Intelligence
- FR4: Generate a file map, AST/symbol index, and import/call graph on repository intake.
- FR5: Build a test-to-source mapping to identify which tests cover which code paths.
- FR6: Parse configuration files and their relationships to source (build configs, CI, env files).
- FR7: Ingest git history to inform blame-aware and convention-aware suggestions.
- FR8: Refresh relevant indices automatically after code changes (avoid stale context).

### 6.3 Tiered Memory
- FR9: Support distinct memory tiers: working state, task state, project conventions, episodic outcomes, reusable procedures, user preferences, verified evidence.
- FR10: Attach provenance (source, timestamp, confidence) to every memory item.
- FR11: Support invalidation rules (e.g., auto-expire memory tied to now-changed code).
- FR12: Provide inspect/edit/export/delete controls for all memory tiers (user-facing).

### 6.4 Context Manager
- FR13: Dynamically budget tokens per task based on complexity and remaining context window.
- FR14: Score and rank retrieved context by relevance to the current subtask.
- FR15: Produce hierarchical summaries for large files/modules exceeding budget.
- FR16: Detect and flag stale context (e.g., referencing pre-edit file state).
- FR17: Apply prompt-injection resistance to any content retrieved from the repository, issue trackers, or tool outputs.

### 6.5 Task Graph / Planning
- FR18: Decompose an issue into a task graph with sequential and parallel branches.
- FR19: Support bounded specialist sub-agents (e.g., "test-writer," "reviewer") with scoped permissions.
- FR20: Insert independent review checkpoints between major task-graph stages.
- FR21: Support early termination when a branch is no longer viable.
- FR22: Support dynamic replanning when new information invalidates the current plan.

### 6.6 Sandboxed Execution
- FR23: Execute all commands in a scoped filesystem/network sandbox.
- FR24: Enforce resource limits (CPU, memory, time) per command.
- FR25: Isolate secrets from the execution environment by default.
- FR26: Support filesystem snapshots for rollback.
- FR27: Require approval gates for actions outside a pre-approved policy (e.g., network calls, destructive commands).
- FR28: Provide an emergency termination mechanism accessible at any point in execution.

### 6.7 Verification-First Completion
- FR29: Run declared build, test, lint, type-check, and static-analysis suites before marking any task complete.
- FR30: Run regression tests against previously passing behavior.
- FR31: Support hidden evaluator tasks injected by an external grader without the agent's foreknowledge.
- FR32: Require verification evidence — not model self-assessment — as the sole basis for "done" status.

### 6.8 Observability & Reviewer View
- FR33: Log plan revisions, retrieved context, tool calls, files touched, tests run, failures, and recovery actions.
- FR34: Track and display token/cost usage per task and per subtask.
- FR35: Generate a reviewer-facing summary: why the patch is believed complete, what remains uncertain, and how to roll it back.
- FR36: Never expose raw hidden chain-of-thought; surface only structured, human-readable rationale.

### 6.9 Minimum Viable Demonstration Flow
- FR37: On repository intake, produce an initial map and prompt for a bounded issue/feature request.
- FR38: Reproduce the reported issue and record it as a structured evidence item before making changes.
- FR39: Produce an explicit task graph visible to the user.
- FR40: Execute the coding run, apply the declared verification suite, and recover from at least one injected failure during the demo.
- FR41: Run a comparison: same model, baseline harness vs. submitted harness, same budget — and report the delta.
- FR42: Present the reviewer view (completeness, uncertainty, rollback instructions) at the end of every run.

### 6.10 Evaluation & Benchmarking
- FR43: Integrate Terminal-Bench as the primary benchmark suite.
- FR44: Integrate SWE-bench Verified/Lite, LiveCodeBench, and repository-understanding tasks as complementary suites.
- FR45: Support organizer-provided hidden issues as held-out evaluation.
- FR46: Produce a standard report: pass rate, hidden-test pass rate, cost/task, tokens, tool-call failure rate, recovery rate, stale-context rate, human interventions, safety violations.
- FR47: Support configurable ablation runs: memory on/off, structural retrieval on/off, single-agent/multi-agent, cold/warm memory, baseline/submitted harness.

---

## 7. Non-Functional Requirements

### 7.1 Performance
- NFR1: Time-to-first-verified-patch should scale sub-linearly with repository size for well-scoped issues.
- NFR2: Context retrieval and relevance scoring should not dominate end-to-end task latency (target: <20% of total wall-clock time).

### 7.2 Scalability
- NFR3: Support large monorepositories with sparse documentation and polyglot services without requiring architecture changes.
- NFR4: Support tasks requiring more than one hour of continuous agent work without losing coherent task/working state.

### 7.3 Reliability
- NFR5: Gracefully handle flaky tests (e.g., retry-with-quarantine logic) without falsely blaming the agent's patch.
- NFR6: Recover from at least one class of injected failure per run without human intervention (per MVD requirement).

### 7.4 Security & Safety
- NFR7: The harness must never receive or request unrestricted host credentials, private files outside the target repo, SSH keys, browser sessions, or production deployment authority.
- NFR8: All sandbox escapes, policy violations, or approval-gate bypass attempts must be logged and blocked by default.
- NFR9: No mechanism may allow benchmark gaming via leaked test access or hidden-task inspection.

### 7.5 Portability / Model Independence
- NFR10: Swapping the underlying model must require configuration changes only — no changes to context, memory, planning, or verification code paths.
- NFR11: Support restricted-network operation without functional collapse (degrade gracefully, not silently).

### 7.6 Auditability & Transparency
- NFR12: Every completed task must produce a reproducible trace sufficient for a third party to understand what happened and why, without needing access to raw model reasoning.
- NFR13: All memory items must be inspectable, exportable, and deletable by the user at any time.

### 7.7 Usability
- NFR14: The CLI/terminal UI should surface task-graph state, current action, and evidence status without requiring the user to parse raw logs.
- NFR15: The reviewer view should be understandable by a developer unfamiliar with the specific run within a few minutes.

### 7.8 Maintainability
- NFR16: Each of the eight engineering surfaces (adapter, repo intelligence, memory, context, task graph, sandbox, verification, observability) should be independently testable and replaceable.
- NFR17: Ablation configuration should not require code changes — only configuration/flag changes.

---

## 8. Out of Scope (v1)
- Full autonomous production deployment.
- Multi-repository cross-service refactors spanning separate git remotes.
- Long-running (multi-day) autonomous sessions without checkpoint review.
- Non-terminal (GUI-first) interfaces beyond a minimal trace viewer.

---

## 9. Key Risks
| Risk | Mitigation |
|---|---|
| Harness improvements are hard to isolate from model improvements | Strict ablation protocol (O1) with same-model, same-budget comparisons as a required deliverable |
| Overfitting to visible benchmark tasks | Hidden evaluator tasks (FR31, FR45) not accessible during development |
| Sandbox escape or credential leakage | Hard safety boundary (NFR7–NFR9), approval gates, emergency termination |
| Context staleness causing incorrect patches | Explicit stale-context detection and auto-refresh (FR16, FR8) |
| Verification suite gives false confidence (weak tests) | Regression testing + hidden tasks as cross-check (FR30–FR31) |

---

## 10. Deliverables Checklist (per problem statement)
- [ ] Working CLI/terminal UI + model/tool adapter SDK
- [ ] Context and memory engine with inspect/edit/export/delete controls
- [ ] Sandboxed execution service, trace viewer, reproducible benchmark runner
- [ ] Architecture, threat-model, ablation, failure-analysis, and cost report
- [ ] Demonstration on an unseen repository with a rollback-ready patch

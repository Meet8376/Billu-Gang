# temp script - can be deleted

Run Execution Control Route Handlers
Autonomous AI Code Repair + Docker Verification Pipeline.
Member 2 -- Backend Core & Model Adapter Lead
"""

import os
import ast
import re
import uuid
import time
import logging
import asyncio
from typing import Optional, List, Tuple, Any, Set

from fastapi import APIRouter, status
from pydantic import BaseModel

from backend.core.adapters.gemini_adapter import GeminiAdapter
from backend.core.schemas.sse_events import SSEEvent, EventType
from backend.core.routes.sse_routes import broadcaster
from backend.verification.pipeline.runner import VerificationRunner, VerificationRun
from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig

router = APIRouter()
logger = logging.getLogger(__name__)

# Constants

SKIP_DIRS: Set[str] = {
    ".git", "node_modules", "venv", "__pycache__", "dist",
    ".ruff_cache", ".pytest_cache", ".mypy_cache", ".eggs", "build",
    ".tox", ".hg", ".svn",
}

SUPPORTED_EXTS: Tuple[str, ...] = (
    ".py", ".java", ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".go", ".rs", ".cs", ".kt", ".kts", ".swift",
    ".rb", ".php", ".sh", ".bash", ".zsh", ".sql",
    ".html", ".css", ".scss", ".sass", ".less",
    ".json", ".yaml", ".yml", ".toml",
    ".r", ".R", ".scala", ".groovy", ".dart", ".lua", ".pl",
)

LANG_TO_EXT = {
    "python": ".py", "py": ".py",
    "java": ".java",
    "c": ".c", "h": ".h",
    "cpp": ".cpp", "c++": ".cpp", "hpp": ".hpp", "cc": ".cc", "cxx": ".cxx",
    "typescript": ".ts", "ts": ".ts", "tsx": ".tsx",
    "javascript": ".js", "js": ".js", "jsx": ".jsx",
    "go": ".go", "golang": ".go",
    "rust": ".rs", "rs": ".rs",
    "csharp": ".cs", "cs": ".cs",
    "kotlin": ".kt", "kt": ".kt",
    "swift": ".swift",
    "ruby": ".rb", "rb": ".rb",
    "php": ".php",
    "shell": ".sh", "bash": ".sh", "sh": ".sh", "zsh": ".zsh",
    "sql": ".sql",
    "html": ".html", "css": ".css", "scss": ".scss",
    "json": ".json", "yaml": ".yaml", "yml": ".yml", "toml": ".toml",
    "scala": ".scala", "groovy": ".groovy",
    "dart": ".dart", "lua": ".lua", "perl": ".pl", "r": ".r",
}

# Pydantic models

class RunControlRequest(BaseModel):
    session_id: str
    prompt: Optional[str] = None
    issue_description: Optional[str] = None
    model_name: Optional[str] = "gemini-2.5-flash-lite"
    workspace_path: Optional[str] = None
    api_key: Optional[str] = None


class RunControlResponse(BaseModel):
    session_id: str
    status: str
    message: str
    score: Optional[int] = None
    tests_summary: Optional[str] = None
    execution_time_sec: Optional[float] = 0.0


# Helpers

async def publish_stage_event(
    event_type: EventType,
    stage_name: str,
    completed: int,
    total: int = 7,
    log_line: Optional[str] = None,
    payload: Optional[dict] = None,
):
    pct = round((completed / total) * 100.0, 1)
    evt = SSEEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        stage_name=stage_name,
        completed_stages=completed,
        total_stages=total,
        progress_percentage=pct,
        log_line=log_line,
        payload=payload or {},
    )
    await broadcaster.publish(evt)


def collect_workspace_files(workspace: str) -> List[Tuple[str, str]]:
    results = []
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel_root = os.path.relpath(root, workspace)
        parts = rel_root.replace("\\", "/").split("/")
        if any(p in SKIP_DIRS for p in parts if p and p != "."):
            continue
        for f in sorted(files):
            if f.endswith(SUPPORTED_EXTS):
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, workspace)
                results.append((abs_path, rel_path))
    return results


def build_code_context(workspace: str) -> str:
    file_pairs = collect_workspace_files(workspace)
    if not file_pairs:
        return "No source files found in workspace."
    snippets = []
    for abs_path, rel_path in file_pairs:
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            snippets.append(f"=== File: {rel_path} ===\n{content}\n")
        except Exception as e:
            snippets.append(f"=== File: {rel_path} === [Could not read: {e}]\n")
    return "\n".join(snippets)


def detect_python_syntax_errors(workspace: str) -> List[str]:
    errors = []
    for abs_path, rel_path in collect_workspace_files(workspace):
        if not abs_path.endswith(".py"):
            continue
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as fh:
                source = fh.read()
            ast.parse(source, filename=rel_path)
        except SyntaxError as e:
            msg = f"SyntaxError in {rel_path} at line {e.lineno}: {e.msg}"
            if e.text:
                msg += f"\n  Offending code: {e.text.strip()}"
            errors.append(msg)
        except Exception as e:
            errors.append(f"ParseError in {rel_path}: {e}")
    return errors


def extract_verification_errors(verif_res: VerificationRun) -> str:
    errors = []
    for stage in verif_res.stage_results:
        if not stage.passed and stage.raw_output and stage.raw_output.strip():
            errors.append(f"[{stage.stage.value.upper()} FAILURE]\n{stage.raw_output.strip()}")
    return "\n\n".join(errors)


def write_file_safely(path: str, content: str) -> bool:
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
            if not content.endswith("\n"):
                fh.write("\n")
        return True
    except Exception as e:
        logger.error(f"[FileWrite] Failed to write {path}: {e}")
        return False


def apply_code_fixes(workspace: str, ai_response: str) -> List[str]:
    """
    Parse markdown code blocks from AI response and write to correct files.
    Strategy:
      1. Explicit File: header comment inside code block
      2. Filename mentioned anywhere in AI response
      3. Single source file in workspace -> auto-target it
      4. Match by language extension if only one file of that type exists
    """
    modified: List[str] = []
    code_block_pattern = re.compile(
        r"```(?P<lang>[a-zA-Z0-9_+\-]*)\s*\n(?P<body>.*?)```",
        re.DOTALL,
    )
    workspace_files = collect_workspace_files(workspace)
    workspace_file_names = {os.path.basename(p[0]): p[0] for p in workspace_files}

    for m in code_block_pattern.finditer(ai_response):
        lang_tag = m.group("lang").lower().strip()
        body = m.group("body")

        header_match = re.match(
            r"^(?://|#|/\*|<!--)\s*File:\s*([^\n\r*`]+)",
            body.strip(),
            re.IGNORECASE,
        )

        no_code_langs = {"", "text", "diff", "log", "output", "console", "powershell", "cmd"}
        if lang_tag in no_code_langs and not header_match:
            continue

        target_path = None
        if header_match:
            declared_name = os.path.basename(header_match.group(1).strip().strip("`* "))
            body_lines = body.strip().splitlines()
            body = "\n".join(body_lines[1:])
            if declared_name in workspace_file_names:
                target_path = workspace_file_names[declared_name]
            else:
                target_path = os.path.join(workspace, declared_name)

        if not target_path:
            for fname, abs_path in workspace_file_names.items():
                if fname in ai_response:
                    target_path = abs_path
                    break

        if not target_path and len(workspace_files) == 1:
            target_path = workspace_files[0][0]

        if not target_path and lang_tag in LANG_TO_EXT:
            ext = LANG_TO_EXT[lang_tag]
            candidates = [p for p in workspace_files if p[0].endswith(ext)]
            if len(candidates) == 1:
                target_path = candidates[0][0]

        if not target_path:
            logger.debug(f"[CodeFix] Cannot resolve target for lang={lang_tag!r}, skipping.")
            continue

        clean_code = body.strip()
        if not clean_code:
            continue

        if write_file_safely(target_path, clean_code):
            basename = os.path.basename(target_path)
            if basename not in modified:
                modified.append(basename)
            logger.info(f"[CodeFix] Wrote {len(clean_code)} bytes to {target_path}")

    return modified


# Recursive repair engine

async def recursive_repair_loop(
    workspace: str,
    prompt: str,
    gemini: GeminiAdapter,
    runner: VerificationRunner,
    sandbox: Any,
    initial_verif: VerificationRun,
    max_attempts: int = 6,
) -> Tuple[List[str], VerificationRun, str]:
    all_modified: List[str] = []
    latest_verif = initial_verif
    latest_ai_text = ""

    for attempt in range(1, max_attempts + 1):
        py_errors = detect_python_syntax_errors(workspace)
        verif_errors = extract_verification_errors(latest_verif)

        combined_errors = ""
        if py_errors:
            combined_errors += "=== Python Syntax Errors ===\n" + "\n".join(py_errors) + "\n\n"
        if verif_errors:
            combined_errors += "=== Verification / Test Failures ===\n" + verif_errors + "\n\n"

        if attempt > 1 and not combined_errors and latest_verif.success:
            logger.info(f"[RepairLoop] All clean after {attempt - 1} attempt(s). Done.")
            break

        code_context = build_code_context(workspace)

        if combined_errors:
            task_section = f"ERRORS DETECTED -- REPAIR REQUIRED:\n\n{combined_errors}\nUser task: {prompt}"
        else:
            task_section = f"No errors. Review code quality and apply improvements.\nUser task: {prompt}"

        system_prompt = (
            "You are an autonomous AI code repair engine with full write access to the repository.\n"
            "Rules:\n"
            "  1. Output EVERY modified file as a fenced markdown code block.\n"
            "  2. First line inside each code block MUST be a file header:\n"
            "       Python/Shell/Ruby/SQL: # File: <filename>\n"
            "       Java/C/C++/Go/Rust/JS/TS/C#/Kotlin/Swift: // File: <filename>\n"
            "  3. Output COMPLETE file contents -- no partial snippets, no diffs.\n"
            "  4. Fix ALL syntax errors, ALL logic bugs, ALL compilation errors.\n"
            "  5. Output ONLY code blocks. No explanations, no prose.\n"
        )

        user_message = (
            f"=== REPAIR ATTEMPT {attempt}/{max_attempts} ===\n\n"
            f"{task_section}\n\n"
            f"=== FULL REPOSITORY SOURCE CODE ===\n\n"
            f"{code_context}\n\n"
            f"Output complete corrected replacement file(s) now:"
        )

        logger.info(f"[RepairLoop] Attempt {attempt}/{max_attempts}, prompt length: {len(user_message)} chars")

        try:
            completion = await gemini.complete(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt,
            )
            latest_ai_text = completion.content
        except Exception as e:
            logger.error(f"[RepairLoop] Gemini call error on attempt {attempt}: {e}")
            latest_ai_text = f"[Gemini error: {e}]"
            await asyncio.sleep(1)
            continue

        fixed = apply_code_fixes(workspace, latest_ai_text)
        for f in fixed:
            if f not in all_modified:
                all_modified.append(f)

        if not fixed:
            logger.warning(f"[RepairLoop] Attempt {attempt}: no code blocks found in AI response.")

        try:
            latest_verif = runner.run_verification()
            new_py = detect_python_syntax_errors(workspace)
            new_verif = extract_verification_errors(latest_verif)
            if not new_py and not new_verif and latest_verif.success:
                logger.info(f"[RepairLoop] Verification 100% clean after attempt {attempt}!")
                break
            logger.info(
                f"[RepairLoop] After attempt {attempt}: py_errors={len(new_py)}, "
                f"verif_errors={bool(new_verif)}, success={latest_verif.success}"
            )
        except Exception as e:
            logger.warning(f"[RepairLoop] Verification re-run error on attempt {attempt}: {e}")

    return all_modified, latest_verif, latest_ai_text


# Route handlers

@router.post("/run", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
@router.post("/run/start", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def start_run(payload: RunControlRequest):
    """
    Full autonomous pipeline:
      1. Scan  2. Detect  3. Docker  4. Deps  5. Verify  6. AI Repair Loop  7. Report
    """
    start_time = time.time()
    session_id = payload.session_id
    model_name = payload.model_name or "gemini-2.5-flash-lite"
    prompt = payload.prompt or payload.issue_description or "Fix all errors, improve code quality."
    workspace = payload.workspace_path or os.getcwd()
    api_key = (
        payload.api_key
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY", "")
    )

    source_files = collect_workspace_files(workspace)
    await publish_stage_event(
        EventType.CLONE_COMPLETED, "Repository Scanned", completed=1,
        log_line=f"[Scan] {len(source_files)} source file(s) found in {workspace}",
    )

    exts_found = sorted({os.path.splitext(p[0])[1] for p in source_files})
    await publish_stage_event(
        EventType.DETECTION_COMPLETED, "Language & Environment Detected", completed=2,
        log_line=f"[Detect] Types: {', '.join(exts_found) or 'none'}",
    )

    env_vars = {
        "GEMINI_API_KEY": api_key, "GOOGLE_API_KEY": api_key,
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
    }
    container_id = "local-process-sandbox"
    sandbox = None
    try:
        sandbox = DockerSandbox(SandboxConfig(host_workspace_path=workspace, env_vars=env_vars))
        container_id = sandbox.start()
        docker_log = f"[Docker] Container: {container_id[:12] if container_id else 'active'}"
    except Exception as e:
        docker_log = f"[Docker] Unavailable ({e}). Local process mode."
    await publish_stage_event(
        EventType.CONTAINER_STARTED, "Docker Sandbox Ready", completed=3, log_line=docker_log,
    )

    if sandbox and getattr(sandbox, "container", None):
        dep_res = sandbox.exec_command("python -m pip --version")
        dep_log = f"[Deps] {dep_res.stdout.strip()[:100] or 'pip active'}"
    else:
        dep_log = "[Deps] Local process dependency check."
    await publish_stage_event(
        EventType.DEPENDENCY_INSTALL_COMPLETED, "Dependencies Verified", completed=4, log_line=dep_log,
    )

    await publish_stage_event(
        EventType.TESTS_STARTED, "Running Verification Suite", completed=4,
        log_line="[Verify] Running lint + tests...",
    )

    def docker_exec(cmd: list, cwd: str) -> Tuple[int, str, str]:
        translated = []
        for arg in cmd:
            if workspace in arg or (os.sep in arg and arg.startswith(workspace[:3])):
                translated.append(arg.replace(workspace, "/workspace").replace("\\", "/"))
            else:
                translated.append(arg)
        res = sandbox.exec_command(" ".join(translated), cwd="/workspace")
        return res.exit_code, res.stdout, res.stderr

    runner = (
        VerificationRunner(workspace_path=workspace, command_executor=docker_exec)
        if sandbox and getattr(sandbox, "container", None)
        else VerificationRunner(workspace_path=workspace)
    )
    initial_verif = runner.run_verification()
    py_syntax_errors = detect_python_syntax_errors(workspace)

    verif_log = f"[Verify] {initial_verif.summary_message}"
    if py_syntax_errors:
        verif_log += f" | {len(py_syntax_errors)} syntax error(s) detected."
    await publish_stage_event(
        EventType.TESTS_COMPLETED, "Verification Complete", completed=5,
        log_line=verif_log, payload={"pytest_results": initial_verif.pytest_results},
    )

    await publish_stage_event(
        EventType.ANALYSIS_STARTED, "AI Recursive Repair Engine", completed=5,
        log_line=f"[AI] Model: {model_name} | Max 6 attempts | No token cap",
    )

    from backend.orchestrator.sandbox.snapshot_manager import SnapshotManager
    snap_mgr = None
    try:
        if sandbox and getattr(sandbox, "container", None):
            snap_mgr = SnapshotManager(sandbox)
            snap_mgr.initialize_workspace_git()
    except Exception as e:
        logger.warning(f"[Snapshot] Init failed: {e}")

    gemini = GeminiAdapter(model_name=model_name, api_key=api_key)
    modified_files, final_verif, ai_summary = await recursive_repair_loop(
        workspace=workspace, prompt=prompt, gemini=gemini,
        runner=runner, sandbox=sandbox, initial_verif=initial_verif, max_attempts=6,
    )

    repair_log = (
        f"[AI] Done. Modified: {', '.join(modified_files) or 'none'}. "
        f"Status: {'CLEAN' if final_verif.success else 'needs-review'}."
    )
    await publish_stage_event(
        EventType.PATCH_APPLIED if modified_files else EventType.ANALYSIS_COMPLETED,
        "Repair Complete", completed=6,
        log_line=repair_log, payload={"modified_files": modified_files},
    )

    elapsed = round(time.time() - start_time, 2)
    tests_passed = final_verif.pytest_results.get("passed", 0)
    tests_total = final_verif.pytest_results.get("total", 0)
    tests_summary = f"{tests_passed}/{tests_total} passed" if tests_total else "N/A"

    rem_py = detect_python_syntax_errors(workspace)
    rem_verif = extract_verification_errors(final_verif)
    combined_remaining = ("\n".join(rem_py) + "\n" + rem_verif).strip()
    overall_clean = not rem_py and not rem_verif and final_verif.success

    docs_dir = os.path.join(workspace, "Docs")
    os.makedirs(docs_dir, exist_ok=True)
    report_content = "\n".join([
        "# AI Autonomous Code Repair Report", "",
        "| Field | Value |", "|---|---|",
        f"| Session ID | {session_id} |",
        f"| Docker Container | {container_id[:12] if container_id else 'local'} |",
        f"| AI Model | {model_name} |",
        f"| Repair Status | {'CLEAN -- All errors resolved' if overall_clean else 'Partial -- Review remaining issues'} |",
        f"| Tests | {tests_summary} |",
        f"| Files Modified | {', '.join(modified_files) if modified_files else 'None'} |",
        f"| Duration | {elapsed}s |", "",
        "## Remaining Issues After Repair", "",
        f"```\n{combined_remaining or 'No errors remaining.'}\n```", "",
        "## AI Repair Analysis", "", ai_summary,
    ])

    for fname in ("fix_report.md", "codebase_review.md"):
        write_file_safely(os.path.join(docs_dir, fname), report_content)

    if snap_mgr and modified_files:
        try:
            snap = snap_mgr.create_checkpoint(
                step_name="AI Code Fix Applied",
                description=f"Autonomous repair: {', '.join(modified_files)}",
            )
            commit_short = snap.commit_hash[:8] if snap.commit_hash else "committed"
            await publish_stage_event(
                EventType.PATCH_APPLIED, "Changes Committed to Git", completed=7,
                log_line=f"[Git] Committed ({commit_short}): {', '.join(modified_files)}",
            )
        except Exception as e:
            logger.warning(f"[Git] Commit failed: {e}")

    await publish_stage_event(
        EventType.REPORT_COMPLETED, "Execution Complete", completed=7,
        log_line=f"[Done] Report saved in {elapsed}s.",
        payload={
            "score": 100 if overall_clean else 75,
            "tests_summary": tests_summary,
            "elapsed_seconds": elapsed,
            "modified_files": modified_files,
            "report_path": os.path.join(docs_dir, "fix_report.md"),
        },
    )

    return RunControlResponse(
        session_id=session_id,
        status="completed",
        message=f"Repair finished. {'All clean.' if overall_clean else 'See Docs/fix_report.md.'}",
        score=100 if overall_clean else 75,
        tests_summary=tests_summary,
        execution_time_sec=elapsed,
    )


@router.post("/run/pause", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def pause_run(payload: RunControlRequest):
    return RunControlResponse(session_id=payload.session_id, status="paused", message="Execution paused")


@router.post("/run/resume", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def resume_run(payload: RunControlRequest):
    return RunControlResponse(session_id=payload.session_id, status="running", message="Execution resumed")


@router.post("/run/cancel", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def cancel_run(payload: RunControlRequest):
    return RunControlResponse(session_id=payload.session_id, status="cancelled", message="Execution cancelled")
'''

with open(r"d:\Billu-Gang\Billu-Gang\backend\core\routes\run_routes.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(NEW_CONTENT.strip() + "\n")

print(f"Written {len(NEW_CONTENT.strip().splitlines())} lines to run_routes.py")

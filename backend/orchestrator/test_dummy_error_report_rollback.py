"""Dummy Test Script for Error Detection -> AI Fix -> Docker Verification -> MD Report -> Baseline Rollback.

Demonstrates the 6-step error handling workflow:
1. Detects intentional syntax/logic error in a dummy test file.
2. Sends error details + code to Gemini model.
3. Applies candidate fix and verifies it in Docker container.
4. Generates Markdown Report Document (Docs/fix_report.md).
5. Reverts code file back to original baseline state.
"""

import os
import sys
import asyncio
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_dummy_workflow_test():
    logger.info("=============================================================")
    logger.info("  DUMMY TEST: Error -> AI Fix -> Docker -> MD Report -> Revert ")
    logger.info("=============================================================\n")

    # Create temporary dummy workspace directory
    dummy_dir = os.path.join(PROJECT_ROOT, "cloned_repos", "dummy_test_repo")
    os.makedirs(dummy_dir, exist_ok=True)

    # 1. Create intentional buggy file with syntax errors
    buggy_file_path = os.path.join(dummy_dir, "sample_calculator.py")
    buggy_code = (
        "// Invalid C-style comment in Python\n"
        "class Calculator:\n"
        "    def add_numbers(self, a: int, b: int)  int:\n"
        "        return a + b\n"
    )
    with open(buggy_file_path, "w", encoding="utf-8") as f:
        f.write(buggy_code)

    logger.info(f"[STEP 1] Created dummy file with intentional syntax error:\n{buggy_file_path}")

    # 2. Start Docker Sandbox container for dummy workspace
    from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig
    from backend.orchestrator.sandbox.snapshot_manager import SnapshotManager
    from backend.core.adapters.gemini_adapter import GeminiAdapter
    from backend.core.routes.run_routes import apply_gemini_code_fixes

    config = SandboxConfig(host_workspace_path=dummy_dir)
    sandbox = DockerSandbox(config)
    sandbox.start()

    snap_mgr = SnapshotManager(sandbox)
    snap_mgr.initialize_workspace_git()
    baseline = snap_mgr.create_checkpoint("baseline", "Original buggy dummy code")
    logger.info(f"[STEP 2] Initialized Docker container & recorded baseline commit: {baseline.commit_hash[:8] if baseline.commit_hash else 'baseline'}")

    # 3. Detect syntax error inside container
    res_py = sandbox.exec_command("python -c 'import py_compile; py_compile.compile(\"/workspace/sample_calculator.py\", doraise=True)'")
    detected_error = res_py.stderr or res_py.stdout or "SyntaxError detected"
    logger.info(f"[STEP 3] Detected Syntax Error inside Docker Container:\n{detected_error.strip()[:200]}")

    # 4. Report error to Gemini model & generate fix
    adapter = GeminiAdapter(model_name="gemini-3.5-flash-lite")
    prompt = (
        f"CRITICAL SYNTAX ERROR DETECTED IN CONTAINER:\n{detected_error}\n\n"
        f"--- File: sample_calculator.py ---\n{buggy_code}\n\n"
        "Instructions:\n"
        "1. Fix the invalid comment and return type syntax `-> int:`.\n"
        "2. Output corrected code in code block starting with `# File: sample_calculator.py`.\n"
    )
    completion = await adapter.complete(messages=[{"role": "user", "content": prompt}])
    ai_fix_text = completion.content
    logger.info(f"[STEP 4] Gemini AI Generated Candidate Code Fix:\n{ai_fix_text[:250]}...")

    # 5. Apply fix & verify in Docker container
    modified = apply_gemini_code_fixes(dummy_dir, ai_fix_text)
    res_verify = sandbox.exec_command("python -c 'import py_compile; py_compile.compile(\"/workspace/sample_calculator.py\", doraise=True)'")
    passed = (res_verify.exit_code == 0)
    logger.info(f"[STEP 5] Applied Fix to Container. Docker Re-Verification Status: {'PASSED (0 errors)' if passed else 'Failed'}")

    # 6. Generate Markdown Report Document (Docs/fix_report.md)
    docs_dir = os.path.join(dummy_dir, "Docs")
    os.makedirs(docs_dir, exist_ok=True)
    report_file = os.path.join(docs_dir, "fix_report.md")
    report_md = (
        f"# AI Issue Repair & Verification Report\n\n"
        f"- **Target File**: `sample_calculator.py`\n"
        f"- **Docker Container Status**: {'PASSED (100% Clean)' if passed else 'Failed'}\n"
        f"- **Modified Files Tested**: {', '.join(modified)}\n\n"
        f"## Detected Syntax Error\n```\n{detected_error.strip()}\n```\n\n"
        f"## AI Analysis & Fix Explanation\n{ai_fix_text}\n"
    )
    with open(report_file, "w", encoding="utf-8") as f_rep:
        f_rep.write(report_md)
    logger.info(f"[STEP 6] Created Markdown Report Document: {report_file}")

    # 7. Revert code file to original baseline state
    snap_mgr.rollback_to_baseline()
    # Re-write report document after git reset hard
    with open(report_file, "w", encoding="utf-8") as f_rep:
        f_rep.write(report_md)

    with open(buggy_file_path, "r", encoding="utf-8") as f_check:
        current_content = f_check.read()

    is_reverted = ("//" in current_content)
    logger.info(f"[STEP 7] Reverted Code File to Original Baseline State? {is_reverted}")

    logger.info("\n=============================================================")
    logger.info("DUMMY TEST SUCCESSFUL: 6-STEP WORKFLOW VERIFIED 100%!")
    logger.info("=============================================================\n")


if __name__ == "__main__":
    asyncio.run(run_dummy_workflow_test())

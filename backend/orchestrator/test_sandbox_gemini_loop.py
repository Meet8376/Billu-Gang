"""End-to-End Verification Test for Docker Sandbox Execution & Gemini Model Integration.

Validates that code execution, verification test suites, and Gemini AI reviews
run reliably inside the active Docker container without failures.
"""

import os
import sys
import asyncio
import logging

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def test_sandbox_docker_exec():
    """Test 1: Verify container startup and execution inside Docker sandbox."""
    logger.info("=== Test 1: Container Execution inside Docker Sandbox ===")
    from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig

    config = SandboxConfig(
        host_workspace_path=PROJECT_ROOT,
        image_name="ae01-sandbox:latest"
    )
    sandbox = DockerSandbox(config)
    container_id = sandbox.start()
    assert container_id, "Failed to start Docker Sandbox container"
    logger.info(f"[OK] Sandbox Container started: {container_id[:12]}")

    res = sandbox.exec_command("python --version")
    assert res.exit_code == 0, f"Python command failed inside container: {res.stderr}"
    logger.info(f"[OK] Container Python version: {res.stdout.strip()}")

    res_pip = sandbox.exec_command("pip --version")
    assert res_pip.exit_code == 0, f"Pip command failed inside container: {res_pip.stderr}"
    logger.info(f"[OK] Container Pip version: {res_pip.stdout.strip()}")
    return sandbox


async def test_verification_pipeline_in_docker(sandbox):
    """Test 2: Verify VerificationRunner executing tests inside Docker container."""
    logger.info("=== Test 2: Verification Runner Execution in Container ===")
    from backend.verification.pipeline.runner import VerificationRunner

    def docker_exec(cmd: list, cwd: str):
        container_cmd = []
        for arg in cmd:
            if PROJECT_ROOT in arg or (":" in arg and "\\" in arg):
                container_cmd.append("/workspace")
            else:
                container_cmd.append(arg)
        cmd_str = " ".join(container_cmd)
        res = sandbox.exec_command(cmd_str, cwd="/workspace")
        return res.exit_code, res.stdout, res.stderr

    runner = VerificationRunner(
        workspace_path=PROJECT_ROOT,
        command_executor=docker_exec
    )
    verif_run = runner.run_verification(session_id="test-docker-sess")
    assert verif_run is not None, "Verification run returned None"
    logger.info(f"[OK] Verification Run completed (Success: {verif_run.success}, Stages: {len(verif_run.stage_results)})")
    for stage in verif_run.stage_results:
        logger.info(f"    - Stage '{stage.stage.value}': Passed={stage.passed} ({stage.duration_ms:.1f}ms)")


async def test_gemini_adapter():
    """Test 3: Verify GeminiAdapter model completion and prompt review."""
    logger.info("=== Test 3: Gemini Model Adapter Verification ===")
    from backend.core.adapters.gemini_adapter import GeminiAdapter

    adapter = GeminiAdapter(model_name="gemini-3.5-flash-lite")
    logger.info(f"[OK] Initialized GeminiAdapter with mapped model '{adapter.model_name}'")

    completion = await adapter.complete(
        messages=[{"role": "user", "content": "Return a 1-sentence verification confirming Gemini AI review active inside Docker sandbox."}],
        system_prompt="You are a code review agent."
    )
    assert completion.content, "Completion response content was empty"
    logger.info(f"[OK] Gemini AI Completion Output: {completion.content[:150]}")


async def test_full_run_routes_integration():
    """Test 4: Verify complete end-to-end /run endpoint execution."""
    logger.info("=== Test 4: Full Run Routes Pipeline Execution ===")
    from backend.core.routes.run_routes import start_run, RunControlRequest

    req = RunControlRequest(
        session_id="e2e-test-session",
        prompt="Verify Docker container test execution and Gemini AI review",
        model_name="gemini-3.5-flash-lite",
        workspace_path=PROJECT_ROOT
    )
    resp = await start_run(req)
    assert resp.status == "completed", f"Run status was '{resp.status}', expected 'completed'"
    logger.info(f"[OK] Full /run pipeline executed cleanly: {resp.message} (Score: {resp.score}, Tests: {resp.tests_summary})")


async def main():
    logger.info("Starting End-to-End Docker Sandbox & Gemini Verification Test Suite...")
    try:
        sandbox = await test_sandbox_docker_exec()
        await test_verification_pipeline_in_docker(sandbox)
        await test_gemini_adapter()
        await test_full_run_routes_integration()
        logger.info("\n" + "=" * 60)
        logger.info("ALL DOCKER SANDBOX & GEMINI INTEGRATION TESTS PASSED CLEANLY!")
        logger.info("=" * 60 + "\n")
    except Exception as e:
        logger.error(f"TEST SUITE FAILED: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

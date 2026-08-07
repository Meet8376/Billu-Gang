"""Unit tests for Phase 6 Quick-Start Setup and Validation (Member 4 Lead)."""

from backend.orchestrator.setup_sandbox import check_docker_daemon, check_python_dependencies, check_python_environment, run_setup_validation


def test_quickstart_validation_routines():
    """Verify quick-start environment check functions execute cleanly."""
    py_ok = check_python_environment()
    assert py_ok is True

    deps = check_python_dependencies()
    assert "pydantic" in deps
    assert deps["pydantic"] is True

    docker_ok, _ = check_docker_daemon()
    assert isinstance(docker_ok, bool)

    setup_res = run_setup_validation()
    assert setup_res is True

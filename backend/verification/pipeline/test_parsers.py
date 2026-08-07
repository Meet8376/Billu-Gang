"""
Test Output Parser Module.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import json
import xml.etree.ElementTree as ET
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TestResultStatus(str, Enum):
    """Execution status for individual test cases."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestCaseResult(BaseModel):
    """Detailed record of an individual test case result."""
    name: str = Field(..., description="Name of the test case")
    classname: Optional[str] = Field(None, description="Class or module name containing the test")
    file: Optional[str] = Field(None, description="File path of the test")
    duration_seconds: float = Field(0.0, description="Execution duration in seconds")
    status: TestResultStatus = Field(TestResultStatus.PASSED, description="Test outcome status")
    message: Optional[str] = Field(None, description="Failure or error message/stacktrace")
    stdout: Optional[str] = Field(None, description="Standard output captured during test execution")
    stderr: Optional[str] = Field(None, description="Standard error captured during test execution")


class TestRunSummary(BaseModel):
    """Aggregated summary of a test suite execution."""
    framework: str = Field(..., description="Testing framework (pytest, jest, npm, etc.)")
    passed: int = Field(0, description="Total passed test count")
    failed: int = Field(0, description="Total failed test count")
    skipped: int = Field(0, description="Total skipped test count")
    errors: int = Field(0, description="Total errored test count")
    total: int = Field(0, description="Total test count")
    duration_seconds: float = Field(0.0, description="Total suite execution duration")
    test_cases: List[TestCaseResult] = Field(default_factory=list, description="List of individual test case results")
    raw_output: Optional[str] = Field(None, description="Raw test runner output string")

    @property
    def is_success(self) -> bool:
        """Returns True if no tests failed or errored."""
        return self.failed == 0 and self.errors == 0


def parse_pytest_xml(xml_content_or_path: str) -> TestRunSummary:
    """
    Parses Pytest / JUnit XML output string or file path into a typed TestRunSummary.
    """
    content = xml_content_or_path
    path = Path(xml_content_or_path)
    if path.exists() and path.is_file():
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            pass

    test_cases: List[TestCaseResult] = []
    passed = 0
    failed = 0
    skipped = 0
    errors = 0
    total_time = 0.0

    try:
        root = ET.fromstring(content)
        # Handle <testsuites> wrapper or single <testsuite> root
        suites = root.findall(".//testsuite") if root.tag == "testsuites" else [root]

        for suite in suites:
            total_time += float(suite.attrib.get("time", 0.0))
            for case in suite.findall("testcase"):
                c_name = case.attrib.get("name", "unknown")
                c_class = case.attrib.get("classname", "")
                c_file = case.attrib.get("file", None)
                c_time = float(case.attrib.get("time", 0.0))

                c_status = TestResultStatus.PASSED
                c_msg = None

                failure_node = case.find("failure")
                error_node = case.find("error")
                skipped_node = case.find("skipped")

                if failure_node is not None:
                    c_status = TestResultStatus.FAILED
                    failed += 1
                    c_msg = failure_node.attrib.get("message") or failure_node.text
                elif error_node is not None:
                    c_status = TestResultStatus.ERROR
                    errors += 1
                    c_msg = error_node.attrib.get("message") or error_node.text
                elif skipped_node is not None:
                    c_status = TestResultStatus.SKIPPED
                    skipped += 1
                    c_msg = skipped_node.attrib.get("message") or skipped_node.text
                else:
                    passed += 1

                system_out_node = case.find("system-out")
                system_err_node = case.find("system-err")
                c_stdout = system_out_node.text if system_out_node is not None else None
                c_stderr = system_err_node.text if system_err_node is not None else None

                test_cases.append(
                    TestCaseResult(
                        name=c_name,
                        classname=c_class,
                        file=c_file,
                        duration_seconds=c_time,
                        status=c_status,
                        message=c_msg,
                        stdout=c_stdout,
                        stderr=c_stderr,
                    )
                )
    except Exception as e:
        # Fallback for malformed XML
        return TestRunSummary(
            framework="pytest_xml",
            passed=0,
            failed=1,
            errors=1,
            total=1,
            duration_seconds=0.0,
            raw_output=content,
            test_cases=[
                TestCaseResult(
                    name="xml_parse_error",
                    status=TestResultStatus.ERROR,
                    message=f"Failed to parse pytest XML output: {str(e)}",
                )
            ],
        )

    return TestRunSummary(
        framework="pytest_xml",
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        total=len(test_cases),
        duration_seconds=total_time,
        test_cases=test_cases,
        raw_output=content,
    )


def parse_pytest_json(json_content_or_path: str) -> TestRunSummary:
    """
    Parses pytest-json report output string or JSON file path into a typed TestRunSummary.
    """
    content = json_content_or_path
    path = Path(json_content_or_path)
    if path.exists() and path.is_file():
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            pass

    try:
        data: Dict[str, Any] = json.loads(content)
        summary_dict = data.get("summary", {})
        passed = summary_dict.get("passed", 0)
        failed = summary_dict.get("failed", 0)
        skipped = summary_dict.get("skipped", 0)
        errors = summary_dict.get("error", 0)
        total = summary_dict.get("total", passed + failed + skipped + errors)
        duration = float(data.get("duration", 0.0))

        test_cases: List[TestCaseResult] = []
        tests_list = data.get("tests", [])
        for t in tests_list:
            nodeid = t.get("nodeid", "")
            outcome = t.get("outcome", "passed")
            c_duration = float(t.get("duration", 0.0))

            if outcome == "passed":
                status = TestResultStatus.PASSED
            elif outcome == "failed":
                status = TestResultStatus.FAILED
            elif outcome == "skipped":
                status = TestResultStatus.SKIPPED
            else:
                status = TestResultStatus.ERROR

            call_info = t.get("call", {})
            crash_info = call_info.get("crash", {})
            msg = crash_info.get("message") or call_info.get("longrepr")

            test_cases.append(
                TestCaseResult(
                    name=nodeid,
                    duration_seconds=c_duration,
                    status=status,
                    message=str(msg) if msg else None,
                )
            )

        return TestRunSummary(
            framework="pytest_json",
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total=total,
            duration_seconds=duration,
            test_cases=test_cases,
            raw_output=content,
        )
    except Exception as e:
        return TestRunSummary(
            framework="pytest_json",
            passed=0,
            failed=1,
            errors=1,
            total=1,
            raw_output=content,
            test_cases=[
                TestCaseResult(
                    name="json_parse_error",
                    status=TestResultStatus.ERROR,
                    message=f"Failed to parse pytest JSON output: {str(e)}",
                )
            ],
        )


def parse_npm_test(stdout_content: str) -> TestRunSummary:
    """
    Parses Jest / npm test stdout content or Jest JSON output into a typed TestRunSummary.
    """
    # Attempt to parse as Jest JSON output first
    try:
        data = json.loads(stdout_content)
        if "numPassedTests" in data or "testResults" in data:
            passed = data.get("numPassedTests", 0)
            failed = data.get("numFailedTests", 0)
            pending = data.get("numPendingTests", 0)
            total = data.get("numTotalTests", passed + failed + pending)
            duration = 0.0
            test_results = data.get("testResults", [])
            test_cases: List[TestCaseResult] = []

            for tr in test_results:
                perf = tr.get("perfStats", {})
                if perf.get("end") and perf.get("start"):
                    duration += (perf["end"] - perf["start"]) / 1000.0

                for assertion in tr.get("assertionResults", []):
                    title = assertion.get("title", "")
                    status_str = assertion.get("status", "passed")
                    st = TestResultStatus.PASSED if status_str == "passed" else TestResultStatus.FAILED
                    msg = "\n".join(assertion.get("failureMessages", [])) or None

                    test_cases.append(
                        TestCaseResult(
                            name=title,
                            file=tr.get("testFilePath"),
                            status=st,
                            message=msg,
                        )
                    )

            return TestRunSummary(
                framework="jest_npm_json",
                passed=passed,
                failed=failed,
                skipped=pending,
                errors=0,
                total=total,
                duration_seconds=duration,
                test_cases=test_cases,
                raw_output=stdout_content,
            )
    except Exception:
        pass

    # Regex/line-based text parsing fallback for terminal stdout output
    passed = 0
    failed = 0
    skipped = 0
    total = 0
    test_cases: List[TestCaseResult] = []

    lines = stdout_content.splitlines()
    for line in lines:
        line_strip = line.strip()
        if "PASS" in line_strip:
            passed += 1
            test_cases.append(TestCaseResult(name=line_strip, status=TestResultStatus.PASSED))
        elif "FAIL" in line_strip:
            failed += 1
            test_cases.append(TestCaseResult(name=line_strip, status=TestResultStatus.FAILED, message=line_strip))
        elif "Tests:" in line_strip:
            # Parse Jest summary line, e.g., "Tests: 2 failed, 10 passed, 12 total"
            parts = line_strip.replace("Tests:", "").split(",")
            for part in parts:
                part = part.strip()
                tokens = part.split()
                if len(tokens) >= 2:
                    val = int(tokens[0]) if tokens[0].isdigit() else 0
                    if "passed" in tokens[1]:
                        passed = val
                    elif "failed" in tokens[1]:
                        failed = val
                    elif "skipped" in tokens[1] or "pending" in tokens[1]:
                        skipped = val
                    elif "total" in tokens[1]:
                        total = val

    if total == 0:
        total = passed + failed + skipped

    return TestRunSummary(
        framework="jest_npm_text",
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=0,
        total=total,
        duration_seconds=0.0,
        test_cases=test_cases,
        raw_output=stdout_content,
    )

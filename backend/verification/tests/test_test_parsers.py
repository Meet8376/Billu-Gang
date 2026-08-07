"""
Unit tests for test_parsers module (pytest XML/JSON & npm test output parsing).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import pytest
from backend.verification.pipeline.test_parsers import (
    parse_pytest_xml,
    parse_pytest_json,
    parse_npm_test,
    TestResultStatus,
)


def test_parse_pytest_xml_success():
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="pytest" errors="0" failures="0" skipped="0" tests="2" time="0.123">
        <testcase classname="tests.test_sample" name="test_addition" time="0.050" />
        <testcase classname="tests.test_sample" name="test_subtraction" time="0.073" />
    </testsuite>
</testsuites>"""

    summary = parse_pytest_xml(xml_content)
    assert summary.framework == "pytest_xml"
    assert summary.passed == 2
    assert summary.failed == 0
    assert summary.errors == 0
    assert summary.total == 2
    assert summary.is_success is True
    assert len(summary.test_cases) == 2
    assert summary.test_cases[0].name == "test_addition"
    assert summary.test_cases[0].status == TestResultStatus.PASSED


def test_parse_pytest_xml_failure():
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="pytest" errors="0" failures="1" skipped="1" tests="3" time="0.5">
    <testcase classname="tests.test_demo" name="test_pass" time="0.1" />
    <testcase classname="tests.test_demo" name="test_fail" time="0.2">
        <failure message="AssertionError: 1 != 2">Stacktrace details here</failure>
    </testcase>
    <testcase classname="tests.test_demo" name="test_skip" time="0.0">
        <skipped message="Skipped due to condition" />
    </testcase>
</testsuite>"""

    summary = parse_pytest_xml(xml_content)
    assert summary.passed == 1
    assert summary.failed == 1
    assert summary.skipped == 1
    assert summary.total == 3
    assert summary.is_success is False
    assert summary.test_cases[1].status == TestResultStatus.FAILED
    assert "AssertionError" in summary.test_cases[1].message


def test_parse_pytest_json():
    json_content = """{
        "duration": 1.25,
        "summary": {
            "passed": 3,
            "failed": 1,
            "total": 4
        },
        "tests": [
            {"nodeid": "test_a.py::test_1", "outcome": "passed", "duration": 0.2},
            {"nodeid": "test_a.py::test_2", "outcome": "passed", "duration": 0.3},
            {"nodeid": "test_a.py::test_3", "outcome": "passed", "duration": 0.4},
            {
                "nodeid": "test_b.py::test_4",
                "outcome": "failed",
                "duration": 0.35,
                "call": {"crash": {"message": "ValueError: Invalid input"}}
            }
        ]
    }"""

    summary = parse_pytest_json(json_content)
    assert summary.framework == "pytest_json"
    assert summary.passed == 3
    assert summary.failed == 1
    assert summary.total == 4
    assert summary.is_success is False
    assert summary.test_cases[3].status == TestResultStatus.FAILED
    assert "ValueError" in summary.test_cases[3].message


def test_parse_npm_test_json():
    jest_json = """{
        "numPassedTests": 5,
        "numFailedTests": 0,
        "numPendingTests": 1,
        "numTotalTests": 6,
        "testResults": [
            {
                "testFilePath": "/src/app.test.js",
                "perfStats": {"start": 1000, "end": 2500},
                "assertionResults": [
                    {"title": "renders header", "status": "passed"},
                    {"title": "handles button click", "status": "passed"}
                ]
            }
        ]
    }"""

    summary = parse_npm_test(jest_json)
    assert summary.framework == "jest_npm_json"
    assert summary.passed == 5
    assert summary.failed == 0
    assert summary.skipped == 1
    assert summary.total == 6
    assert summary.is_success is True


def test_parse_npm_test_stdout():
    stdout_text = """
    PASS src/utils.test.js
    FAIL src/api.test.js
    Tests: 1 failed, 4 passed, 5 total
    Snapshots: 0 total
    Time: 2.45 s
    """

    summary = parse_npm_test(stdout_text)
    assert summary.framework == "jest_npm_text"
    assert summary.passed == 4
    assert summary.failed == 1
    assert summary.total == 5
    assert summary.is_success is False

"""
Intelligent Test Runner with Context Engineering Integration
"""

import asyncio
import json
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestRunStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestFramework(Enum):
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"
    JUNIT = "junit"


@dataclass
class TestResult:
    name: str
    status: TestRunStatus
    duration: float
    message: Optional[str] = None
    traceback: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None


@dataclass
class TestSuiteResult:
    name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    coverage_percentage: Optional[float] = None
    test_results: List[TestResult] = None


@dataclass
class TestRunConfiguration:
    framework: TestFramework
    test_paths: List[str]
    parallel: bool = True
    coverage: bool = True
    verbose: bool = False
    timeout: int = 300  # seconds
    environment: Dict[str, str] = None
    markers: List[str] = None
    exclude_markers: List[str] = None


class TestRunner:
    """
    Intelligent test runner that executes generated tests with comprehensive
    reporting, coverage analysis, and integration with Context Engineering
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results_dir = self.project_root / "test_results"
        self.results_dir.mkdir(exist_ok=True)

    async def run_test_suite(
        self, test_suite, config: TestRunConfiguration
    ) -> TestSuiteResult:
        """
        Run a complete test suite with the specified configuration
        """
        print(f"Running test suite: {test_suite.name}")
        print(f"Framework: {config.framework.value}")

        # Prepare test environment
        await self._prepare_test_environment(test_suite, config)

        # Write test files
        await self._write_test_files(test_suite)

        # Execute tests
        start_time = time.time()

        if config.framework == TestFramework.PYTEST:
            result = await self._run_pytest(test_suite, config)
        elif config.framework == TestFramework.JEST:
            result = await self._run_jest(test_suite, config)
        elif config.framework == TestFramework.UNITTEST:
            result = await self._run_unittest(test_suite, config)
        else:
            raise ValueError(f"Unsupported test framework: {config.framework}")

        duration = time.time() - start_time

        # Parse results and generate reports
        suite_result = await self._parse_test_results(test_suite, result, duration)

        # Generate comprehensive report
        await self._generate_test_report(suite_result, config)

        return suite_result

    async def _prepare_test_environment(self, test_suite, config: TestRunConfiguration):
        """Prepare the test environment"""

        # Create test directory structure
        test_dir = self.project_root / "tests"
        test_dir.mkdir(exist_ok=True)

        # Create subdirectories for different test types
        (test_dir / "unit").mkdir(exist_ok=True)
        (test_dir / "integration").mkdir(exist_ok=True)
        (test_dir / "api").mkdir(exist_ok=True)
        (test_dir / "performance").mkdir(exist_ok=True)
        (test_dir / "security").mkdir(exist_ok=True)

        # Write setup and teardown files
        if test_suite.setup_code:
            setup_file = (
                test_dir / "conftest.py"
                if config.framework == TestFramework.PYTEST
                else test_dir / "setup.py"
            )
            setup_file.write_text(test_suite.setup_code)

        # Write fixtures
        if test_suite.fixtures:
            fixtures_dir = test_dir / "fixtures"
            fixtures_dir.mkdir(exist_ok=True)

            for fixture_name, fixture_content in test_suite.fixtures.items():
                fixture_file = fixtures_dir / f"{fixture_name}.json"
                fixture_file.write_text(fixture_content)

        # Install dependencies if needed
        await self._install_test_dependencies(test_suite, config)

    async def _write_test_files(self, test_suite):
        """Write test files to disk"""

        for test_case in test_suite.test_cases:
            test_file_path = self.project_root / test_case.file_path
            test_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Add imports and setup to test code
            full_test_code = self._prepare_test_code(test_case)

            test_file_path.write_text(full_test_code)
            print(f"Written test file: {test_file_path}")

    def _prepare_test_code(self, test_case) -> str:
        """Prepare complete test code with imports"""

        imports = self._generate_imports(test_case)

        return f"""
{imports}

{test_case.code}
"""

    def _generate_imports(self, test_case) -> str:
        """Generate appropriate imports for test case"""

        base_imports = []

        if test_case.framework == TestFramework.PYTEST:
            base_imports.extend(
                ["import pytest", "from unittest.mock import Mock, patch, MagicMock"]
            )
        elif test_case.framework == TestFramework.UNITTEST:
            base_imports.extend(
                ["import unittest", "from unittest.mock import Mock, patch, MagicMock"]
            )

        # Add test-type specific imports
        if test_case.test_type.value == "api":
            if "fastapi" in test_case.dependencies:
                base_imports.append("from fastapi.testclient import TestClient")
            if "httpx" in test_case.dependencies:
                base_imports.append("import httpx")

        if test_case.test_type.value == "performance":
            base_imports.extend(["import time", "import psutil"])

        if test_case.test_type.value == "security":
            base_imports.extend(["import hashlib", "import secrets"])

        return "\n".join(base_imports)

    async def _install_test_dependencies(
        self, test_suite, config: TestRunConfiguration
    ):
        """Install required test dependencies"""

        all_dependencies = set()

        # Collect dependencies from all test cases
        for test_case in test_suite.test_cases:
            all_dependencies.update(test_case.dependencies)

        # Add framework-specific dependencies
        if config.framework == TestFramework.PYTEST:
            all_dependencies.update(["pytest", "pytest-asyncio", "pytest-mock"])
            if config.coverage:
                all_dependencies.add("pytest-cov")
        elif config.framework == TestFramework.JEST:
            all_dependencies.update(["jest", "@types/jest"])

        # Install dependencies
        if all_dependencies:
            deps_list = list(all_dependencies)
            print(f"Installing dependencies: {deps_list}")

            # For Python packages
            python_deps = [dep for dep in deps_list if not dep.startswith("@")]
            if python_deps:
                cmd = ["pip", "install"] + python_deps
                process = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

    async def _run_pytest(
        self, test_suite, config: TestRunConfiguration
    ) -> Dict[str, Any]:
        """Run tests using pytest"""

        cmd = ["python", "-m", "pytest"]

        # Add test paths
        if config.test_paths:
            cmd.extend(config.test_paths)
        else:
            cmd.append("tests/")

        # Add options
        if config.verbose:
            cmd.append("-v")

        if config.coverage:
            cmd.extend(["--cov=src", "--cov-report=xml", "--cov-report=html"])

        # Add markers
        if config.markers:
            for marker in config.markers:
                cmd.extend(["-m", marker])

        if config.exclude_markers:
            for marker in config.exclude_markers:
                cmd.extend(["-m", f"not {marker}"])

        # Parallel execution
        if config.parallel:
            cmd.extend(["-n", "auto"])

        # Output format
        cmd.extend(["--junit-xml=test_results/junit.xml"])

        # Set working directory
        cwd = str(self.project_root)

        # Set environment
        env = config.environment or {}
        env.update({"PYTHONPATH": str(self.project_root / "src"), "TESTING": "1"})

        print(f"Running command: {' '.join(cmd)}")

        # Execute pytest
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=config.timeout
        )

        return {
            "returncode": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "framework": "pytest",
        }

    async def _run_jest(
        self, test_suite, config: TestRunConfiguration
    ) -> Dict[str, Any]:
        """Run tests using Jest"""

        cmd = ["npm", "test"]

        # Jest configuration
        jest_config = {
            "testEnvironment": "node",
            "coverage": config.coverage,
            "verbose": config.verbose,
            "reporters": ["default", "jest-junit"],
        }

        # Write Jest configuration
        jest_config_file = self.project_root / "jest.config.json"
        jest_config_file.write_text(json.dumps(jest_config, indent=2))

        # Execute Jest
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.project_root),
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=config.timeout
        )

        return {
            "returncode": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "framework": "jest",
        }

    async def _run_unittest(
        self, test_suite, config: TestRunConfiguration
    ) -> Dict[str, Any]:
        """Run tests using unittest"""

        cmd = ["python", "-m", "unittest"]

        if config.verbose:
            cmd.append("-v")

        # Discover tests
        cmd.extend(["discover", "-s", "tests", "-p", "test_*.py"])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.project_root),
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=config.timeout
        )

        return {
            "returncode": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "framework": "unittest",
        }

    async def _parse_test_results(
        self, test_suite, execution_result: Dict[str, Any], duration: float
    ) -> TestSuiteResult:
        """Parse test execution results"""

        if execution_result["framework"] == "pytest":
            return await self._parse_pytest_results(
                test_suite, execution_result, duration
            )
        elif execution_result["framework"] == "jest":
            return await self._parse_jest_results(
                test_suite, execution_result, duration
            )
        elif execution_result["framework"] == "unittest":
            return await self._parse_unittest_results(
                test_suite, execution_result, duration
            )

        # Fallback parsing
        return TestSuiteResult(
            name=test_suite.name,
            total_tests=len(test_suite.test_cases),
            passed=0,
            failed=0,
            skipped=0,
            errors=0,
            duration=duration,
        )

    async def _parse_pytest_results(
        self, test_suite, execution_result: Dict[str, Any], duration: float
    ) -> TestSuiteResult:
        """Parse pytest XML results"""

        junit_file = self.results_dir / "junit.xml"

        if not junit_file.exists():
            # Fallback to stdout parsing
            return self._parse_stdout_results(test_suite, execution_result, duration)

        # Parse XML results
        tree = ET.parse(junit_file)
        root = tree.getroot()

        test_results = []
        total_tests = 0
        passed = 0
        failed = 0
        skipped = 0
        errors = 0

        for testcase in root.findall(".//testcase"):
            total_tests += 1

            name = testcase.get("name", "unknown")
            test_duration = float(testcase.get("time", 0))

            # Determine status
            if testcase.find("failure") is not None:
                status = TestRunStatus.FAILED
                failed += 1
                failure = testcase.find("failure")
                message = failure.get("message", "") if failure is not None else ""
                traceback = failure.text if failure is not None else ""
            elif testcase.find("error") is not None:
                status = TestRunStatus.ERROR
                errors += 1
                error = testcase.find("error")
                message = error.get("message", "") if error is not None else ""
                traceback = error.text if error is not None else ""
            elif testcase.find("skipped") is not None:
                status = TestRunStatus.SKIPPED
                skipped += 1
                skipped_elem = testcase.find("skipped")
                message = (
                    skipped_elem.get("message", "") if skipped_elem is not None else ""
                )
                traceback = None
            else:
                status = TestRunStatus.PASSED
                passed += 1
                message = None
                traceback = None

            test_result = TestResult(
                name=name,
                status=status,
                duration=test_duration,
                message=message,
                traceback=traceback,
            )
            test_results.append(test_result)

        # Parse coverage if available
        coverage_percentage = None
        coverage_file = self.project_root / "coverage.xml"
        if coverage_file.exists():
            coverage_percentage = self._parse_coverage_xml(coverage_file)

        return TestSuiteResult(
            name=test_suite.name,
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=duration,
            coverage_percentage=coverage_percentage,
            test_results=test_results,
        )

    async def _parse_jest_results(
        self, test_suite, execution_result: Dict[str, Any], duration: float
    ) -> TestSuiteResult:
        """Parse Jest JSON results"""

        # Jest outputs JSON to stdout
        try:
            results = json.loads(execution_result["stdout"])

            total_tests = results.get("numTotalTests", 0)
            passed = results.get("numPassedTests", 0)
            failed = results.get("numFailedTests", 0)
            skipped = results.get("numPendingTests", 0)

            return TestSuiteResult(
                name=test_suite.name,
                total_tests=total_tests,
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=0,
                duration=duration,
                coverage_percentage=results.get("coverageMap", {})
                .get("total", {})
                .get("lines", {})
                .get("pct"),
            )

        except json.JSONDecodeError:
            return self._parse_stdout_results(test_suite, execution_result, duration)

    async def _parse_unittest_results(
        self, test_suite, execution_result: Dict[str, Any], duration: float
    ) -> TestSuiteResult:
        """Parse unittest results from stdout"""

        return self._parse_stdout_results(test_suite, execution_result, duration)

    def _parse_stdout_results(
        self, test_suite, execution_result: Dict[str, Any], duration: float
    ) -> TestSuiteResult:
        """Parse results from stdout as fallback"""

        stdout = execution_result["stdout"]

        # Basic parsing - this could be enhanced
        total_tests = len(test_suite.test_cases)

        # Simple heuristics
        if "FAILED" in stdout or execution_result["returncode"] != 0:
            failed = 1
            passed = total_tests - 1
        else:
            failed = 0
            passed = total_tests

        return TestSuiteResult(
            name=test_suite.name,
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=0,
            errors=0,
            duration=duration,
        )

    def _parse_coverage_xml(self, coverage_file: Path) -> Optional[float]:
        """Parse coverage from XML file"""

        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()

            # Find overall coverage
            coverage = root.get("line-rate")
            if coverage:
                return float(coverage) * 100

        except Exception as e:
            print(f"Error parsing coverage: {e}")

        return None

    async def _generate_test_report(
        self, suite_result: TestSuiteResult, config: TestRunConfiguration
    ):
        """Generate comprehensive test report"""

        # Generate HTML report
        html_report = self._generate_html_report(suite_result, config)
        html_file = self.results_dir / "test_report.html"
        html_file.write_text(html_report)

        # Generate JSON report
        json_report = self._generate_json_report(suite_result, config)
        json_file = self.results_dir / "test_report.json"
        json_file.write_text(json_report)

        # Generate summary
        summary = self._generate_summary_report(suite_result)
        summary_file = self.results_dir / "test_summary.txt"
        summary_file.write_text(summary)

        print(f"Test reports generated in: {self.results_dir}")

    def _generate_html_report(
        self, suite_result: TestSuiteResult, config: TestRunConfiguration
    ) -> str:
        """Generate HTML test report"""

        success_rate = (
            (suite_result.passed / suite_result.total_tests * 100)
            if suite_result.total_tests > 0
            else 0
        )

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {suite_result.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; text-align: center; }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .test-results {{ margin: 20px 0; }}
        .test-case {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .test-case.passed {{ border-left-color: #28a745; }}
        .test-case.failed {{ border-left-color: #dc3545; }}
        .test-case.skipped {{ border-left-color: #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Report: {suite_result.name}</h1>
        <p>Framework: {config.framework.value}</p>
        <p>Execution Time: {suite_result.duration:.2f} seconds</p>
        <p>Success Rate: {success_rate:.1f}%</p>
    </div>
    
    <div class="metrics">
        <div class="metric passed">
            <h3>{suite_result.passed}</h3>
            <p>Passed</p>
        </div>
        <div class="metric failed">
            <h3>{suite_result.failed}</h3>
            <p>Failed</p>
        </div>
        <div class="metric">
            <h3>{suite_result.skipped}</h3>
            <p>Skipped</p>
        </div>
        <div class="metric">
            <h3>{suite_result.total_tests}</h3>
            <p>Total</p>
        </div>
        {f'<div class="metric"><h3>{suite_result.coverage_percentage:.1f}%</h3><p>Coverage</p></div>' if suite_result.coverage_percentage else ''}
    </div>
    
    <div class="test-results">
        <h2>Test Results</h2>
        {''.join(self._generate_test_case_html(test) for test in (suite_result.test_results or []))}
    </div>
</body>
</html>
"""
        return html

    def _generate_test_case_html(self, test_result: TestResult) -> str:
        """Generate HTML for individual test case"""

        status_class = test_result.status.value

        return f"""
        <div class="test-case {status_class}">
            <h4>{test_result.name}</h4>
            <p>Status: {test_result.status.value.upper()}</p>
            <p>Duration: {test_result.duration:.3f}s</p>
            {f'<p>Message: {test_result.message}</p>' if test_result.message else ''}
            {f'<pre>{test_result.traceback}</pre>' if test_result.traceback else ''}
        </div>
        """

    def _generate_json_report(
        self, suite_result: TestSuiteResult, config: TestRunConfiguration
    ) -> str:
        """Generate JSON test report"""

        report = {
            "suite_name": suite_result.name,
            "framework": config.framework.value,
            "summary": {
                "total_tests": suite_result.total_tests,
                "passed": suite_result.passed,
                "failed": suite_result.failed,
                "skipped": suite_result.skipped,
                "errors": suite_result.errors,
                "duration": suite_result.duration,
                "success_rate": (
                    (suite_result.passed / suite_result.total_tests * 100)
                    if suite_result.total_tests > 0
                    else 0
                ),
                "coverage_percentage": suite_result.coverage_percentage,
            },
            "test_results": [
                asdict(test) for test in (suite_result.test_results or [])
            ],
        }

        return json.dumps(report, indent=2, default=str)

    def _generate_summary_report(self, suite_result: TestSuiteResult) -> str:
        """Generate text summary report"""

        success_rate = (
            (suite_result.passed / suite_result.total_tests * 100)
            if suite_result.total_tests > 0
            else 0
        )

        summary = f"""
Test Suite: {suite_result.name}
{'=' * 50}

Summary:
  Total Tests: {suite_result.total_tests}
  Passed: {suite_result.passed}
  Failed: {suite_result.failed}
  Skipped: {suite_result.skipped}
  Errors: {suite_result.errors}
  
  Duration: {suite_result.duration:.2f} seconds
  Success Rate: {success_rate:.1f}%
  {'Coverage: ' + str(suite_result.coverage_percentage) + '%' if suite_result.coverage_percentage else ''}

Status: {'PASSED' if suite_result.failed == 0 and suite_result.errors == 0 else 'FAILED'}
"""

        return summary
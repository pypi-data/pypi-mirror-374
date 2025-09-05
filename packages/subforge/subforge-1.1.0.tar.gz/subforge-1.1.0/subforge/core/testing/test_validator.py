"""
Test Validation System
Validates generated tests for quality, coverage, and compliance
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ValidationLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    severity: ValidationSeverity
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    rule_id: str = None


@dataclass
class ValidationResult:
    passed: bool
    score: float  # 0.0 to 1.0
    issues: List[ValidationIssue]
    metrics: Dict[str, Any]
    recommendations: List[str]


class TestValidator:
    """
    Comprehensive test validation system that ensures generated tests
    meet quality standards and best practices
    """

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        self.rules = self._initialize_validation_rules()

    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules based on level"""
        base_rules = {
            "naming_conventions": {
                "test_function_prefix": "test_",
                "test_class_prefix": "Test",
                "descriptive_names": True,
            },
            "structure_requirements": {
                "arrange_act_assert": True,
                "single_assertion_per_test": False,
                "test_isolation": True,
            },
            "coverage_requirements": {
                "min_assertion_count": 1,
                "error_case_coverage": True,
                "edge_case_coverage": True,
            },
            "quality_metrics": {
                "max_test_length": 50,  # lines
                "max_complexity": 5,
                "documentation_required": True,
            },
        }

        if self.validation_level == ValidationLevel.COMPREHENSIVE:
            base_rules.update(
                {
                    "advanced_patterns": {
                        "mock_usage_validation": True,
                        "fixture_optimization": True,
                        "parameterized_tests": True,
                    },
                    "performance_requirements": {
                        "test_execution_time": 1.0,  # seconds
                        "setup_teardown_efficiency": True,
                    },
                    "security_validation": {
                        "sensitive_data_exposure": True,
                        "credential_hardcoding": True,
                    },
                }
            )

        return base_rules

    def validate_test_suite(self, test_suite) -> ValidationResult:
        """
        Validate an entire test suite
        """
        all_issues = []
        metrics = {}
        recommendations = []

        # Validate each test case
        test_scores = []
        for test_case in test_suite.test_cases:
            result = self.validate_test_case(test_case)
            all_issues.extend(result.issues)
            test_scores.append(result.score)

        # Suite-level validations
        suite_issues, suite_metrics = self._validate_suite_structure(test_suite)
        all_issues.extend(suite_issues)
        metrics.update(suite_metrics)

        # Calculate overall score
        overall_score = sum(test_scores) / len(test_scores) if test_scores else 0.0

        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues, metrics)

        # Determine pass/fail
        critical_issues = [
            issue
            for issue in all_issues
            if issue.severity == ValidationSeverity.CRITICAL
        ]
        error_issues = [
            issue for issue in all_issues if issue.severity == ValidationSeverity.ERROR
        ]

        passed = len(critical_issues) == 0 and len(error_issues) == 0

        return ValidationResult(
            passed=passed,
            score=overall_score,
            issues=all_issues,
            metrics=metrics,
            recommendations=recommendations,
        )

    def validate_test_case(self, test_case) -> ValidationResult:
        """
        Validate a single test case
        """
        issues = []
        metrics = {}

        # Parse the test code
        try:
            tree = ast.parse(test_case.code)
            metrics["ast_nodes"] = len(list(ast.walk(tree)))
        except SyntaxError as e:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Syntax error in test code: {str(e)}",
                    line_number=getattr(e, "lineno", None),
                    rule_id="SYNTAX_ERROR",
                )
            )
            return ValidationResult(
                passed=False,
                score=0.0,
                issues=issues,
                metrics=metrics,
                recommendations=["Fix syntax errors before proceeding"],
            )

        # Validate naming conventions
        issues.extend(self._validate_naming_conventions(test_case, tree))

        # Validate structure
        issues.extend(self._validate_test_structure(test_case, tree))

        # Validate assertions
        assertion_issues, assertion_metrics = self._validate_assertions(test_case, tree)
        issues.extend(assertion_issues)
        metrics.update(assertion_metrics)

        # Validate documentation
        issues.extend(self._validate_documentation(test_case, tree))

        # Advanced validations for comprehensive level
        if self.validation_level == ValidationLevel.COMPREHENSIVE:
            issues.extend(self._validate_advanced_patterns(test_case, tree))
            issues.extend(self._validate_security_concerns(test_case, tree))

        # Calculate score
        score = self._calculate_test_score(issues, metrics)

        # Generate recommendations
        recommendations = self._generate_test_recommendations(issues, test_case)

        passed = all(
            issue.severity
            not in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
            for issue in issues
        )

        return ValidationResult(
            passed=passed,
            score=score,
            issues=issues,
            metrics=metrics,
            recommendations=recommendations,
        )

    def _validate_naming_conventions(self, test_case, tree) -> List[ValidationIssue]:
        """Validate naming conventions"""
        issues = []

        # Check test function names
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("test_"):
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Test function '{node.name}' should start with 'test_'",
                            line_number=node.lineno,
                            suggestion=f"Rename to 'test_{node.name}'",
                            rule_id="NAMING_TEST_FUNCTION",
                        )
                    )

                # Check for descriptive names
                if len(node.name) < 10:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message=f"Test function name '{node.name}' should be more descriptive",
                            line_number=node.lineno,
                            suggestion="Use descriptive names that explain what is being tested",
                            rule_id="NAMING_DESCRIPTIVE",
                        )
                    )

            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("Test"):
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Test class '{node.name}' should start with 'Test'",
                            line_number=node.lineno,
                            suggestion=f"Rename to 'Test{node.name}'",
                            rule_id="NAMING_TEST_CLASS",
                        )
                    )

        return issues

    def _validate_test_structure(self, test_case, tree) -> List[ValidationIssue]:
        """Validate test structure and organization"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                # Check for AAA pattern (Arrange, Act, Assert)
                comments = self._extract_comments(
                    test_case.code, node.lineno, node.end_lineno
                )
                has_aaa_comments = any(
                    comment.lower().strip() in ["# arrange", "# act", "# assert"]
                    for comment in comments
                )

                if (
                    not has_aaa_comments
                    and self.validation_level == ValidationLevel.COMPREHENSIVE
                ):
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message=f"Test function '{node.name}' should follow AAA pattern",
                            line_number=node.lineno,
                            suggestion="Add # Arrange, # Act, # Assert comments",
                            rule_id="STRUCTURE_AAA",
                        )
                    )

                # Check test length
                test_length = node.end_lineno - node.lineno
                if test_length > self.rules["quality_metrics"]["max_test_length"]:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message=f"Test function '{node.name}' is too long ({test_length} lines)",
                            line_number=node.lineno,
                            suggestion="Consider breaking into smaller, focused tests",
                            rule_id="STRUCTURE_LENGTH",
                        )
                    )

        return issues

    def _validate_assertions(
        self, test_case, tree
    ) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate assertions in test code"""
        issues = []
        metrics = {}

        assertion_count = 0
        assertion_types = set()

        for node in ast.walk(tree):
            # Count assert statements
            if isinstance(node, ast.Assert):
                assertion_count += 1
                assertion_types.add("assert")

            # Count pytest assertions
            elif isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Attribute)
                    and hasattr(node.func, "attr")
                    and node.func.attr.startswith("assert")
                ):
                    assertion_count += 1
                    assertion_types.add("pytest")

        metrics["assertion_count"] = assertion_count
        metrics["assertion_types"] = list(assertion_types)

        # Validate minimum assertion count
        min_assertions = self.rules["coverage_requirements"]["min_assertion_count"]
        if assertion_count < min_assertions:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Test has {assertion_count} assertions, minimum is {min_assertions}",
                    suggestion="Add appropriate assertions to verify test results",
                    rule_id="ASSERTION_COUNT",
                )
            )

        # Check for meaningful assertions
        if assertion_count == 0:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    message="Test has no assertions - it doesn't verify anything",
                    suggestion="Add assertions to verify expected behavior",
                    rule_id="ASSERTION_MISSING",
                )
            )

        return issues, metrics

    def _validate_documentation(self, test_case, tree) -> List[ValidationIssue]:
        """Validate test documentation"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                # Check for docstring
                if not ast.get_docstring(node):
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message=f"Test function '{node.name}' missing docstring",
                            line_number=node.lineno,
                            suggestion="Add docstring explaining what the test verifies",
                            rule_id="DOC_MISSING_DOCSTRING",
                        )
                    )

        return issues

    def _validate_advanced_patterns(self, test_case, tree) -> List[ValidationIssue]:
        """Validate advanced testing patterns"""
        issues = []

        # Check for proper mock usage
        mock_imports = []
        mock_usage = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "mock" in node.module:
                    mock_imports.extend([alias.name for alias in node.names])

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in mock_imports:
                    mock_usage.append(node.func.id)

        # Validate mock usage patterns
        if mock_imports and not mock_usage:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Mock imported but not used in test",
                    suggestion="Remove unused mock import or use mocks appropriately",
                    rule_id="MOCK_UNUSED",
                )
            )

        return issues

    def _validate_security_concerns(self, test_case, tree) -> List[ValidationIssue]:
        """Validate security concerns in test code"""
        issues = []

        # Check for hardcoded credentials
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        for pattern in sensitive_patterns:
            matches = re.findall(pattern, test_case.code, re.IGNORECASE)
            if matches:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Potential hardcoded credential found: {matches[0][:20]}...",
                        suggestion="Use environment variables or test fixtures for credentials",
                        rule_id="SECURITY_HARDCODED_CREDS",
                    )
                )

        return issues

    def _validate_suite_structure(
        self, test_suite
    ) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate overall test suite structure"""
        issues = []
        metrics = {}

        # Check test type distribution
        test_types = {}
        for test_case in test_suite.test_cases:
            test_type = test_case.test_type.value
            test_types[test_type] = test_types.get(test_type, 0) + 1

        metrics["test_type_distribution"] = test_types

        # Validate minimum test types
        required_types = ["unit", "integration"]
        missing_types = [t for t in required_types if t not in test_types]

        if missing_types:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Missing test types: {', '.join(missing_types)}",
                    suggestion="Consider adding tests for missing types",
                    rule_id="SUITE_COVERAGE",
                )
            )

        # Check for setup/teardown
        if not test_suite.setup_code:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message="No setup code defined for test suite",
                    suggestion="Consider adding setup code for test initialization",
                    rule_id="SUITE_SETUP",
                )
            )

        return issues, metrics

    def _calculate_test_score(
        self, issues: List[ValidationIssue], metrics: Dict[str, Any]
    ) -> float:
        """Calculate quality score for a test"""
        base_score = 1.0

        # Deduct points for issues
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 0.5
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 0.3
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 0.1
            # INFO issues don't deduct points

        # Bonus points for good practices
        assertion_count = metrics.get("assertion_count", 0)
        if assertion_count > 1:
            base_score += 0.1

        return max(0.0, min(1.0, base_score))

    def _generate_recommendations(
        self, issues: List[ValidationIssue], metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Count issues by severity
        issue_counts = {}
        for issue in issues:
            severity = issue.severity.value
            issue_counts[severity] = issue_counts.get(severity, 0) + 1

        if issue_counts.get("critical", 0) > 0:
            recommendations.append(
                "Fix critical issues immediately - tests may not run"
            )

        if issue_counts.get("error", 0) > 0:
            recommendations.append(
                "Address error-level issues to improve test reliability"
            )

        if issue_counts.get("warning", 0) > 3:
            recommendations.append(
                "Consider addressing warning issues to improve code quality"
            )

        # Specific recommendations based on metrics
        test_distribution = metrics.get("test_type_distribution", {})
        total_tests = sum(test_distribution.values())

        if total_tests > 0:
            unit_percentage = (test_distribution.get("unit", 0) / total_tests) * 100
            if unit_percentage < 60:
                recommendations.append(
                    "Increase unit test coverage - aim for 60-80% unit tests"
                )

        return recommendations

    def _generate_test_recommendations(
        self, issues: List[ValidationIssue], test_case
    ) -> List[str]:
        """Generate recommendations for a specific test case"""
        recommendations = []

        issue_types = {issue.rule_id for issue in issues}

        if "ASSERTION_COUNT" in issue_types or "ASSERTION_MISSING" in issue_types:
            recommendations.append(
                "Add more comprehensive assertions to verify behavior"
            )

        if "NAMING_DESCRIPTIVE" in issue_types:
            recommendations.append(
                "Use more descriptive test names that explain the scenario"
            )

        if "STRUCTURE_LENGTH" in issue_types:
            recommendations.append("Break long tests into smaller, focused test cases")

        if "DOC_MISSING_DOCSTRING" in issue_types:
            recommendations.append(
                "Add docstrings to explain test purpose and expected outcomes"
            )

        return recommendations

    def _extract_comments(self, code: str, start_line: int, end_line: int) -> List[str]:
        """Extract comments from code section"""
        lines = code.split("\n")
        comments = []

        for i in range(max(0, start_line - 1), min(len(lines), end_line)):
            line = lines[i].strip()
            if line.startswith("#"):
                comments.append(line)

        return comments
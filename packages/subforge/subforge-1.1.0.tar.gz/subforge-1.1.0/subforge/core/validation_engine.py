#!/usr/bin/env python3
"""
SubForge Validation Engine
Comprehensive validation system for generated configurations
"""

import json
import re
import tempfile
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class ValidationLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class ValidatorType(Enum):
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    SECURITY = "security"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"


@dataclass
class ValidationResult:
    """Result from a single validation check"""

    validator_name: str
    validator_type: ValidatorType
    level: ValidationLevel
    message: str
    details: Optional[str]
    file_path: Optional[str]
    line_number: Optional[int]
    suggestion: Optional[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ValidationReport:
    """Complete validation report for a configuration"""

    configuration_id: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    critical_issues: int
    results: List[ValidationResult]
    deployment_ready: bool
    overall_score: float
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "results": [result.to_dict() for result in self.results],
        }

    def add_result(self, result: ValidationResult):
        """Add a validation result to the report"""
        self.results.append(result)
        self.total_checks += 1

        if result.level == ValidationLevel.SUCCESS:
            self.passed_checks += 1
        elif result.level == ValidationLevel.WARNING:
            self.warning_checks += 1
        elif result.level == ValidationLevel.CRITICAL:
            self.failed_checks += 1
            self.critical_issues += 1
        else:
            self.failed_checks += 1

    def calculate_score(self):
        """Calculate overall validation score (0-100)"""
        if self.total_checks == 0:
            self.overall_score = 0.0
            return

        # Weight different levels
        score = 0.0
        score += self.passed_checks * 1.0
        score += self.warning_checks * 0.7
        score -= self.critical_issues * 2.0
        score -= (self.failed_checks - self.critical_issues) * 1.0

        # Normalize to 0-100
        max_score = self.total_checks * 1.0
        self.overall_score = max(0.0, min(100.0, (score / max_score) * 100))

        # Determine deployment readiness
        self.deployment_ready = self.critical_issues == 0 and self.overall_score >= 70.0


class BaseValidator:
    """Base class for all validators"""

    def __init__(self, name: str, validator_type: ValidatorType):
        self.name = name
        self.validator_type = validator_type

    def validate(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate configuration and return results"""
        raise NotImplementedError


class SyntaxValidator(BaseValidator):
    """Validates syntax of generated files"""

    def __init__(self):
        super().__init__("Syntax Validator", ValidatorType.SYNTAX)

    def validate(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate syntax of all generated files"""
        results = []

        # Check generated configurations
        generated_configs = context.get("generated_configurations", {})

        for generator_name, config in generated_configs.items():
            if isinstance(config, dict):
                # Validate CLAUDE.md content
                if "claude_md_content" in config:
                    results.extend(
                        self._validate_claude_md_syntax(
                            config["claude_md_content"], generator_name
                        )
                    )

                # Validate YAML configurations
                if "workflows" in config:
                    results.extend(
                        self._validate_yaml_syntax(
                            config["workflows"], f"{generator_name}_workflows"
                        )
                    )

        return results

    def _validate_claude_md_syntax(
        self, content: str, source: str
    ) -> List[ValidationResult]:
        """Validate CLAUDE.md markdown syntax"""
        results = []
        lines = content.split("\n")

        # Check for required sections
        required_sections = [
            "## Project Overview",
            "## Available Subagents",
            "## Development Guidelines",
        ]
        found_sections = []

        for line in lines:
            if line.strip().startswith("## "):
                found_sections.append(line.strip())

        for section in required_sections:
            if section in found_sections:
                results.append(
                    ValidationResult(
                        validator_name=self.name,
                        validator_type=self.validator_type,
                        level=ValidationLevel.SUCCESS,
                        message=f"Required section '{section}' found",
                        details=None,
                        file_path=f"{source}.md",
                        line_number=None,
                        suggestion=None,
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        validator_name=self.name,
                        validator_type=self.validator_type,
                        level=ValidationLevel.WARNING,
                        message=f"Missing recommended section '{section}'",
                        details="CLAUDE.md files should include standard sections for consistency",
                        file_path=f"{source}.md",
                        line_number=None,
                        suggestion=f"Add '{section}' section to improve clarity",
                    )
                )

        # Check for malformed markdown
        for i, line in enumerate(lines, 1):
            # Check for unbalanced code blocks
            if line.strip().startswith("```") and line.count("```") % 2 != 0:
                code_block_count = content[: content.find(line)].count("```")
                if code_block_count % 2 == 0:  # Opening block
                    # Find matching close
                    remaining_content = "\n".join(lines[i:])
                    if "```" not in remaining_content:
                        results.append(
                            ValidationResult(
                                validator_name=self.name,
                                validator_type=self.validator_type,
                                level=ValidationLevel.CRITICAL,
                                message="Unclosed code block detected",
                                details="Code block opened but never closed",
                                file_path=f"{source}.md",
                                line_number=i,
                                suggestion="Add closing ``` to complete the code block",
                            )
                        )

        return results

    def _validate_yaml_syntax(self, data: Any, source: str) -> List[ValidationResult]:
        """Validate YAML syntax"""
        results = []

        try:
            if isinstance(data, str):
                yaml.safe_load(data)
            elif isinstance(data, (list, dict)):
                yaml.safe_dump(data)

            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.SUCCESS,
                    message="Valid YAML syntax",
                    details=None,
                    file_path=f"{source}.yaml",
                    line_number=None,
                    suggestion=None,
                )
            )

        except yaml.YAMLError as e:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.CRITICAL,
                    message="Invalid YAML syntax",
                    details=str(e),
                    file_path=f"{source}.yaml",
                    line_number=getattr(e, "problem_mark", None),
                    suggestion="Fix YAML syntax errors",
                )
            )

        return results


class SemanticValidator(BaseValidator):
    """Validates semantic correctness of configurations"""

    def __init__(self):
        super().__init__("Semantic Validator", ValidatorType.SEMANTIC)

    def validate(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate semantic correctness"""
        results = []

        # Validate subagent consistency
        results.extend(self._validate_subagent_consistency(configuration, context))

        # Validate workflow logic
        results.extend(self._validate_workflow_logic(configuration, context))

        # Validate tool permissions
        results.extend(self._validate_tool_permissions(configuration, context))

        return results

    def _validate_subagent_consistency(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate that subagents are consistent with project needs"""
        results = []

        project_profile = context.get("project_profile")
        selected_templates = context.get("template_selections", {}).get(
            "selected_templates", []
        )

        if not project_profile or not selected_templates:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.WARNING,
                    message="Insufficient data for semantic validation",
                    details="Missing project profile or template selections",
                    file_path=None,
                    line_number=None,
                    suggestion="Ensure project analysis and template selection completed successfully",
                )
            )
            return results

        # Check if selected subagents match project characteristics
        tech_stack = project_profile.get("technology_stack", {})
        languages = tech_stack.get("languages", [])
        frameworks = tech_stack.get("frameworks", [])

        # Frontend development check
        has_frontend_tech = any(
            lang in ["javascript", "typescript", "html", "css"] for lang in languages
        ) or any(fw in ["react", "vue", "angular", "svelte"] for fw in frameworks)
        has_frontend_agent = "frontend-developer" in selected_templates

        if has_frontend_tech and not has_frontend_agent:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.WARNING,
                    message="Frontend technology detected but no frontend developer subagent",
                    details=f"Project uses frontend technologies: {', '.join(lang for lang in languages if lang in ['javascript', 'typescript', 'html', 'css'])}",
                    file_path=None,
                    line_number=None,
                    suggestion="Consider adding frontend-developer subagent",
                )
            )
        elif not has_frontend_tech and has_frontend_agent:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.INFO,
                    message="Frontend developer subagent selected for non-frontend project",
                    details="This may be intentional for future frontend development",
                    file_path=None,
                    line_number=None,
                    suggestion=None,
                )
            )
        else:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.SUCCESS,
                    message="Frontend subagent selection matches project needs",
                    details=None,
                    file_path=None,
                    line_number=None,
                    suggestion=None,
                )
            )

        # Backend development check
        has_backend_tech = (
            any(
                fw in ["express", "fastapi", "django", "flask", "spring", "rails"]
                for fw in frameworks
            )
            or "python" in languages
            or "java" in languages
            or "go" in languages
        )
        has_backend_agent = "backend-developer" in selected_templates

        if has_backend_tech and not has_backend_agent:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.WARNING,
                    message="Backend technology detected but no backend developer subagent",
                    details=f"Project uses backend technologies: {', '.join(frameworks)}",
                    file_path=None,
                    line_number=None,
                    suggestion="Consider adding backend-developer subagent",
                )
            )
        elif has_backend_tech and has_backend_agent:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.SUCCESS,
                    message="Backend subagent selection matches project needs",
                    details=None,
                    file_path=None,
                    line_number=None,
                    suggestion=None,
                )
            )

        return results

    def _validate_workflow_logic(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate workflow logic and dependencies"""
        results = []

        generated_configs = context.get("generated_configurations", {})
        workflow_config = generated_configs.get("workflow-generator", {})

        if "workflows" in workflow_config:
            workflows = workflow_config["workflows"]

            for workflow in workflows:
                if isinstance(workflow, dict):
                    name = workflow.get("name", "Unknown")
                    steps = workflow.get("steps", [])

                    # Check for logical step ordering
                    if "test" in steps and "implement" in steps:
                        test_idx = steps.index("test")
                        impl_idx = steps.index("implement")

                        if test_idx < impl_idx:
                            results.append(
                                ValidationResult(
                                    validator_name=self.name,
                                    validator_type=self.validator_type,
                                    level=ValidationLevel.WARNING,
                                    message=f"Workflow '{name}' has test before implementation",
                                    details="Testing should typically come after implementation",
                                    file_path="workflows.yaml",
                                    line_number=None,
                                    suggestion="Consider reordering steps: implement → test",
                                )
                            )
                        else:
                            results.append(
                                ValidationResult(
                                    validator_name=self.name,
                                    validator_type=self.validator_type,
                                    level=ValidationLevel.SUCCESS,
                                    message=f"Workflow '{name}' has logical step ordering",
                                    details=None,
                                    file_path="workflows.yaml",
                                    line_number=None,
                                    suggestion=None,
                                )
                            )

        return results

    def _validate_tool_permissions(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate tool permissions are appropriate"""
        results = []

        generated_configs = context.get("generated_configurations", {})
        agent_config = generated_configs.get("agent-generator", {})

        if "generated_agents" in agent_config:
            agents = agent_config["generated_agents"]

            for agent in agents:
                if isinstance(agent, dict):
                    name = agent.get("name", "Unknown")
                    tools = agent.get("tools", [])

                    # Check for appropriate tool permissions
                    if name == "frontend-developer":
                        if "bash" not in tools:
                            results.append(
                                ValidationResult(
                                    validator_name=self.name,
                                    validator_type=self.validator_type,
                                    level=ValidationLevel.WARNING,
                                    message="Frontend developer missing bash tool",
                                    details="Frontend developers often need bash for build tools",
                                    file_path="agents.yaml",
                                    line_number=None,
                                    suggestion="Consider adding 'bash' to tools list",
                                )
                            )

                    # Check for excessive permissions
                    if len(tools) > 8:
                        results.append(
                            ValidationResult(
                                validator_name=self.name,
                                validator_type=self.validator_type,
                                level=ValidationLevel.INFO,
                                message=f"Agent '{name}' has many tool permissions ({len(tools)})",
                                details="Consider if all tools are necessary for this agent's role",
                                file_path="agents.yaml",
                                line_number=None,
                                suggestion="Review tool permissions for security best practices",
                            )
                        )

                    # Success case
                    if 3 <= len(tools) <= 6:
                        results.append(
                            ValidationResult(
                                validator_name=self.name,
                                validator_type=self.validator_type,
                                level=ValidationLevel.SUCCESS,
                                message=f"Agent '{name}' has appropriate tool permissions",
                                details=f"Tools: {', '.join(tools)}",
                                file_path="agents.yaml",
                                line_number=None,
                                suggestion=None,
                            )
                        )

        return results


class SecurityValidator(BaseValidator):
    """Validates security aspects of configurations"""

    def __init__(self):
        super().__init__("Security Validator", ValidatorType.SECURITY)

    def validate(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate security aspects"""
        results = []

        # Check for sensitive data exposure
        results.extend(self._check_sensitive_data_exposure(configuration, context))

        # Validate tool permissions security
        results.extend(self._validate_tool_security(configuration, context))

        # Check for insecure patterns
        results.extend(self._check_insecure_patterns(configuration, context))

        return results

    def _check_sensitive_data_exposure(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Check for potential sensitive data exposure"""
        results = []

        # Patterns that might indicate sensitive data
        sensitive_patterns = [
            r'password\s*[=:]\s*["\'].*["\']',
            r'api[_-]?key\s*[=:]\s*["\'].*["\']',
            r'secret\s*[=:]\s*["\'].*["\']',
            r'token\s*[=:]\s*["\'].*["\']',
            r"private[_-]?key",
            r"[a-zA-Z0-9]{32,}",  # Long strings that might be tokens
        ]

        # Check all generated content
        generated_configs = context.get("generated_configurations", {})

        for generator_name, config in generated_configs.items():
            if isinstance(config, dict):
                content_str = json.dumps(config, indent=2)

                for pattern in sensitive_patterns:
                    matches = re.finditer(pattern, content_str, re.IGNORECASE)
                    for match in matches:
                        # Skip obviously safe patterns
                        if any(
                            safe in match.group().lower()
                            for safe in ["example", "placeholder", "your_", "xxx"]
                        ):
                            continue

                        results.append(
                            ValidationResult(
                                validator_name=self.name,
                                validator_type=self.validator_type,
                                level=ValidationLevel.WARNING,
                                message="Potential sensitive data found in configuration",
                                details=f"Pattern '{pattern}' matched in {generator_name}",
                                file_path=f"{generator_name}.json",
                                line_number=None,
                                suggestion="Review and remove any actual sensitive data, use placeholders instead",
                            )
                        )

        if not any(result.level == ValidationLevel.WARNING for result in results):
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.SUCCESS,
                    message="No sensitive data patterns detected",
                    details=None,
                    file_path=None,
                    line_number=None,
                    suggestion=None,
                )
            )

        return results

    def _validate_tool_security(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate security of tool permissions"""
        results = []

        # High-risk tools that should be used carefully
        high_risk_tools = ["bash", "shell", "exec", "eval"]

        generated_configs = context.get("generated_configurations", {})
        agent_config = generated_configs.get("agent-generator", {})

        if "generated_agents" in agent_config:
            agents = agent_config["generated_agents"]

            for agent in agents:
                if isinstance(agent, dict):
                    name = agent.get("name", "Unknown")
                    tools = agent.get("tools", [])

                    # Check for high-risk tools
                    risky_tools = [tool for tool in tools if tool in high_risk_tools]

                    if risky_tools:
                        results.append(
                            ValidationResult(
                                validator_name=self.name,
                                validator_type=self.validator_type,
                                level=ValidationLevel.INFO,
                                message=f"Agent '{name}' has high-risk tool permissions",
                                details=f"High-risk tools: {', '.join(risky_tools)}",
                                file_path="agents.yaml",
                                line_number=None,
                                suggestion="Ensure these tools are necessary for the agent's function",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                validator_name=self.name,
                                validator_type=self.validator_type,
                                level=ValidationLevel.SUCCESS,
                                message=f"Agent '{name}' has safe tool permissions",
                                details=f"Tools: {', '.join(tools)}",
                                file_path="agents.yaml",
                                line_number=None,
                                suggestion=None,
                            )
                        )

        return results

    def _check_insecure_patterns(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Check for insecure configuration patterns"""
        results = []

        # Check for overly permissive configurations
        generated_configs = context.get("generated_configurations", {})

        # Look for patterns that might be insecure
        insecure_patterns = [
            "eval(",
            "exec(",
            "shell=True",
            "trust=True",
            "verify=False",
            "ssl_verify=False",
        ]

        found_insecure = False
        for generator_name, config in generated_configs.items():
            if isinstance(config, dict):
                content_str = json.dumps(config, indent=2)

                for pattern in insecure_patterns:
                    if pattern in content_str:
                        found_insecure = True
                        results.append(
                            ValidationResult(
                                validator_name=self.name,
                                validator_type=self.validator_type,
                                level=ValidationLevel.WARNING,
                                message=f"Potentially insecure pattern found: '{pattern}'",
                                details=f"Found in {generator_name} configuration",
                                file_path=f"{generator_name}.json",
                                line_number=None,
                                suggestion="Review this pattern for security implications",
                            )
                        )

        if not found_insecure:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.SUCCESS,
                    message="No insecure patterns detected",
                    details=None,
                    file_path=None,
                    line_number=None,
                    suggestion=None,
                )
            )

        return results


class IntegrationValidator(BaseValidator):
    """Validates integration between components"""

    def __init__(self):
        super().__init__("Integration Validator", ValidatorType.INTEGRATION)

    def validate(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate component integration"""
        results = []

        # Check subagent compatibility
        results.extend(self._validate_subagent_compatibility(configuration, context))

        # Check workflow integration
        results.extend(self._validate_workflow_integration(configuration, context))

        return results

    def _validate_subagent_compatibility(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate that subagents work well together"""
        results = []

        selected_templates = context.get("template_selections", {}).get(
            "selected_templates", []
        )

        if len(selected_templates) < 2:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.INFO,
                    message="Single subagent configuration",
                    details="Only one subagent selected - integration checks limited",
                    file_path=None,
                    line_number=None,
                    suggestion=None,
                )
            )
            return results

        # Check for complementary pairs
        complementary_pairs = [
            ("frontend-developer", "backend-developer"),
            ("backend-developer", "database-specialist"),
            ("devops-engineer", "security-auditor"),
            ("test-engineer", "code-reviewer"),
        ]

        found_pairs = []
        for pair in complementary_pairs:
            if pair[0] in selected_templates and pair[1] in selected_templates:
                found_pairs.append(pair)
                results.append(
                    ValidationResult(
                        validator_name=self.name,
                        validator_type=self.validator_type,
                        level=ValidationLevel.SUCCESS,
                        message=f"Complementary subagent pair found: {pair[0]} + {pair[1]}",
                        details="These subagents work well together",
                        file_path=None,
                        line_number=None,
                        suggestion=None,
                    )
                )

        # Check for essential subagents
        if "code-reviewer" not in selected_templates:
            results.append(
                ValidationResult(
                    validator_name=self.name,
                    validator_type=self.validator_type,
                    level=ValidationLevel.WARNING,
                    message="No code reviewer subagent selected",
                    details="Code reviewer is recommended for all projects",
                    file_path=None,
                    line_number=None,
                    suggestion="Consider adding code-reviewer subagent",
                )
            )

        return results

    def _validate_workflow_integration(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate workflow integration with subagents"""
        results = []

        generated_configs = context.get("generated_configurations", {})
        workflow_config = generated_configs.get("workflow-generator", {})
        selected_templates = context.get("template_selections", {}).get(
            "selected_templates", []
        )

        if "commands" in workflow_config:
            commands = workflow_config["commands"]

            # Check if commands align with available subagents
            for command, description in commands.items():
                # Extract potential subagent references
                if (
                    "review" in command.lower()
                    and "code-reviewer" not in selected_templates
                ):
                    results.append(
                        ValidationResult(
                            validator_name=self.name,
                            validator_type=self.validator_type,
                            level=ValidationLevel.WARNING,
                            message=f"Command '{command}' references review but no code-reviewer subagent",
                            details="Command may not work as expected",
                            file_path="workflows.yaml",
                            line_number=None,
                            suggestion="Add code-reviewer subagent or modify command",
                        )
                    )
                elif (
                    "deploy" in command.lower()
                    and "devops-engineer" not in selected_templates
                ):
                    results.append(
                        ValidationResult(
                            validator_name=self.name,
                            validator_type=self.validator_type,
                            level=ValidationLevel.WARNING,
                            message=f"Command '{command}' references deployment but no devops-engineer subagent",
                            details="Command may not work as expected",
                            file_path="workflows.yaml",
                            line_number=None,
                            suggestion="Add devops-engineer subagent or modify command",
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            validator_name=self.name,
                            validator_type=self.validator_type,
                            level=ValidationLevel.SUCCESS,
                            message=f"Command '{command}' properly integrated",
                            details=description,
                            file_path="workflows.yaml",
                            line_number=None,
                            suggestion=None,
                        )
                    )

        return results


class ValidationEngine:
    """Main validation engine that orchestrates all validators"""

    def __init__(self):
        self.validators = [
            SyntaxValidator(),
            SemanticValidator(),
            SecurityValidator(),
            IntegrationValidator(),
        ]

    def validate_configuration(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> ValidationReport:
        """Run comprehensive validation on a configuration"""

        config_id = context.get("project_id", "unknown")

        report = ValidationReport(
            configuration_id=config_id,
            total_checks=0,
            passed_checks=0,
            failed_checks=0,
            warning_checks=0,
            critical_issues=0,
            results=[],
            deployment_ready=False,
            overall_score=0.0,
            recommendations=[],
        )

        print(f"🔍 Running comprehensive validation for {config_id}...")

        # Run all validators
        for validator in self.validators:
            print(f"  ⚡ Running {validator.name}...")

            try:
                validator_results = validator.validate(configuration, context)

                for result in validator_results:
                    report.add_result(result)

                print(
                    f"    ✅ {validator.name} completed ({len(validator_results)} checks)"
                )

            except Exception as e:
                error_result = ValidationResult(
                    validator_name=validator.name,
                    validator_type=validator.validator_type,
                    level=ValidationLevel.CRITICAL,
                    message=f"Validator failed: {str(e)}",
                    details="Internal validator error",
                    file_path=None,
                    line_number=None,
                    suggestion="Report this issue to SubForge developers",
                )
                report.add_result(error_result)
                print(f"    ❌ {validator.name} failed: {e}")

        # Calculate final score and recommendations
        report.calculate_score()
        report.recommendations = self._generate_recommendations(report)

        print(f"✅ Validation completed: {report.overall_score:.1f}% score")

        return report

    def _generate_recommendations(self, report: ValidationReport) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Group results by type and level
        critical_count = sum(
            1 for r in report.results if r.level == ValidationLevel.CRITICAL
        )
        warning_count = sum(
            1 for r in report.results if r.level == ValidationLevel.WARNING
        )

        if critical_count > 0:
            recommendations.append(
                f"Fix {critical_count} critical issues before deployment"
            )

        if warning_count > 0:
            recommendations.append(
                f"Address {warning_count} warnings to improve configuration quality"
            )

        # Specific recommendations based on validator types
        validator_issues = {}
        for result in report.results:
            if result.level in [ValidationLevel.CRITICAL, ValidationLevel.WARNING]:
                validator_type = result.validator_type.value
                validator_issues[validator_type] = (
                    validator_issues.get(validator_type, 0) + 1
                )

        if validator_issues.get("security", 0) > 0:
            recommendations.append("Review security settings and permissions")

        if validator_issues.get("integration", 0) > 0:
            recommendations.append("Check subagent and workflow integration")

        if validator_issues.get("syntax", 0) > 0:
            recommendations.append("Fix syntax errors in generated files")

        # Score-based recommendations
        if report.overall_score < 70:
            recommendations.append(
                "Configuration needs significant improvements before production use"
            )
        elif report.overall_score < 85:
            recommendations.append(
                "Configuration is functional but has room for improvement"
            )
        else:
            recommendations.append("Configuration meets high quality standards")

        return recommendations

    def create_test_deployment(
        self, configuration: Dict[str, Any], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Create a test deployment to validate actual functionality"""

        print("🧪 Creating test deployment...")

        try:
            # Create temporary directory for test
            with tempfile.TemporaryDirectory() as temp_dir:
                test_path = Path(temp_dir)

                # Create basic Claude Code structure
                claude_dir = test_path / ".claude"
                claude_dir.mkdir()

                agents_dir = claude_dir / "agents"
                agents_dir.mkdir()

                # Create test CLAUDE.md
                generated_configs = context.get("generated_configurations", {})
                claude_config = generated_configs.get("claude-md-generator", {})

                if "claude_md_content" in claude_config:
                    claude_md = claude_dir / "CLAUDE.md"
                    claude_md.write_text(claude_config["claude_md_content"])

                # Create test agent files
                agent_config = generated_configs.get("agent-generator", {})
                if "generated_agents" in agent_config:
                    for agent in agent_config["generated_agents"]:
                        if isinstance(agent, dict):
                            agent_name = agent.get("name", "unknown")
                            agent_file = agents_dir / f"{agent_name}.md"
                            agent_file.write_text(
                                f"# {agent_name}\n\nTest agent configuration"
                            )

                # Run basic validation checks
                if not claude_md.exists():
                    return False, "Failed to create CLAUDE.md file"

                if not any(agents_dir.iterdir()):
                    return False, "Failed to create any agent files"

                # Test file syntax
                try:
                    claude_md.read_text()
                except Exception as e:
                    return False, f"CLAUDE.md file has issues: {e}"

                print("✅ Test deployment successful")
                return True, "Test deployment completed successfully"

        except Exception as e:
            print(f"❌ Test deployment failed: {e}")
            return False, f"Test deployment failed: {str(e)}"


# CLI interface for testing
def main():
    """CLI interface for testing the validation engine"""
    import argparse

    parser = argparse.ArgumentParser(description="SubForge Validation Engine Test")
    parser.add_argument("config_file", help="Configuration file to validate (JSON)")
    parser.add_argument("--output", "-o", help="Output validation report to file")
    parser.add_argument(
        "--test-deployment", action="store_true", help="Run test deployment"
    )

    args = parser.parse_args()

    try:
        # Load configuration
        with open(args.config_file) as f:
            config_data = json.load(f)

        # Extract configuration and context
        configuration = config_data.get("configuration", {})
        context = config_data.get("context", {})

        # Run validation
        engine = ValidationEngine()
        report = engine.validate_configuration(configuration, context)

        # Display results
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        print(f"Configuration ID: {report.configuration_id}")
        print(f"Overall Score: {report.overall_score:.1f}%")
        print(f"Deployment Ready: {'Yes' if report.deployment_ready else 'No'}")
        print(f"Total Checks: {report.total_checks}")
        print(f"  Passed: {report.passed_checks}")
        print(f"  Warnings: {report.warning_checks}")
        print(f"  Failed: {report.failed_checks}")
        print(f"  Critical: {report.critical_issues}")

        if report.recommendations:
            print("\nRecommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")

        # Show detailed results
        if report.results:
            print("\nDetailed Results:")
            for result in report.results:
                level_emoji = {
                    ValidationLevel.SUCCESS: "✅",
                    ValidationLevel.INFO: "ℹ️",
                    ValidationLevel.WARNING: "⚠️",
                    ValidationLevel.CRITICAL: "❌",
                }
                emoji = level_emoji.get(result.level, "❓")
                print(f"  {emoji} {result.validator_name}: {result.message}")
                if result.suggestion:
                    print(f"      Suggestion: {result.suggestion}")

        # Test deployment
        if args.test_deployment:
            success, message = engine.create_test_deployment(configuration, context)
            print(f"\nTest Deployment: {'✅ Success' if success else '❌ Failed'}")
            print(f"  {message}")

        # Save report
        if args.output:
            with open(args.output, "w") as f:
                json.dump(report.to_dict(), f, indent=2)
            print(f"\n💾 Report saved to: {args.output}")

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
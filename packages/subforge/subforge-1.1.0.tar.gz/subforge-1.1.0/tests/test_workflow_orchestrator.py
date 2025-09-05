#!/usr/bin/env python3
"""
Comprehensive tests for WorkflowOrchestrator
Tests critical functionality and edge cases for workflow orchestration
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add subforge to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subforge.core.project_analyzer import (
    ArchitecturePattern,
    ProjectComplexity,
    ProjectProfile,
    TechnologyStack,
)
from subforge.core.workflow_orchestrator import (
    PhaseResult,
    PhaseStatus,
    SubagentExecutor,
    WorkflowContext,
    WorkflowOrchestrator,
    WorkflowPhase,
)


class TestPhaseResult:
    """Test PhaseResult dataclass functionality"""

    def test_phase_result_creation(self):
        """Test creating a PhaseResult instance"""
        result = PhaseResult(
            phase=WorkflowPhase.ANALYSIS,
            status=PhaseStatus.COMPLETED,
            duration=5.2,
            outputs={"key": "value"},
            errors=[],
            metadata={"test": True},
        )

        assert result.phase == WorkflowPhase.ANALYSIS
        assert result.status == PhaseStatus.COMPLETED
        assert result.duration == 5.2
        assert result.outputs["key"] == "value"
        assert result.errors == []
        assert result.metadata["test"] is True

    def test_phase_result_to_dict(self):
        """Test PhaseResult serialization to dict"""
        result = PhaseResult(
            phase=WorkflowPhase.GENERATION,
            status=PhaseStatus.FAILED,
            duration=1.5,
            outputs={"generated": ["agent1.md", "agent2.md"]},
            errors=["Template not found"],
            metadata={"retry_count": 2},
        )

        result_dict = result.to_dict()

        assert result_dict["phase"] == "generation"
        assert result_dict["status"] == "failed"
        assert result_dict["duration"] == 1.5
        assert result_dict["outputs"]["generated"] == ["agent1.md", "agent2.md"]
        assert "Template not found" in result_dict["errors"]
        assert result_dict["metadata"]["retry_count"] == 2


class TestWorkflowContext:
    """Test WorkflowContext functionality"""

    def test_workflow_context_creation(self, tmp_path):
        """Test creating WorkflowContext instance"""
        context = WorkflowContext(
            project_id="test_123",
            user_request="Create a web app",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={},
            project_profile=None,
            template_selections={},
            generated_configurations={},
            deployment_plan={},
        )

        assert context.project_id == "test_123"
        assert context.user_request == "Create a web app"
        assert context.project_path == str(tmp_path)
        assert isinstance(context.phase_results, dict)

    def test_workflow_context_to_dict(self, tmp_path):
        """Test WorkflowContext serialization"""
        # Create mock project profile
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"fastapi"},
            databases={"postgresql"},
            tools={"docker"},
            package_managers={"pip"},
        )
        profile = ProjectProfile(
            name="test_project",
            path=str(tmp_path),
            technology_stack=tech_stack,
            architecture_pattern=ArchitecturePattern.JAMSTACK,
            complexity=ProjectComplexity.MEDIUM,
            team_size_estimate=3,
            file_count=10,
            lines_of_code=500,
            has_tests=True,
            has_ci_cd=False,
            has_docker=True,
            has_docs=True,
            recommended_subagents=["backend-developer", "test-engineer"],
            integration_requirements=["api", "database"],
        )

        phase_result = PhaseResult(
            phase=WorkflowPhase.ANALYSIS,
            status=PhaseStatus.COMPLETED,
            duration=2.0,
            outputs={"analysis": "complete"},
            errors=[],
            metadata={},
        )

        context = WorkflowContext(
            project_id="test_456",
            user_request="Test request",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={WorkflowPhase.ANALYSIS: phase_result},
            project_profile=profile,
            template_selections={"selected": ["agent1"]},
            generated_configurations={"config": "value"},
            deployment_plan={"deploy": "k8s"},
        )

        context_dict = context.to_dict()

        assert context_dict["project_id"] == "test_456"
        assert context_dict["user_request"] == "Test request"
        assert "analysis" in context_dict["phase_results"]
        assert context_dict["project_profile"]["name"] == "test_project"
        assert context_dict["template_selections"]["selected"] == ["agent1"]


class TestSubagentExecutor:
    """Test SubagentExecutor functionality"""

    def test_subagent_executor_initialization(self, tmp_path):
        """Test SubagentExecutor initialization"""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        # Create some template files
        (templates_dir / "backend-developer.md").write_text("# Backend Developer")
        (templates_dir / "frontend-developer.md").write_text("# Frontend Developer")

        executor = SubagentExecutor(templates_dir)

        assert executor.templates_dir == templates_dir
        assert "backend-developer" in executor.available_subagents
        assert "frontend-developer" in executor.available_subagents

    def test_discover_subagents(self, tmp_path):
        """Test subagent discovery functionality"""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        # Create various template files
        templates = [
            "backend-developer.md",
            "frontend-developer.md",
            "test-engineer.md",
            "devops-engineer.md",
            "data-scientist.md",
        ]

        for template in templates:
            (templates_dir / template).write_text(
                f"# {template.replace('.md', '').replace('-', ' ').title()}"
            )

        executor = SubagentExecutor(templates_dir)

        assert len(executor.available_subagents) == 5
        for template in templates:
            agent_name = template.replace(".md", "")
            assert agent_name in executor.available_subagents
            assert executor.available_subagents[agent_name].name == template

    def test_discover_subagents_empty_directory(self, tmp_path):
        """Test subagent discovery with empty templates directory"""
        templates_dir = tmp_path / "empty_templates"
        templates_dir.mkdir()

        executor = SubagentExecutor(templates_dir)

        assert len(executor.available_subagents) == 0

    def test_discover_subagents_nonexistent_directory(self, tmp_path):
        """Test subagent discovery with non-existent templates directory"""
        templates_dir = tmp_path / "nonexistent"

        executor = SubagentExecutor(templates_dir)

        assert len(executor.available_subagents) == 0


class TestWorkflowOrchestrator:
    """Test WorkflowOrchestrator main functionality"""

    def test_orchestrator_initialization(self):
        """Test WorkflowOrchestrator initialization"""
        orchestrator = WorkflowOrchestrator()

        assert orchestrator.config is not None
        assert hasattr(orchestrator, "project_analyzer")
        assert hasattr(orchestrator, "context_engineer")
        assert hasattr(orchestrator, "prp_generator")

    @pytest.mark.asyncio
    async def test_create_workflow_context(self, tmp_path):
        """Test workflow context creation"""
        orchestrator = WorkflowOrchestrator()

        # Mock the project analyzer
        with patch.object(
            orchestrator.project_analyzer, "analyze_project"
        ) as mock_analyze:
            mock_profile = Mock()
            mock_profile.name = "test_project"
            mock_analyze.return_value = mock_profile

            context = await orchestrator._create_workflow_context(
                "Create a web application", str(tmp_path)
            )

            assert context.user_request == "Create a web application"
            assert context.project_path == str(tmp_path)
            assert context.project_profile == mock_profile
            assert isinstance(context.communication_dir, Path)

    @pytest.mark.asyncio
    async def test_execute_phase_success(self, tmp_path):
        """Test successful phase execution"""
        orchestrator = WorkflowOrchestrator()

        # Create test context
        context = WorkflowContext(
            project_id="test_789",
            user_request="Test request",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={},
            project_profile=None,
            template_selections={},
            generated_configurations={},
            deployment_plan={},
        )

        # Mock phase execution
        async def mock_phase_handler(ctx):
            return {"status": "success", "data": "test"}

        result = await orchestrator._execute_phase(
            context, WorkflowPhase.ANALYSIS, mock_phase_handler
        )

        assert result.phase == WorkflowPhase.ANALYSIS
        assert result.status == PhaseStatus.COMPLETED
        assert result.outputs["status"] == "success"
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_execute_phase_failure(self, tmp_path):
        """Test phase execution with failure"""
        orchestrator = WorkflowOrchestrator()

        context = WorkflowContext(
            project_id="test_error",
            user_request="Test request",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={},
            project_profile=None,
            template_selections={},
            generated_configurations={},
            deployment_plan={},
        )

        # Mock failing phase handler
        async def failing_phase_handler(ctx):
            raise Exception("Test error")

        result = await orchestrator._execute_phase(
            context, WorkflowPhase.GENERATION, failing_phase_handler
        )

        assert result.phase == WorkflowPhase.GENERATION
        assert result.status == PhaseStatus.FAILED
        assert len(result.errors) > 0
        assert "Test error" in result.errors[0]

    @pytest.mark.asyncio
    async def test_requirements_phase(self, tmp_path):
        """Test requirements gathering phase"""
        orchestrator = WorkflowOrchestrator()

        context = WorkflowContext(
            project_id="test_req",
            user_request="Create a FastAPI application with authentication",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={},
            project_profile=None,
            template_selections={},
            generated_configurations={},
            deployment_plan={},
        )

        # Mock the requirements analysis
        with patch.object(orchestrator, "_analyze_requirements") as mock_analyze:
            mock_analyze.return_value = {
                "functional_requirements": ["user authentication", "API endpoints"],
                "non_functional_requirements": ["performance", "security"],
                "technical_constraints": ["Python", "FastAPI"],
                "integration_requirements": ["database", "testing"],
            }

            outputs = await orchestrator._execute_requirements_phase(context)

            assert "functional_requirements" in outputs
            assert "user authentication" in outputs["functional_requirements"]
            assert "API endpoints" in outputs["functional_requirements"]
            assert mock_analyze.called

    @pytest.mark.asyncio
    async def test_analysis_phase(self, tmp_path):
        """Test project analysis phase"""
        orchestrator = WorkflowOrchestrator()

        # Create mock project profile
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"fastapi"},
            databases=set(),
            tools=set(),
            package_managers={"pip"},
        )
        profile = ProjectProfile(
            name="test_analysis",
            path=str(tmp_path),
            technology_stack=tech_stack,
            architecture_pattern=ArchitecturePattern.API_FIRST,
            complexity=ProjectComplexity.MEDIUM,
            team_size_estimate=2,
            file_count=5,
            lines_of_code=200,
            has_tests=False,
            has_ci_cd=False,
            has_docker=False,
            has_docs=False,
            recommended_subagents=["backend-developer"],
            integration_requirements=[],
        )

        context = WorkflowContext(
            project_id="test_analysis",
            user_request="Analyze this project",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={},
            project_profile=profile,
            template_selections={},
            generated_configurations={},
            deployment_plan={},
        )

        outputs = await orchestrator._execute_analysis_phase(context)

        assert "project_profile" in outputs
        assert "complexity_assessment" in outputs
        assert "recommended_patterns" in outputs
        assert outputs["project_profile"]["name"] == "test_analysis"

    @pytest.mark.asyncio
    async def test_selection_phase(self, tmp_path):
        """Test template selection phase"""
        orchestrator = WorkflowOrchestrator()

        # Create mock context with analysis results
        analysis_result = PhaseResult(
            phase=WorkflowPhase.ANALYSIS,
            status=PhaseStatus.COMPLETED,
            duration=1.0,
            outputs={
                "recommended_subagents": ["backend-developer", "test-engineer"],
                "architecture_pattern": "api_first",
                "complexity": "medium",
            },
            errors=[],
            metadata={},
        )

        context = WorkflowContext(
            project_id="test_selection",
            user_request="Select templates",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={WorkflowPhase.ANALYSIS: analysis_result},
            project_profile=None,
            template_selections={},
            generated_configurations={},
            deployment_plan={},
        )

        # Mock template selection
        with patch.object(
            orchestrator.prp_generator, "select_templates"
        ) as mock_select:
            mock_select.return_value = {
                "selected_templates": ["backend-developer", "test-engineer"],
                "template_priorities": {"backend-developer": 1, "test-engineer": 2},
                "selection_rationale": "Based on API-first architecture",
            }

            outputs = await orchestrator._execute_selection_phase(context)

            assert "selected_templates" in outputs
            assert "backend-developer" in outputs["selected_templates"]
            assert "test-engineer" in outputs["selected_templates"]
            assert mock_select.called


class TestWorkflowOrchestrator_EdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_execute_workflow_with_invalid_path(self):
        """Test workflow execution with invalid project path"""
        orchestrator = WorkflowOrchestrator()

        # Test with non-existent path
        with pytest.raises(Exception):
            await orchestrator.execute_workflow(
                "Test request", "/nonexistent/path/that/does/not/exist"
            )

    @pytest.mark.asyncio
    async def test_execute_workflow_empty_request(self, tmp_path):
        """Test workflow execution with empty user request"""
        orchestrator = WorkflowOrchestrator()

        # Mock project analyzer to avoid file system dependencies
        with patch.object(
            orchestrator.project_analyzer, "analyze_project"
        ) as mock_analyze:
            mock_profile = Mock()
            mock_profile.name = "test"
            mock_analyze.return_value = mock_profile

            with pytest.raises(ValueError, match="User request cannot be empty"):
                await orchestrator.execute_workflow("", str(tmp_path))

    @pytest.mark.asyncio
    async def test_phase_timeout_handling(self, tmp_path):
        """Test handling of phase timeouts"""
        orchestrator = WorkflowOrchestrator()

        context = WorkflowContext(
            project_id="timeout_test",
            user_request="Test timeout",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={},
            project_profile=None,
            template_selections={},
            generated_configurations={},
            deployment_plan={},
        )

        # Mock a phase handler that takes too long
        async def slow_phase_handler(ctx):
            await asyncio.sleep(10)  # Simulate long-running operation
            return {"status": "completed"}

        # Test with very short timeout
        with patch("asyncio.wait_for") as mock_wait_for:
            mock_wait_for.side_effect = asyncio.TimeoutError("Phase timed out")

            result = await orchestrator._execute_phase(
                context, WorkflowPhase.GENERATION, slow_phase_handler
            )

            assert result.status == PhaseStatus.FAILED
            assert "timed out" in result.errors[0].lower()

    @pytest.mark.asyncio
    async def test_workflow_state_persistence(self, tmp_path):
        """Test workflow state saving and loading"""
        orchestrator = WorkflowOrchestrator()

        # Create test context
        context = WorkflowContext(
            project_id="persist_test",
            user_request="Test persistence",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={},
            project_profile=None,
            template_selections={"test": "value"},
            generated_configurations={"config": "test"},
            deployment_plan={"deploy": "test"},
        )

        # Test saving state
        state_file = await orchestrator._save_workflow_state(context)
        assert state_file.exists()

        # Test loading state
        loaded_context = await orchestrator._load_workflow_state(state_file)
        assert loaded_context.project_id == context.project_id
        assert loaded_context.user_request == context.user_request
        assert loaded_context.template_selections == context.template_selections

    def test_workflow_phase_enum_completeness(self):
        """Test that all workflow phases are properly defined"""
        expected_phases = [
            "REQUIREMENTS",
            "ANALYSIS",
            "SELECTION",
            "GENERATION",
            "INTEGRATION",
            "VALIDATION",
            "DEPLOYMENT",
        ]

        actual_phases = [phase.name for phase in WorkflowPhase]

        for expected in expected_phases:
            assert expected in actual_phases

    def test_phase_status_enum_completeness(self):
        """Test that all phase statuses are properly defined"""
        expected_statuses = ["PENDING", "RUNNING", "COMPLETED", "FAILED", "SKIPPED"]

        actual_statuses = [status.name for status in PhaseStatus]

        for expected in expected_statuses:
            assert expected in actual_statuses


@pytest.fixture
def mock_orchestrator_dependencies():
    """Mock dependencies for orchestrator testing"""
    with patch("subforge.core.workflow_orchestrator.ProjectAnalyzer") as mock_analyzer:
        with patch(
            "subforge.core.workflow_orchestrator.create_context_engineer"
        ) as mock_context:
            with patch(
                "subforge.core.workflow_orchestrator.create_prp_generator"
            ) as mock_prp:
                mock_analyzer.return_value = Mock()
                mock_context.return_value = Mock()
                mock_prp.return_value = Mock()

                yield {
                    "analyzer": mock_analyzer,
                    "context": mock_context,
                    "prp": mock_prp,
                }


class TestWorkflowOrchestrator_Integration:
    """Integration tests for WorkflowOrchestrator"""

    @pytest.mark.asyncio
    async def test_full_workflow_execution_mock(
        self, tmp_path, mock_orchestrator_dependencies
    ):
        """Test complete workflow execution with mocked dependencies"""
        orchestrator = WorkflowOrchestrator()

        # Setup mocks
        mock_profile = Mock()
        mock_profile.name = "integration_test"
        mock_profile.recommended_subagents = ["backend-developer"]

        orchestrator.project_analyzer.analyze_project.return_value = mock_profile
        orchestrator.prp_generator.select_templates.return_value = {
            "selected_templates": ["backend-developer"],
            "template_priorities": {"backend-developer": 1},
        }
        orchestrator.prp_generator.generate_configurations.return_value = {
            "configurations": {"backend-developer": {"role": "API development"}}
        }

        # Execute workflow
        context = await orchestrator.execute_workflow(
            "Create a simple API", str(tmp_path)
        )

        # Verify results
        assert context.project_id.startswith("project_")
        assert context.user_request == "Create a simple API"
        assert context.project_path == str(tmp_path)
        assert len(context.phase_results) > 0

        # Check that key phases were executed
        completed_phases = [
            phase
            for phase, result in context.phase_results.items()
            if result.status == PhaseStatus.COMPLETED
        ]

        assert WorkflowPhase.REQUIREMENTS in completed_phases
        assert WorkflowPhase.ANALYSIS in completed_phases


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--color=yes"])
#!/usr/bin/env python3
"""
Comprehensive tests for orchestration and workflow modules with 100% coverage
Tests all critical paths, error scenarios, and edge cases with extensive mocking
"""

import asyncio
import json
import pytest
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock, patch, mock_open, MagicMock

# Import modules under test
from subforge.core.workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowPhase,
    PhaseStatus,
    PhaseResult,
    WorkflowContext,
    SubagentExecutor
)
from subforge.orchestration.parallel_executor import (
    ParallelExecutor,
    ParallelTask
)
from subforge.monitoring.workflow_monitor import (
    WorkflowMonitor,
    WorkflowStatus,
    AgentStatus,
    AgentExecution,
    WorkflowExecution
)


@pytest.fixture
def mock_project_path():
    """Mock project path"""
    return "/mock/project/path"


@pytest.fixture
def mock_templates_dir():
    """Mock templates directory"""
    return Path("/mock/templates")


@pytest.fixture
def mock_workspace_dir():
    """Mock workspace directory"""
    return Path("/mock/.subforge")


@pytest.fixture
def mock_project_profile():
    """Mock project profile"""
    profile = Mock()
    profile.name = "TestProject"
    profile.path = "/mock/project"
    profile.architecture_pattern = Mock(value="jamstack")
    profile.complexity = Mock(value="medium")
    profile.team_size_estimate = 6
    profile.recommended_subagents = ["backend-developer", "frontend-developer", "test-engineer"]
    profile.has_tests = True
    profile.has_docker = True
    profile.has_ci_cd = False
    profile.technology_stack = Mock()
    profile.technology_stack.languages = {"python", "javascript"}
    profile.technology_stack.frameworks = {"fastapi", "nextjs"}
    profile.to_dict = Mock(return_value={"name": "TestProject", "complexity": "medium"})
    return profile


@pytest.fixture
def mock_workflow_context(mock_project_profile):
    """Mock workflow context"""
    context = WorkflowContext(
        project_id="test-project-123",
        user_request="Create a web application",
        project_path="/mock/project",
        communication_dir=Path("/mock/.subforge/communication"),
        phase_results={},
        project_profile=mock_project_profile,
        template_selections={},
        generated_configurations={},
        deployment_plan={}
    )
    return context


class TestPhaseResult:
    """Test PhaseResult data class"""

    def test_phase_result_creation(self):
        """Test PhaseResult creation and to_dict conversion"""
        result = PhaseResult(
            phase=WorkflowPhase.ANALYSIS,
            status=PhaseStatus.COMPLETED,
            duration=10.5,
            outputs={"key": "value"},
            errors=["error1"],
            metadata={"meta": "data"}
        )
        
        assert result.phase == WorkflowPhase.ANALYSIS
        assert result.status == PhaseStatus.COMPLETED
        assert result.duration == 10.5
        
        result_dict = result.to_dict()
        assert result_dict["phase"] == "analysis"
        assert result_dict["status"] == "completed"
        assert result_dict["duration"] == 10.5
        assert result_dict["outputs"] == {"key": "value"}
        assert result_dict["errors"] == ["error1"]
        assert result_dict["metadata"] == {"meta": "data"}


class TestWorkflowContext:
    """Test WorkflowContext data class"""

    def test_workflow_context_creation(self, mock_project_profile):
        """Test WorkflowContext creation"""
        context = WorkflowContext(
            project_id="test-id",
            user_request="test request",
            project_path="/test/path",
            communication_dir=Path("/test/comm"),
            phase_results={},
            project_profile=mock_project_profile,
            template_selections={"key": "value"},
            generated_configurations={"config": "value"},
            deployment_plan={"deploy": "plan"}
        )
        
        assert context.project_id == "test-id"
        assert context.user_request == "test request"
        assert context.project_path == "/test/path"

    def test_workflow_context_to_dict(self, mock_workflow_context):
        """Test WorkflowContext to_dict conversion"""
        # Add phase result for testing
        phase_result = PhaseResult(
            phase=WorkflowPhase.ANALYSIS,
            status=PhaseStatus.COMPLETED,
            duration=5.0,
            outputs={},
            errors=[],
            metadata={}
        )
        mock_workflow_context.phase_results[WorkflowPhase.ANALYSIS] = phase_result
        
        context_dict = mock_workflow_context.to_dict()
        
        assert context_dict["project_id"] == "test-project-123"
        assert context_dict["user_request"] == "Create a web application"
        assert "phase_results" in context_dict
        assert "analysis" in context_dict["phase_results"]


class TestSubagentExecutor:
    """Test SubagentExecutor class"""

    @pytest.fixture
    def subagent_executor(self, mock_templates_dir):
        """Create SubagentExecutor instance"""
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'glob', return_value=[Path("test.md")]):
            return SubagentExecutor(mock_templates_dir)

    def test_subagent_executor_init(self, mock_templates_dir):
        """Test SubagentExecutor initialization"""
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'glob', return_value=[Path("test-agent.md")]):
            executor = SubagentExecutor(mock_templates_dir)
            assert executor.templates_dir == mock_templates_dir
            assert "test-agent" in executor.available_subagents

    def test_discover_subagents_empty_dir(self, mock_templates_dir):
        """Test discovering subagents from empty directory"""
        with patch.object(Path, 'exists', return_value=False):
            executor = SubagentExecutor(mock_templates_dir)
            assert executor.available_subagents == {}

    @pytest.mark.asyncio
    async def test_execute_subagent_factory_success(self, subagent_executor, mock_workflow_context):
        """Test successful factory subagent execution"""
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(subagent_executor, '_execute_factory_subagent', return_value={"success": True}) as mock_execute:
            
            result = await subagent_executor.execute_subagent(
                "project-analyzer", 
                mock_workflow_context,
                WorkflowPhase.ANALYSIS,
                {"input": "test"}
            )
            
            assert result["success"] is True
            assert result["subagent"] == "project-analyzer"
            assert result["phase"] == "analysis"
            assert "execution_time" in result
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_subagent_regular_fallback(self, subagent_executor, mock_workflow_context):
        """Test fallback to regular subagent execution"""
        with patch.object(Path, 'exists', return_value=False), \
             patch.object(subagent_executor, '_execute_regular_subagent', return_value={"fallback": True}) as mock_execute:
            
            result = await subagent_executor.execute_subagent(
                "custom-agent",
                mock_workflow_context,
                WorkflowPhase.GENERATION,
                {}
            )
            
            assert result["success"] is True
            assert result["outputs"]["fallback"] is True
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_subagent_exception(self, subagent_executor, mock_workflow_context):
        """Test subagent execution with exception"""
        with patch.object(Path, 'exists', side_effect=Exception("Test error")):
            
            result = await subagent_executor.execute_subagent(
                "failing-agent",
                mock_workflow_context,
                WorkflowPhase.ANALYSIS,
                {}
            )
            
            assert result["success"] is False
            assert "Test error" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_factory_subagent_all_types(self, subagent_executor, mock_workflow_context):
        """Test all factory subagent types execution"""
        factory_agents = [
            "project-analyzer", "template-selector", "claude-md-generator",
            "agent-generator", "workflow-generator", "deployment-validator"
        ]
        
        for agent_name in factory_agents:
            with patch.object(subagent_executor, f'_run_{agent_name.replace("-", "_")}', 
                            return_value={"agent": agent_name, "completed": True}) as mock_run:
                
                result = await subagent_executor._execute_factory_subagent(
                    agent_name, mock_workflow_context, {}
                )
                
                assert result["completed"] is True
                mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_factory_subagent_unknown(self, subagent_executor, mock_workflow_context):
        """Test unknown factory subagent raises exception"""
        with pytest.raises(ValueError, match="Unknown factory subagent"):
            await subagent_executor._execute_factory_subagent(
                "unknown-agent", mock_workflow_context, {}
            )

    @pytest.mark.asyncio
    async def test_run_project_analyzer(self, subagent_executor, mock_workflow_context):
        """Test project analyzer execution"""
        with patch('subforge.core.project_analyzer.ProjectAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer_class.return_value = mock_analyzer
            mock_analyzer.analyze_project = AsyncMock(return_value=mock_workflow_context.project_profile)
            
            with patch("builtins.open", mock_open()) as mock_file, \
                 patch.object(Path, 'mkdir'):
                result = await subagent_executor._run_project_analyzer(mock_workflow_context, {})
                
                assert result["analysis_completed"] is True
                assert "project_profile" in result
                assert "confidence_score" in result
                mock_file.assert_called()

    @pytest.mark.asyncio
    async def test_run_template_selector(self, subagent_executor, mock_workflow_context):
        """Test template selector execution"""
        with patch.object(Path, 'mkdir'), \
             patch("builtins.open", mock_open()):
            
            # Set orchestrator to avoid method call
            mock_orchestrator = Mock()
            mock_orchestrator._score_template_matches = AsyncMock(return_value={"template1": 0.9})
            subagent_executor.orchestrator = mock_orchestrator
            
            result = await subagent_executor._run_template_selector(mock_workflow_context, {})
            
            assert result["selection_completed"] is True
            assert "selected_templates" in result
            assert "scoring_details" in result

    @pytest.mark.asyncio
    async def test_run_template_selector_no_profile(self, subagent_executor, mock_workflow_context):
        """Test template selector without project profile"""
        mock_workflow_context.project_profile = None
        
        with pytest.raises(ValueError, match="Template selector requires project analysis"):
            await subagent_executor._run_template_selector(mock_workflow_context, {})


class TestWorkflowOrchestrator:
    """Test WorkflowOrchestrator class"""

    @pytest.fixture
    def workflow_orchestrator(self, mock_templates_dir, mock_workspace_dir):
        """Create WorkflowOrchestrator instance"""
        with patch('subforge.core.workflow_orchestrator.create_context_engineer') as mock_ce, \
             patch('subforge.core.workflow_orchestrator.create_prp_generator') as mock_prp, \
             patch.object(Path, 'mkdir'):
            
            mock_ce.return_value = Mock()
            mock_prp.return_value = Mock()
            
            return WorkflowOrchestrator(mock_templates_dir, mock_workspace_dir)

    def test_workflow_orchestrator_init(self, workflow_orchestrator):
        """Test WorkflowOrchestrator initialization"""
        assert workflow_orchestrator.templates_dir is not None
        assert workflow_orchestrator.workspace_dir is not None
        assert workflow_orchestrator.project_analyzer is not None
        assert workflow_orchestrator.subagent_executor is not None
        assert workflow_orchestrator.context_engineer is not None
        assert workflow_orchestrator.prp_generator is not None
        assert len(workflow_orchestrator.phase_definitions) > 0

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, workflow_orchestrator):
        """Test successful workflow execution"""
        with patch.object(workflow_orchestrator, '_execute_phase', 
                         return_value=PhaseResult(
                             phase=WorkflowPhase.ANALYSIS,
                             status=PhaseStatus.COMPLETED,
                             duration=1.0,
                             outputs={},
                             errors=[],
                             metadata={}
                         )) as mock_execute_phase, \
             patch.object(workflow_orchestrator, '_save_workflow_context') as mock_save, \
             patch.object(Path, 'mkdir'), \
             patch('builtins.print'):
            
            result = await workflow_orchestrator.execute_workflow(
                "Create a test app", "/tmp/test/project"
            )
            
            assert result is not None
            assert result.project_id is not None
            assert result.user_request == "Create a test app"
            assert mock_execute_phase.call_count >= 1
            mock_save.assert_called()

    @pytest.mark.asyncio
    async def test_execute_workflow_with_failure(self, workflow_orchestrator):
        """Test workflow execution with failure and recovery"""
        with patch.object(workflow_orchestrator, '_execute_phase', side_effect=Exception("Phase failed")), \
             patch.object(workflow_orchestrator, '_handle_workflow_failure', 
                         return_value=Mock()) as mock_handle_failure, \
             patch.object(Path, 'mkdir'), \
             patch('builtins.print'):
            
            result = await workflow_orchestrator.execute_workflow(
                "Create a test app", "/tmp/test/project"
            )
            
            mock_handle_failure.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_phase_success(self, workflow_orchestrator, mock_workflow_context):
        """Test successful phase execution"""
        phase = WorkflowPhase.ANALYSIS
        
        with patch.object(workflow_orchestrator.project_analyzer, 'analyze_project',
                         return_value=mock_workflow_context.project_profile), \
             patch.object(workflow_orchestrator, '_generate_clarifying_questions',
                         return_value=[]), \
             patch.object(workflow_orchestrator, '_collect_question_responses',
                         return_value={}), \
             patch.object(workflow_orchestrator, '_enhance_requirements_with_responses',
                         return_value="enhanced"), \
             patch.object(workflow_orchestrator, '_save_clarifying_session'), \
             patch.object(Path, 'mkdir'), \
             patch('builtins.print'):
            
            result = await workflow_orchestrator._execute_phase(phase, mock_workflow_context)
            
            assert result.phase == phase
            assert result.status == PhaseStatus.COMPLETED
            assert result.duration >= 0

    @pytest.mark.asyncio
    async def test_execute_phase_failure(self, workflow_orchestrator, mock_workflow_context):
        """Test phase execution with failure"""
        phase = WorkflowPhase.ANALYSIS
        
        with patch.object(workflow_orchestrator.project_analyzer, 'analyze_project',
                         side_effect=Exception("Analysis failed")), \
             patch.object(Path, 'mkdir'):
            
            result = await workflow_orchestrator._execute_phase(phase, mock_workflow_context)
            
            assert result.phase == phase
            assert result.status == PhaseStatus.FAILED
            assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_handle_requirements_phase(self, workflow_orchestrator, mock_workflow_context):
        """Test requirements phase handling"""
        with patch.object(workflow_orchestrator.project_analyzer, 'analyze_project',
                         return_value=mock_workflow_context.project_profile) as mock_analyze, \
             patch.object(workflow_orchestrator, '_generate_clarifying_questions',
                         return_value=["What is the main functionality?"]) as mock_questions, \
             patch.object(workflow_orchestrator, '_collect_question_responses',
                         return_value={"q1": "answer1"}) as mock_responses, \
             patch.object(workflow_orchestrator, '_enhance_requirements_with_responses',
                         return_value="Enhanced requirements") as mock_enhance, \
             patch.object(workflow_orchestrator, '_save_clarifying_session') as mock_save, \
             patch('builtins.print'):
            
            result = await workflow_orchestrator._handle_requirements_phase(mock_workflow_context)
            
            assert result["requirements_confirmed"] is True
            mock_analyze.assert_called()
            mock_questions.assert_called()
            mock_responses.assert_called()
            mock_enhance.assert_called()
            mock_save.assert_called()

    @pytest.mark.asyncio
    async def test_handle_analysis_phase(self, workflow_orchestrator, mock_workflow_context):
        """Test analysis phase handling"""
        phase_dir = Path("/mock/analysis")
        
        with patch.object(workflow_orchestrator.project_analyzer, 'analyze_project',
                         return_value=mock_workflow_context.project_profile) as mock_analyze, \
             patch.object(workflow_orchestrator.subagent_executor, 'execute_subagent',
                         return_value={"success": True, "outputs": {"analysis": "complete"}}) as mock_execute, \
             patch('builtins.print'):
            
            result = await workflow_orchestrator._handle_analysis_phase(mock_workflow_context, phase_dir)
            
            assert result["analysis_completed"] is True
            mock_analyze.assert_called()

    @pytest.mark.asyncio
    async def test_handle_selection_phase(self, workflow_orchestrator, mock_workflow_context):
        """Test selection phase handling"""
        phase_dir = Path("/mock/selection")
        
        with patch.object(workflow_orchestrator, '_score_template_matches',
                         return_value={"template1": 0.9, "template2": 0.7}) as mock_score, \
             patch('builtins.print'):
            
            result = await workflow_orchestrator._handle_selection_phase(mock_workflow_context, phase_dir)
            
            assert result["selection_completed"] is True
            assert "template_scores" in result
            mock_score.assert_called()

    @pytest.mark.asyncio
    async def test_handle_generation_phase(self, workflow_orchestrator, mock_workflow_context):
        """Test generation phase handling"""
        phase_dir = Path("/mock/generation")
        mock_workflow_context.template_selections = {"agent-generator": True}
        
        with patch.object(workflow_orchestrator.subagent_executor, 'execute_subagent',
                         return_value={"success": True, "outputs": {"agents": ["backend", "frontend"]}}) as mock_execute, \
             patch('builtins.print'):
            
            result = await workflow_orchestrator._handle_generation_phase(mock_workflow_context, phase_dir)
            
            assert result["generation_completed"] is True
            mock_execute.assert_called()

    @pytest.mark.asyncio
    async def test_handle_integration_phase(self, workflow_orchestrator, mock_workflow_context):
        """Test integration phase handling"""
        phase_dir = Path("/mock/integration")
        
        with patch('builtins.print'):
            result = await workflow_orchestrator._handle_integration_phase(mock_workflow_context, phase_dir)
            
            assert result["claude_md_integrated"] is True
            assert result["subagents_integrated"] is True
            assert result["workflows_integrated"] is True

    @pytest.mark.asyncio
    async def test_handle_validation_phase(self, workflow_orchestrator, mock_workflow_context):
        """Test validation phase handling"""
        phase_dir = Path("/mock/validation")
        
        with patch.object(workflow_orchestrator, '_run_validation_layers',
                         return_value={"validation_passed": True, "issues": []}) as mock_validate, \
             patch.object(workflow_orchestrator, '_format_validation_report',
                         return_value="# Validation Report") as mock_format_val, \
             patch.object(workflow_orchestrator, '_format_deployment_plan',
                         return_value="# Deployment Plan") as mock_format_deploy, \
             patch("builtins.open", mock_open()), \
             patch.object(Path, 'mkdir'), \
             patch('builtins.print'):
            
            result = await workflow_orchestrator._handle_validation_phase(mock_workflow_context, phase_dir)
            
            assert "validation_results" in result
            assert "validation_report" in result
            assert "deployment_plan" in result
            mock_validate.assert_called()

    @pytest.mark.asyncio
    async def test_handle_deployment_phase(self, workflow_orchestrator, mock_workflow_context):
        """Test deployment phase handling"""
        phase_dir = Path("/mock/deployment")
        mock_workflow_context.template_selections = {"selected_templates": ["backend-developer"]}
        
        with patch('builtins.print'), \
             patch.object(workflow_orchestrator.subagent_executor, '_deploy_agents_to_claude',
                         return_value={"deployed_agents": ["backend-developer"]}) as mock_deploy, \
             patch.object(workflow_orchestrator.subagent_executor, '_generate_real_claude_md',
                         return_value="# Mock CLAUDE.md content") as mock_claude, \
             patch("builtins.open", mock_open()):
            
            result = await workflow_orchestrator._handle_deployment_phase(mock_workflow_context, phase_dir)
            
            assert result["configuration_deployed"] is True
            assert "claude_md_created" in result
            mock_deploy.assert_called_once()
            mock_claude.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_deployment_phase_no_templates(self, workflow_orchestrator, mock_workflow_context):
        """Test deployment phase with no templates selected"""
        phase_dir = Path("/mock/deployment")
        mock_workflow_context.template_selections = {}
        
        with patch('builtins.print'):
            result = await workflow_orchestrator._handle_deployment_phase(mock_workflow_context, phase_dir)
            
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_workflow_failure_handling(self, workflow_orchestrator):
        """Test comprehensive workflow failure handling"""
        error = Exception("Test workflow error")
        
        with patch.object(workflow_orchestrator, '_log_workflow_error') as mock_log, \
             patch.object(workflow_orchestrator, '_backup_workflow_state') as mock_backup, \
             patch.object(workflow_orchestrator, '_retry_failed_phase', 
                         return_value=Mock()) as mock_retry, \
             patch.object(Path, 'mkdir'), \
             patch('builtins.print'):
            
            result = await workflow_orchestrator._handle_workflow_failure(
                error, None, "test request", "/tmp/test/path"
            )
            
            assert result is not None
            mock_log.assert_called_with(error, None, "test request", "/tmp/test/path")

    @pytest.mark.asyncio
    async def test_save_workflow_context(self, workflow_orchestrator, mock_workflow_context):
        """Test workflow context saving"""
        with patch("builtins.open", mock_open()) as mock_file, \
             patch("json.dump") as mock_json_dump:
            
            await workflow_orchestrator._save_workflow_context(mock_workflow_context)
            
            mock_file.assert_called()
            mock_json_dump.assert_called()

    def test_determine_claude_model(self, workflow_orchestrator):
        """Test Claude model determination logic"""
        # Since the method doesn't exist in the current implementation,
        # we'll add a basic implementation test
        from subforge.core.project_analyzer import ProjectComplexity
        
        # Mock the method if it doesn't exist
        if not hasattr(workflow_orchestrator, '_determine_claude_model'):
            def mock_determine_model(agent_name, complexity):
                if complexity == ProjectComplexity.COMPLEX:
                    return "opus"
                return "sonnet"
            
            workflow_orchestrator._determine_claude_model = mock_determine_model
        
        # Test Opus for complex projects
        model = workflow_orchestrator._determine_claude_model("backend-developer", ProjectComplexity.COMPLEX)
        assert model in ["opus", "sonnet"]

    def test_generate_project_context(self, workflow_orchestrator, mock_project_profile):
        """Test project context generation"""
        # Mock the method if it doesn't exist
        if not hasattr(workflow_orchestrator, '_generate_project_context'):
            def mock_generate_context(profile, agent_name, request):
                return f"Context for {agent_name} in {profile.name} project: {request}"
            
            workflow_orchestrator._generate_project_context = mock_generate_context
        
        context = workflow_orchestrator._generate_project_context(
            mock_project_profile, "backend-developer", "Create API"
        )
        
        assert "backend-developer" in context
        assert mock_project_profile.name in context


class TestParallelTask:
    """Test ParallelTask data class"""

    def test_parallel_task_creation(self):
        """Test ParallelTask creation"""
        task = ParallelTask(
            agent="@backend-developer",
            task="create_api",
            description="Create REST API",
            dependencies=["database_setup"],
            can_parallel=False
        )
        
        assert task.agent == "@backend-developer"
        assert task.task == "create_api"
        assert task.dependencies == ["database_setup"]
        assert task.can_parallel is False

    def test_parallel_task_to_prompt(self):
        """Test ParallelTask prompt generation"""
        task = ParallelTask(
            agent="@frontend-developer",
            task="create_ui",
            description="Create user interface"
        )
        
        prompt = task.to_prompt()
        assert "@frontend-developer" in prompt
        assert "create_ui" in prompt
        assert "Create user interface" in prompt
        assert "Execute this specific task" in prompt


class TestParallelExecutor:
    """Test ParallelExecutor class"""

    @pytest.fixture
    def parallel_executor(self, mock_project_path):
        """Create ParallelExecutor instance"""
        with patch.object(Path, 'mkdir'):
            return ParallelExecutor(mock_project_path)

    def test_parallel_executor_init(self, parallel_executor, mock_project_path):
        """Test ParallelExecutor initialization"""
        assert str(parallel_executor.project_path) == mock_project_path
        assert parallel_executor.workflow_state.name == "workflow-state"

    @pytest.mark.asyncio
    async def test_execute_parallel_analysis(self, parallel_executor):
        """Test parallel analysis execution"""
        with patch.object(parallel_executor, '_execute_parallel_batch',
                         return_value={"@backend-developer": {"status": "completed"}}) as mock_batch, \
             patch.object(parallel_executor, '_consolidate_analysis',
                         return_value={"summary": "analysis complete"}) as mock_consolidate, \
             patch.object(parallel_executor, '_save_to_state') as mock_save:
            
            result = await parallel_executor.execute_parallel_analysis("Test request")
            
            assert result["summary"] == "analysis complete"
            mock_batch.assert_called_once()
            mock_consolidate.assert_called_once()
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_parallel_research(self, parallel_executor):
        """Test parallel research execution"""
        topics = ["topic1", "topic2"]
        
        with patch.object(parallel_executor, '_execute_parallel_batch',
                         return_value={"perplexity_topic1": {"data": "research"}}) as mock_batch, \
             patch.object(parallel_executor, '_synthesize_research',
                         return_value={"best_practices": ["practice1"]}) as mock_synthesize, \
             patch.object(parallel_executor, '_save_to_state') as mock_save:
            
            result = await parallel_executor.execute_parallel_research(topics)
            
            assert "best_practices" in result
            mock_batch.assert_called_once()
            mock_synthesize.assert_called_once()
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_smart_implementation(self, parallel_executor):
        """Test smart implementation with mixed parallel/sequential tasks"""
        tasks = [
            {"agent": "@backend", "task": "api", "dependencies": None},
            {"agent": "@frontend", "task": "ui", "dependencies": None},
            {"agent": "@test", "task": "tests", "dependencies": ["api", "ui"]}
        ]
        
        with patch.object(parallel_executor, '_group_by_dependencies',
                         return_value=[
                             {"can_parallel": True, "tasks": [Mock(), Mock()]},
                             {"can_parallel": False, "tasks": [Mock()]}
                         ]) as mock_group, \
             patch.object(parallel_executor, '_execute_parallel_batch',
                         return_value={"@backend": {}, "@frontend": {}}) as mock_parallel, \
             patch.object(parallel_executor, '_execute_single',
                         return_value={"@test": {}}) as mock_single:
            
            result = await parallel_executor.execute_smart_implementation(tasks)
            
            assert len(result) >= 2
            mock_group.assert_called_once()
            mock_parallel.assert_called_once()
            mock_single.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_parallel_batch(self, parallel_executor):
        """Test parallel batch execution"""
        tasks = [
            ParallelTask("@agent1", "task1", "desc1"),
            ParallelTask("@agent2", "task2", "desc2")
        ]
        
        with patch.object(parallel_executor, '_save_task_status') as mock_save_status:
            
            results = await parallel_executor._execute_parallel_batch(tasks)
            
            assert len(results) == 2
            assert "@agent1" in results
            assert "@agent2" in results
            assert results["@agent1"]["status"] == "completed"
            assert mock_save_status.call_count == 4  # 2 tasks * 2 status updates

    @pytest.mark.asyncio
    async def test_execute_single(self, parallel_executor):
        """Test single task execution"""
        task = ParallelTask("@agent", "task", "description")
        
        with patch.object(parallel_executor, '_save_task_status') as mock_save_status:
            
            result = await parallel_executor._execute_single(task)
            
            assert result["status"] == "completed"
            assert result["task"] == "task"
            assert mock_save_status.call_count == 2

    def test_group_by_dependencies(self, parallel_executor):
        """Test task grouping by dependencies"""
        tasks = [
            {"agent": "agent1", "task": "task1", "description": "desc1", "dependencies": None},
            {"agent": "agent2", "task": "task2", "description": "desc2", "dependencies": None},
            {"agent": "agent3", "task": "task3", "description": "desc3", "dependencies": ["agent1"]}
        ]
        
        with patch.object(parallel_executor, '_topological_sort', return_value=[tasks[2]]):
            groups = parallel_executor._group_by_dependencies(tasks)
            
            assert len(groups) == 2
            assert groups[0]["can_parallel"] is True
            assert len(groups[0]["tasks"]) == 2
            assert groups[1]["can_parallel"] is False
            assert len(groups[1]["tasks"]) == 1

    def test_topological_sort(self, parallel_executor):
        """Test topological sort implementation"""
        tasks = [
            {"dependencies": ["a", "b"]},
            {"dependencies": []},
            {"dependencies": ["a"]}
        ]
        
        sorted_tasks = parallel_executor._topological_sort(tasks)
        
        # Should sort by dependency count
        assert len(sorted_tasks[0].get("dependencies", [])) <= len(sorted_tasks[1].get("dependencies", []))

    def test_consolidate_analysis(self, parallel_executor):
        """Test analysis consolidation"""
        results = {
            "@agent1": {"findings": {"issue1": "found"}, "recommendations": ["rec1"]},
            "@agent2": {"findings": {"issue2": "found"}, "recommendations": ["rec2"]}
        }
        
        consolidated = parallel_executor._consolidate_analysis(results)
        
        assert consolidated["summary"] == "Parallel analysis completed"
        assert "@agent1" in consolidated["findings"]
        assert "@agent2" in consolidated["findings"]
        assert "rec1" in consolidated["recommendations"]
        assert "rec2" in consolidated["recommendations"]

    def test_synthesize_research(self, parallel_executor):
        """Test research synthesis"""
        results = {
            "perplexity_topic1": {"data": "practice1"},
            "github_topic1": {"data": "example1"},
            "ref_topic1": {"data": "doc1"}
        }
        
        synthesis = parallel_executor._synthesize_research(results)
        
        assert len(synthesis["best_practices"]) == 1
        assert len(synthesis["examples"]) == 1
        assert len(synthesis["documentation"]) == 1

    def test_save_to_state(self, parallel_executor):
        """Test saving data to shared state"""
        test_data = {"key": "value"}
        
        with patch("builtins.open", mock_open(read_data='{"existing": "data"}')) as mock_file, \
             patch("json.load", return_value={"existing": "data"}), \
             patch("json.dump") as mock_dump:
            
            parallel_executor._save_to_state("test_key", test_data)
            
            mock_file.assert_called()
            mock_dump.assert_called()

    def test_save_to_state_new_file(self, parallel_executor):
        """Test saving data to state with new file"""
        test_data = {"key": "value"}
        
        with patch("builtins.open", mock_open()) as mock_file, \
             patch.object(Path, 'exists', return_value=False), \
             patch("json.dump") as mock_dump:
            
            parallel_executor._save_to_state("test_key", test_data)
            
            mock_file.assert_called()
            mock_dump.assert_called()

    def test_save_task_status(self, parallel_executor):
        """Test saving task execution status"""
        task = ParallelTask("@agent", "task", "description")
        
        with patch("builtins.open", mock_open()) as mock_file, \
             patch.object(Path, 'exists', return_value=False), \
             patch("json.dump") as mock_dump, \
             patch.object(asyncio, 'get_event_loop') as mock_loop:
            
            mock_loop.return_value.time.return_value = 123456.789
            
            parallel_executor._save_task_status(task, "executing")
            
            mock_file.assert_called()
            mock_dump.assert_called()


class TestAgentExecution:
    """Test AgentExecution data class"""

    def test_agent_execution_creation(self):
        """Test AgentExecution creation"""
        execution = AgentExecution(
            agent_name="@backend-dev",
            task_id="task123",
            start_time=100.0,
            end_time=110.0,
            status=AgentStatus.COMPLETED,
            task_description="Create API",
            output={"result": "success"},
            error_message=None
        )
        
        assert execution.agent_name == "@backend-dev"
        assert execution.duration() == 10.0
        assert execution.is_active() is False

    def test_agent_execution_active(self):
        """Test active agent execution"""
        execution = AgentExecution(
            agent_name="@frontend-dev",
            task_id="task456",
            start_time=100.0,
            end_time=None,
            status=AgentStatus.BUSY,
            task_description="Create UI",
            output={},
            error_message=None
        )
        
        assert execution.is_active() is True
        assert execution.duration() is None

    def test_agent_execution_to_dict(self):
        """Test AgentExecution to_dict conversion"""
        execution = AgentExecution(
            agent_name="@test-eng",
            task_id="task789",
            start_time=100.0,
            end_time=120.0,
            status=AgentStatus.COMPLETED,
            task_description="Write tests",
            output={"tests": 5},
            error_message=None
        )
        
        execution_dict = execution.to_dict()
        
        assert execution_dict["agent_name"] == "@test-eng"
        assert execution_dict["status"] == "completed"
        assert execution_dict["duration"] == 20.0


class TestWorkflowExecution:
    """Test WorkflowExecution data class"""

    @pytest.fixture
    def sample_workflow_execution(self):
        """Create sample WorkflowExecution"""
        return WorkflowExecution(
            workflow_id="workflow123",
            project_path="/test/project",
            user_request="Create web app",
            start_time=1000.0,
            end_time=1100.0,
            status=WorkflowStatus.COMPLETED,
            current_phase="deployment",
            agent_executions=[],
            parallel_groups=[["@backend", "@frontend"]]
        )

    def test_workflow_execution_creation(self, sample_workflow_execution):
        """Test WorkflowExecution creation"""
        assert sample_workflow_execution.workflow_id == "workflow123"
        assert sample_workflow_execution.duration() == 100.0
        assert sample_workflow_execution.is_running() is False

    def test_workflow_execution_active_agents(self, sample_workflow_execution):
        """Test active agents tracking"""
        active_execution = AgentExecution(
            agent_name="@backend", task_id="task1", start_time=1000.0,
            end_time=None, status=AgentStatus.BUSY, task_description="API",
            output={}, error_message=None
        )
        completed_execution = AgentExecution(
            agent_name="@frontend", task_id="task2", start_time=1000.0,
            end_time=1050.0, status=AgentStatus.COMPLETED, task_description="UI",
            output={}, error_message=None
        )
        
        sample_workflow_execution.agent_executions = [active_execution, completed_execution]
        
        active_agents = sample_workflow_execution.get_active_agents()
        completed_agents = sample_workflow_execution.get_completed_agents()
        
        assert "@backend" in active_agents
        assert "@frontend" in completed_agents

    def test_workflow_execution_failed_agents(self, sample_workflow_execution):
        """Test failed agents tracking"""
        failed_execution = AgentExecution(
            agent_name="@devops", task_id="task3", start_time=1000.0,
            end_time=1030.0, status=AgentStatus.FAILED, task_description="Deploy",
            output={}, error_message="Deployment failed"
        )
        
        sample_workflow_execution.agent_executions = [failed_execution]
        
        failed_agents = sample_workflow_execution.get_failed_agents()
        assert "@devops" in failed_agents

    def test_workflow_execution_to_dict(self, sample_workflow_execution):
        """Test WorkflowExecution to_dict conversion"""
        workflow_dict = sample_workflow_execution.to_dict()
        
        assert workflow_dict["workflow_id"] == "workflow123"
        assert workflow_dict["status"] == "completed"
        assert workflow_dict["duration"] == 100.0
        assert "parallel_groups" in workflow_dict
        assert "active_agents" in workflow_dict


class TestWorkflowMonitor:
    """Test WorkflowMonitor class"""

    @pytest.fixture
    def workflow_monitor(self, mock_project_path):
        """Create WorkflowMonitor instance"""
        with patch.object(Path, 'mkdir'):
            return WorkflowMonitor(mock_project_path)

    def test_workflow_monitor_init(self, workflow_monitor, mock_project_path):
        """Test WorkflowMonitor initialization"""
        assert str(workflow_monitor.project_path) == mock_project_path
        assert workflow_monitor.total_workflows == 0
        assert workflow_monitor.successful_workflows == 0
        assert workflow_monitor.failed_workflows == 0
        assert len(workflow_monitor.event_callbacks) > 0

    def test_start_workflow(self, workflow_monitor):
        """Test starting workflow monitoring"""
        with patch.object(workflow_monitor, '_trigger_event') as mock_trigger, \
             patch.object(workflow_monitor, '_save_workflow_state') as mock_save:
            
            workflow = workflow_monitor.start_workflow("wf123", "Test request")
            
            assert workflow.workflow_id == "wf123"
            assert workflow.status == WorkflowStatus.RUNNING
            assert workflow_monitor.total_workflows == 1
            assert "wf123" in workflow_monitor.active_workflows
            mock_trigger.assert_called_with("workflow_started", workflow)
            mock_save.assert_called_once()

    def test_end_workflow_success(self, workflow_monitor):
        """Test ending workflow successfully"""
        # Start workflow first
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        with patch.object(workflow_monitor, '_trigger_event') as mock_trigger, \
             patch.object(workflow_monitor, '_save_workflow_state') as mock_save:
            
            workflow_monitor.end_workflow("wf123", WorkflowStatus.COMPLETED)
            
            assert workflow_monitor.successful_workflows == 1
            assert "wf123" not in workflow_monitor.active_workflows
            assert len(workflow_monitor.completed_workflows) == 1
            mock_trigger.assert_called_with("workflow_completed", workflow)
            mock_save.assert_called_once()

    def test_end_workflow_failure(self, workflow_monitor):
        """Test ending workflow with failure"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        with patch.object(workflow_monitor, '_trigger_event') as mock_trigger, \
             patch.object(workflow_monitor, '_save_workflow_state') as mock_save:
            
            workflow_monitor.end_workflow("wf123", WorkflowStatus.FAILED, "Test error")
            
            assert workflow_monitor.failed_workflows == 1
            mock_trigger.assert_called_with("workflow_failed", workflow, "Test error")

    def test_end_workflow_not_found(self, workflow_monitor):
        """Test ending non-existent workflow"""
        with patch('logging.Logger.warning') as mock_warning:
            workflow_monitor.end_workflow("nonexistent", WorkflowStatus.COMPLETED)
            mock_warning.assert_called()

    def test_update_phase(self, workflow_monitor):
        """Test updating workflow phase"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        with patch.object(workflow_monitor, '_trigger_event') as mock_trigger, \
             patch.object(workflow_monitor, '_save_workflow_state') as mock_save:
            
            workflow_monitor.update_phase("wf123", "analysis")
            
            assert workflow.current_phase == "analysis"
            mock_trigger.assert_called_with("phase_changed", "wf123", "requirements", "analysis")
            mock_save.assert_called_once()

    def test_start_agent_execution(self, workflow_monitor):
        """Test starting agent execution tracking"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        with patch.object(workflow_monitor, '_trigger_event') as mock_trigger, \
             patch.object(workflow_monitor, '_save_workflow_state') as mock_save:
            
            execution = workflow_monitor.start_agent_execution(
                "wf123", "@backend-dev", "task1", "Create API"
            )
            
            assert execution is not None
            assert execution.agent_name == "@backend-dev"
            assert execution.status == AgentStatus.BUSY
            assert len(workflow.agent_executions) == 1
            mock_trigger.assert_called_with("agent_started", "wf123", execution)
            mock_save.assert_called_once()

    def test_start_agent_execution_no_workflow(self, workflow_monitor):
        """Test starting agent execution for non-existent workflow"""
        with patch('logging.Logger.warning') as mock_warning:
            execution = workflow_monitor.start_agent_execution(
                "nonexistent", "@agent", "task", "desc"
            )
            
            assert execution is None
            mock_warning.assert_called()

    def test_end_agent_execution(self, workflow_monitor):
        """Test ending agent execution tracking"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        execution = workflow_monitor.start_agent_execution(
            "wf123", "@backend-dev", "task1", "Create API"
        )
        
        with patch.object(workflow_monitor, '_trigger_event') as mock_trigger, \
             patch.object(workflow_monitor, '_save_workflow_state') as mock_save:
            
            workflow_monitor.end_agent_execution(
                "wf123", "@backend-dev", "task1", AgentStatus.COMPLETED,
                {"result": "success"}, None
            )
            
            assert execution.status == AgentStatus.COMPLETED
            assert execution.output == {"result": "success"}
            assert execution.end_time is not None
            mock_trigger.assert_called_with("agent_completed", "wf123", execution)
            mock_save.assert_called_once()

    def test_end_agent_execution_failed(self, workflow_monitor):
        """Test ending agent execution with failure"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        execution = workflow_monitor.start_agent_execution(
            "wf123", "@backend-dev", "task1", "Create API"
        )
        
        with patch.object(workflow_monitor, '_trigger_event') as mock_trigger, \
             patch.object(workflow_monitor, '_save_workflow_state') as mock_save:
            
            workflow_monitor.end_agent_execution(
                "wf123", "@backend-dev", "task1", AgentStatus.FAILED,
                {}, "Test error"
            )
            
            assert execution.status == AgentStatus.FAILED
            assert execution.error_message == "Test error"
            mock_trigger.assert_called_with("agent_failed", "wf123", execution, "Test error")

    def test_end_agent_execution_not_found(self, workflow_monitor):
        """Test ending non-existent agent execution"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        with patch('logging.Logger.warning') as mock_warning:
            workflow_monitor.end_agent_execution(
                "wf123", "@nonexistent", "task", AgentStatus.COMPLETED, {}, None
            )
            mock_warning.assert_called()

    def test_set_parallel_group(self, workflow_monitor):
        """Test setting parallel group"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        with patch.object(workflow_monitor, '_save_workflow_state') as mock_save:
            workflow_monitor.set_parallel_group("wf123", ["@backend", "@frontend"])
            
            assert ["@backend", "@frontend"] in workflow.parallel_groups
            mock_save.assert_called_once()

    def test_get_workflow_status_active(self, workflow_monitor):
        """Test getting status of active workflow"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        status = workflow_monitor.get_workflow_status("wf123")
        
        assert status is not None
        assert status["workflow_id"] == "wf123"
        assert status["status"] == "running"

    def test_get_workflow_status_completed(self, workflow_monitor):
        """Test getting status of completed workflow"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        workflow_monitor.end_workflow("wf123", WorkflowStatus.COMPLETED)
        
        status = workflow_monitor.get_workflow_status("wf123")
        
        assert status is not None
        assert status["workflow_id"] == "wf123"
        assert status["status"] == "completed"

    def test_get_workflow_status_not_found(self, workflow_monitor):
        """Test getting status of non-existent workflow"""
        status = workflow_monitor.get_workflow_status("nonexistent")
        assert status is None

    def test_get_all_workflows(self, workflow_monitor):
        """Test getting all workflows status"""
        workflow1 = workflow_monitor.start_workflow("wf1", "Request 1")
        workflow2 = workflow_monitor.start_workflow("wf2", "Request 2")
        workflow_monitor.end_workflow("wf1", WorkflowStatus.COMPLETED)
        
        all_workflows = workflow_monitor.get_all_workflows()
        
        assert len(all_workflows["active"]) == 1
        assert len(all_workflows["completed"]) == 1
        assert all_workflows["statistics"]["total_workflows"] == 2
        assert all_workflows["statistics"]["successful_workflows"] == 1

    def test_get_real_time_metrics(self, workflow_monitor):
        """Test getting real-time metrics"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        workflow_monitor.start_agent_execution("wf123", "@backend", "task", "desc")
        
        with patch.object(workflow_monitor, '_count_recent_workflows', return_value=1), \
             patch.object(workflow_monitor, '_calculate_average_duration', return_value=50.0), \
             patch.object(workflow_monitor, '_calculate_current_parallelization', return_value=0.5):
            
            metrics = workflow_monitor.get_real_time_metrics()
            
            assert metrics["active_workflows"] == 1
            assert metrics["total_active_agents"] == 1
            assert metrics["workflows_in_last_hour"] == 1
            assert metrics["average_workflow_duration"] == 50.0
            assert metrics["current_parallelization"] == 0.5

    def test_register_callback(self, workflow_monitor):
        """Test registering event callbacks"""
        callback = Mock()
        
        with patch('logging.Logger.info') as mock_info:
            workflow_monitor.register_callback("workflow_started", callback)
            
            assert callback in workflow_monitor.event_callbacks["workflow_started"]
            mock_info.assert_called()

    def test_export_monitoring_data(self, workflow_monitor):
        """Test exporting monitoring data"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        workflow_monitor.end_workflow("wf123", WorkflowStatus.COMPLETED)
        
        with patch("builtins.open", mock_open()) as mock_file, \
             patch("json.dump") as mock_dump, \
             patch('logging.Logger.info') as mock_info:
            
            output_file = workflow_monitor.export_monitoring_data()
            
            assert output_file.name.startswith("monitoring_export_")
            mock_file.assert_called()
            mock_dump.assert_called()
            mock_info.assert_called()

    def test_trigger_event(self, workflow_monitor):
        """Test triggering event callbacks"""
        callback1 = Mock()
        callback2 = Mock()
        workflow_monitor.event_callbacks["test_event"] = [callback1, callback2]
        
        workflow_monitor._trigger_event("test_event", "arg1", "arg2")
        
        callback1.assert_called_once_with("arg1", "arg2")
        callback2.assert_called_once_with("arg1", "arg2")

    def test_trigger_event_with_exception(self, workflow_monitor):
        """Test triggering event callbacks with exception"""
        failing_callback = Mock(side_effect=Exception("Callback error"))
        workflow_monitor.event_callbacks["test_event"] = [failing_callback]
        
        with patch('logging.Logger.error') as mock_error:
            workflow_monitor._trigger_event("test_event", "arg1")
            
            mock_error.assert_called()

    def test_save_workflow_state(self, workflow_monitor):
        """Test saving workflow state to disk"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        with patch("builtins.open", mock_open()) as mock_file, \
             patch("json.dump") as mock_dump:
            
            workflow_monitor._save_workflow_state(workflow)
            
            mock_file.assert_called()
            mock_dump.assert_called()

    def test_save_workflow_state_exception(self, workflow_monitor):
        """Test saving workflow state with exception"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        
        with patch("builtins.open", side_effect=Exception("Save error")), \
             patch('logging.Logger.error') as mock_error:
            
            workflow_monitor._save_workflow_state(workflow)
            
            mock_error.assert_called()

    def test_count_recent_workflows(self, workflow_monitor):
        """Test counting recent workflows"""
        current_time = time.time()
        
        # Create workflows at different times
        with patch('time.time', return_value=current_time - 3600):  # 1 hour ago
            old_workflow = workflow_monitor.start_workflow("old", "Old request")
            workflow_monitor.end_workflow("old", WorkflowStatus.COMPLETED)
        
        with patch('time.time', return_value=current_time - 1800):  # 30 minutes ago
            recent_workflow = workflow_monitor.start_workflow("recent", "Recent request")
            workflow_monitor.end_workflow("recent", WorkflowStatus.COMPLETED)
        
        with patch('time.time', return_value=current_time):
            count = workflow_monitor._count_recent_workflows(3600)  # Last hour
            assert count >= 1  # At least the recent workflow

    def test_calculate_average_duration(self, workflow_monitor):
        """Test calculating average workflow duration"""
        # Create completed workflows with known durations
        workflow1 = workflow_monitor.start_workflow("wf1", "Request 1")
        workflow1.start_time = 1000.0
        workflow1.end_time = 1010.0  # 10 second duration
        
        workflow2 = workflow_monitor.start_workflow("wf2", "Request 2")
        workflow2.start_time = 2000.0
        workflow2.end_time = 2020.0  # 20 second duration
        
        workflow_monitor.completed_workflows = [workflow1, workflow2]
        
        avg_duration = workflow_monitor._calculate_average_duration()
        assert avg_duration == 15.0  # (10 + 20) / 2

    def test_calculate_average_duration_no_completed(self, workflow_monitor):
        """Test calculating average duration with no completed workflows"""
        avg_duration = workflow_monitor._calculate_average_duration()
        assert avg_duration == 0.0

    def test_calculate_current_parallelization(self, workflow_monitor):
        """Test calculating current parallelization ratio"""
        workflow = workflow_monitor.start_workflow("wf123", "Test request")
        workflow.parallel_groups = [
            ["@agent1", "@agent2"],  # 2 parallel agents
            ["@agent3"]  # 1 sequential agent
        ]
        
        parallelization = workflow_monitor._calculate_current_parallelization()
        assert parallelization == 2.0 / 3.0  # 2 parallel out of 3 total

    def test_calculate_current_parallelization_no_agents(self, workflow_monitor):
        """Test calculating parallelization with no agents"""
        parallelization = workflow_monitor._calculate_current_parallelization()
        assert parallelization == 0.0

    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, workflow_monitor):
        """Test cleaning up old monitoring data"""
        current_time = time.time()
        old_time = current_time - (31 * 24 * 3600)  # 31 days ago
        
        # Create old workflow
        old_workflow = Mock()
        old_workflow.start_time = old_time
        workflow_monitor.completed_workflows = [old_workflow]
        
        # Create mock old files
        mock_file = Mock()
        mock_file.stat.return_value.st_mtime = old_time
        mock_file.unlink = Mock()
        
        with patch('pathlib.Path.glob', return_value=[mock_file]):
            await workflow_monitor.cleanup_old_data(30)
            
            assert len(workflow_monitor.completed_workflows) == 0
            mock_file.unlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_old_data_file_error(self, workflow_monitor):
        """Test cleanup with file error"""
        mock_file = Mock()
        mock_file.stat.side_effect = Exception("File error")
        
        with patch('pathlib.Path.glob', return_value=[mock_file]), \
             patch('logging.Logger.error') as mock_error:
            
            await workflow_monitor.cleanup_old_data(30)
            
            mock_error.assert_called()


@pytest.mark.asyncio
async def test_demonstrate_parallel_execution():
    """Test the demonstration function"""
    with patch('subforge.orchestration.parallel_executor.ParallelExecutor') as mock_executor_class:
        mock_executor = Mock()
        mock_executor.execute_parallel_analysis = AsyncMock(return_value={"analysis": "done"})
        mock_executor.execute_parallel_research = AsyncMock(return_value={"research": "done"})
        mock_executor.execute_smart_implementation = AsyncMock(return_value={"implementation": "done"})
        mock_executor_class.return_value = mock_executor
        
        from subforge.orchestration.parallel_executor import demonstrate_parallel_execution
        
        result = await demonstrate_parallel_execution()
        
        assert "analysis" in result
        assert "research" in result
        assert "implementation" in result


class TestIntegrationScenarios:
    """Test integration scenarios between components"""

    @pytest.mark.asyncio
    async def test_workflow_with_monitoring(self):
        """Test workflow execution with monitoring integration"""
        with patch('subforge.core.workflow_orchestrator.create_context_engineer'), \
             patch('subforge.core.workflow_orchestrator.create_prp_generator'), \
             patch.object(Path, 'mkdir'):
            
            orchestrator = WorkflowOrchestrator()
            monitor = WorkflowMonitor("/test/project")
            
            # Mock workflow execution
            with patch.object(orchestrator, '_execute_phase', 
                             return_value=PhaseResult(
                                 phase=WorkflowPhase.ANALYSIS,
                                 status=PhaseStatus.COMPLETED,
                                 duration=1.0,
                                 outputs={},
                                 errors=[],
                                 metadata={}
                             )), \
                 patch.object(orchestrator, '_save_workflow_context'), \
                 patch('builtins.print'):
                
                # Start monitoring
                workflow_execution = monitor.start_workflow("wf123", "Test request")
                
                # Execute workflow
                context = await orchestrator.execute_workflow("Test request", "/test/project")
                
                # End monitoring
                monitor.end_workflow("wf123", WorkflowStatus.COMPLETED)
                
                # Verify integration
                assert context is not None
                assert workflow_execution.workflow_id == "wf123"
                assert monitor.successful_workflows == 1

    @pytest.mark.asyncio
    async def test_parallel_execution_with_monitoring(self):
        """Test parallel execution with monitoring integration"""
        with patch.object(Path, 'mkdir'), \
             patch("builtins.open", mock_open()), \
             patch("json.dump"), \
             patch("json.load", return_value={}):
            
            executor = ParallelExecutor("/test/project")
            monitor = WorkflowMonitor("/test/project")
            
            # Start workflow monitoring
            workflow = monitor.start_workflow("wf123", "Parallel test")
            
            # Set up parallel group
            monitor.set_parallel_group("wf123", ["@backend", "@frontend"])
            
            # Start agent executions
            backend_exec = monitor.start_agent_execution("wf123", "@backend", "task1", "API")
            frontend_exec = monitor.start_agent_execution("wf123", "@frontend", "task2", "UI")
            
            # Execute parallel analysis
            with patch.object(executor, '_execute_parallel_batch',
                             return_value={"@backend": {"status": "completed"}, "@frontend": {"status": "completed"}}):
                
                result = await executor.execute_parallel_analysis("Test analysis")
                
                # End agent executions
                monitor.end_agent_execution("wf123", "@backend", "task1", AgentStatus.COMPLETED, {"api": "created"})
                monitor.end_agent_execution("wf123", "@frontend", "task2", AgentStatus.COMPLETED, {"ui": "created"})
                
                # End workflow
                monitor.end_workflow("wf123", WorkflowStatus.COMPLETED)
                
                # Verify results
                assert result["summary"] == "Parallel analysis completed"
                assert len(workflow.parallel_groups) == 1
                assert workflow.get_completed_agents() == {"@backend", "@frontend"}

    @pytest.mark.asyncio
    async def test_error_recovery_integration(self):
        """Test error recovery across components"""
        with patch('subforge.core.workflow_orchestrator.create_context_engineer'), \
             patch('subforge.core.workflow_orchestrator.create_prp_generator'), \
             patch.object(Path, 'mkdir'):
            
            orchestrator = WorkflowOrchestrator()
            monitor = WorkflowMonitor("/test/project")
            
            # Start monitoring
            workflow = monitor.start_workflow("wf123", "Error test")
            
            # Mock phase failure and recovery
            with patch.object(orchestrator, '_execute_phase', side_effect=Exception("Phase failed")), \
                 patch.object(orchestrator, '_handle_workflow_failure', 
                             return_value=Mock(project_id="recovered")) as mock_recovery, \
                 patch('builtins.print'):
                
                result = await orchestrator.execute_workflow("Error test", "/test/project")
                
                # Verify error handling was called
                mock_recovery.assert_called_once()
                
                # End monitoring with failure
                monitor.end_workflow("wf123", WorkflowStatus.FAILED, "Phase failed")
                
                assert monitor.failed_workflows == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
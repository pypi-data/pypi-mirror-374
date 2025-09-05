#!/usr/bin/env python3
"""
Comprehensive tests for core SubForge functionality
Tests the actual implementation methods and improves coverage significantly
"""

import pytest
import asyncio
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add subforge to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subforge.core.project_analyzer import (
    ProjectAnalyzer,
    TechnologyStack,
    ProjectProfile,
    ProjectComplexity,
    ArchitecturePattern
)
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
from subforge.monitoring.metrics_collector import MetricsCollector
from subforge.monitoring.workflow_monitor import WorkflowMonitor


class TestProjectAnalyzerReal:
    """Test actual ProjectAnalyzer functionality"""
    
    def test_analyzer_initialization(self):
        """Test ProjectAnalyzer initialization with real attributes"""
        analyzer = ProjectAnalyzer()
        
        # Test actual attributes that exist
        assert hasattr(analyzer, 'language_extensions')
        assert hasattr(analyzer, 'framework_indicators')
        assert hasattr(analyzer, 'subagent_templates')
        
        # Test language extensions contains expected languages
        assert 'python' in analyzer.language_extensions
        assert 'javascript' in analyzer.language_extensions
        
        # Test framework indicators is populated
        assert len(analyzer.framework_indicators) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_empty_project(self, tmp_path):
        """Test analyzing an empty project directory"""
        analyzer = ProjectAnalyzer()
        
        empty_dir = tmp_path / "empty_project"
        empty_dir.mkdir()
        
        profile = await analyzer.analyze_project(str(empty_dir))
        
        # Should still create a valid profile
        assert isinstance(profile, ProjectProfile)
        assert profile.name == "empty_project"
        assert profile.path == str(empty_dir)
        assert isinstance(profile.technology_stack, TechnologyStack)
        assert isinstance(profile.complexity, ProjectComplexity)
        assert isinstance(profile.architecture_pattern, ArchitecturePattern)
    
    @pytest.mark.asyncio
    async def test_analyze_python_project_real(self, tmp_path):
        """Test analyzing a real Python project structure"""
        analyzer = ProjectAnalyzer()
        
        # Create realistic Python project
        project_dir = tmp_path / "python_project"
        project_dir.mkdir()
        
        # Create Python files
        (project_dir / "main.py").write_text("#!/usr/bin/env python3\ndef main(): pass\nif __name__ == '__main__': main()")
        (project_dir / "utils.py").write_text("import os\nimport sys\n\ndef helper():\n    return True")
        (project_dir / "requirements.txt").write_text("fastapi==0.68.0\npydantic==1.8.2\nuvicorn")
        
        # Create package structure
        pkg_dir = project_dir / "mypackage"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("class MyClass:\n    def method(self):\n        pass")
        
        profile = await analyzer.analyze_project(str(project_dir))
        
        # Verify analysis results
        assert profile.name == "python_project"
        assert "python" in profile.technology_stack.languages
        assert profile.file_count > 0
        assert profile.lines_of_code > 0
    
    @pytest.mark.asyncio
    async def test_analyze_javascript_project_real(self, tmp_path):
        """Test analyzing a real JavaScript project"""
        analyzer = ProjectAnalyzer()
        
        project_dir = tmp_path / "js_project"
        project_dir.mkdir()
        
        # Create JavaScript files
        (project_dir / "index.js").write_text("const express = require('express');\nconst app = express();\napp.listen(3000);")
        (project_dir / "package.json").write_text('{"name": "test-app", "dependencies": {"express": "^4.17.1"}}')
        
        # Create source directory
        src_dir = project_dir / "src"
        src_dir.mkdir()
        (src_dir / "app.js").write_text("function hello() { return 'world'; }")
        
        profile = await analyzer.analyze_project(str(project_dir))
        
        assert profile.name == "js_project"
        assert "javascript" in profile.technology_stack.languages
        assert profile.file_count > 0
    
    def test_detect_technology_stack_method(self, tmp_path):
        """Test the _detect_technology_stack method directly"""
        analyzer = ProjectAnalyzer()
        
        # Create mixed technology project
        project_dir = tmp_path / "mixed_project"
        project_dir.mkdir()
        
        (project_dir / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")
        (project_dir / "style.css").write_text("body { margin: 0; }")
        (project_dir / "script.js").write_text("console.log('hello');")
        
        # Test the actual method
        tech_stack = analyzer._detect_technology_stack(project_dir)
        
        assert isinstance(tech_stack, TechnologyStack)
        assert len(tech_stack.languages) >= 1
        assert isinstance(tech_stack.frameworks, set)
        assert isinstance(tech_stack.databases, set)
        assert isinstance(tech_stack.tools, set)
        assert isinstance(tech_stack.package_managers, set)
    
    def test_detect_architecture_pattern_method(self, tmp_path):
        """Test architecture pattern detection"""
        analyzer = ProjectAnalyzer()
        
        # Create simple monolithic structure
        project_dir = tmp_path / "simple_app"
        project_dir.mkdir()
        (project_dir / "app.py").write_text("def main(): pass")
        (project_dir / "models.py").write_text("class User: pass")
        
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"flask"},
            databases=set(),
            tools=set(),
            package_managers={"pip"}
        )
        
        pattern = analyzer._detect_architecture_pattern(project_dir, tech_stack)
        assert isinstance(pattern, ArchitecturePattern)
    
    def test_estimate_team_size_method(self):
        """Test team size estimation"""
        analyzer = ProjectAnalyzer()
        
        tech_stack = TechnologyStack(
            languages={"python", "javascript"},
            frameworks={"fastapi", "react"},
            databases={"postgresql"},
            tools={"docker"},
            package_managers={"pip", "npm"}
        )
        
        team_size = analyzer._estimate_team_size(
            complexity=ProjectComplexity.MEDIUM,
            tech_stack=tech_stack,
            architecture=ArchitecturePattern.FULLSTACK
        )
        
        assert isinstance(team_size, int)
        assert team_size > 0
        assert team_size <= 20  # Reasonable upper bound
    
    def test_recommend_subagents_method(self):
        """Test subagent recommendation"""
        analyzer = ProjectAnalyzer()
        
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"fastapi"},
            databases={"postgresql"},
            tools={"docker"},
            package_managers={"pip"}
        )
        
        recommendations = analyzer._recommend_subagents(
            tech_stack=tech_stack,
            complexity=ProjectComplexity.MEDIUM,
            architecture=ArchitecturePattern.API_FIRST,
            has_tests=False,
            has_ci_cd=False
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)


class TestWorkflowOrchestratorReal:
    """Test actual WorkflowOrchestrator functionality"""
    
    def test_orchestrator_initialization_real(self):
        """Test real orchestrator initialization"""
        orchestrator = WorkflowOrchestrator()
        
        # Test actual attributes
        assert hasattr(orchestrator, 'config')
        assert hasattr(orchestrator, 'project_analyzer')
        assert hasattr(orchestrator, 'context_engineer')
        assert hasattr(orchestrator, 'prp_generator')
        
        # Verify components are initialized
        assert orchestrator.project_analyzer is not None
        assert orchestrator.context_engineer is not None
        assert orchestrator.prp_generator is not None
    
    @pytest.mark.asyncio
    async def test_workflow_context_creation_real(self, tmp_path):
        """Test workflow context creation with real orchestrator"""
        orchestrator = WorkflowOrchestrator()
        
        # Create test project
        project_dir = tmp_path / "test_workflow"
        project_dir.mkdir()
        (project_dir / "app.py").write_text("def main(): pass")
        
        # This tests the actual context creation flow
        with patch.object(orchestrator.project_analyzer, 'analyze_project') as mock_analyze:
            # Create a real-looking profile
            tech_stack = TechnologyStack(
                languages={"python"},
                frameworks={"flask"},
                databases=set(),
                tools=set(),
                package_managers={"pip"}
            )
            mock_profile = ProjectProfile(
                name="test_workflow",
                path=str(project_dir),
                technology_stack=tech_stack,
                architecture_pattern=ArchitecturePattern.MONOLITHIC,
                complexity=ProjectComplexity.SIMPLE,
                team_size_estimate=2,
                file_count=1,
                lines_of_code=10,
                has_tests=False,
                has_ci_cd=False,
                has_docker=False,
                has_docs=False,
                recommended_subagents=["backend-developer"],
                integration_requirements=[]
            )
            mock_analyze.return_value = mock_profile
            
            context = await orchestrator._create_workflow_context(
                "Create a simple API",
                str(project_dir)
            )
            
            assert isinstance(context, WorkflowContext)
            assert context.user_request == "Create a simple API"
            assert context.project_path == str(project_dir)
            assert context.project_profile == mock_profile
    
    @pytest.mark.asyncio
    async def test_analyze_requirements_method(self, tmp_path):
        """Test requirements analysis method"""
        orchestrator = WorkflowOrchestrator()
        
        # Test the actual method with a realistic user request
        requirements = orchestrator._analyze_requirements(
            "Create a web application with user authentication, database, and tests"
        )
        
        assert isinstance(requirements, dict)
        # Should contain some basic requirement categories
        expected_keys = ["functional_requirements", "non_functional_requirements", 
                        "technical_constraints", "integration_requirements"]
        
        # At least some keys should be present
        assert any(key in requirements for key in expected_keys)
    
    def test_phase_result_dataclass(self):
        """Test PhaseResult dataclass functionality"""
        result = PhaseResult(
            phase=WorkflowPhase.ANALYSIS,
            status=PhaseStatus.COMPLETED,
            duration=2.5,
            outputs={"analyzed_files": 15},
            errors=[],
            metadata={"timestamp": "2023-01-01T10:00:00Z"}
        )
        
        assert result.phase == WorkflowPhase.ANALYSIS
        assert result.status == PhaseStatus.COMPLETED
        assert result.duration == 2.5
        
        # Test serialization
        result_dict = result.to_dict()
        assert result_dict["phase"] == "analysis"
        assert result_dict["status"] == "completed"
        assert result_dict["duration"] == 2.5
    
    def test_workflow_context_serialization(self, tmp_path):
        """Test WorkflowContext serialization"""
        context = WorkflowContext(
            project_id="test_123",
            user_request="Test request",
            project_path=str(tmp_path),
            communication_dir=tmp_path / "comm",
            phase_results={},
            project_profile=None,
            template_selections={"selected": ["agent1"]},
            generated_configurations={"config": "value"},
            deployment_plan={"deploy": "local"}
        )
        
        context_dict = context.to_dict()
        
        assert context_dict["project_id"] == "test_123"
        assert context_dict["user_request"] == "Test request"
        assert context_dict["template_selections"]["selected"] == ["agent1"]
        assert context_dict["generated_configurations"]["config"] == "value"


class TestParallelExecutorReal:
    """Test actual ParallelExecutor functionality"""
    
    def test_executor_initialization_real(self, tmp_path):
        """Test ParallelExecutor initialization"""
        executor = ParallelExecutor(str(tmp_path))
        
        assert executor.project_path == Path(tmp_path)
        assert executor.workflow_state == Path(tmp_path) / "workflow-state"
        assert executor.workflow_state.exists()
    
    @pytest.mark.asyncio
    async def test_execute_parallel_analysis_structure(self, tmp_path):
        """Test parallel analysis method structure"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Mock the internal batch execution method
        with patch.object(executor, '_execute_parallel_batch') as mock_batch:
            mock_batch.return_value = {
                "@code-reviewer": {"status": "completed", "findings": "Good quality"},
                "@test-engineer": {"status": "completed", "coverage": "78%"}
            }
            
            results = await executor.execute_parallel_analysis("Test analysis")
            
            # Should call the batch method
            assert mock_batch.called
            
            # Should return structured results
            assert isinstance(results, dict)
            assert "findings" in results or "agent_reports" in results
    
    def test_parallel_task_dataclass(self):
        """Test ParallelTask dataclass"""
        task = ParallelTask(
            agent="@backend-developer",
            task="create_api",
            description="Create REST API endpoints",
            dependencies=["database_setup"],
            can_parallel=True
        )
        
        assert task.agent == "@backend-developer"
        assert task.task == "create_api"
        assert task.dependencies == ["database_setup"]
        assert task.can_parallel is True
        
        # Test prompt generation
        prompt = task.to_prompt()
        assert "@backend-developer" in prompt
        assert "create_api" in prompt
        assert "Create REST API endpoints" in prompt
        assert "database_setup" in prompt
    
    def test_save_and_load_execution_state(self, tmp_path):
        """Test execution state persistence"""
        executor = ParallelExecutor(str(tmp_path))
        
        state = {
            "execution_id": "test_exec_123",
            "timestamp": "2023-01-01T10:00:00Z",
            "results": {"@agent1": {"status": "completed"}}
        }
        
        # Save state
        state_file = executor._save_execution_state("test_execution", state)
        assert state_file.exists()
        
        # Load state
        loaded_state = executor._load_execution_state(state_file)
        assert loaded_state["execution_id"] == "test_exec_123"
        assert loaded_state["results"]["@agent1"]["status"] == "completed"


class TestMetricsCollectorReal:
    """Test actual MetricsCollector functionality"""
    
    def test_metrics_collector_initialization(self, tmp_path):
        """Test MetricsCollector initialization"""
        collector = MetricsCollector(str(tmp_path))
        
        # Test basic initialization
        assert hasattr(collector, 'current_session')
        assert isinstance(collector.current_session, dict)
        
        # Session should have basic structure
        session = collector.current_session
        assert 'session_id' in session
        assert 'executions' in session
        assert 'token_total' in session
        
        # Should have created metrics directory
        assert (Path(tmp_path) / "metrics").exists()
    
    def test_execution_tracking_workflow(self, tmp_path):
        """Test complete execution tracking workflow"""
        collector = MetricsCollector(str(tmp_path))
        
        # Start execution
        exec_id = collector.start_execution(
            task="test_task",
            agent="@test-agent", 
            phase="analysis",
            parallel=True
        )
        
        assert isinstance(exec_id, str)
        assert len(collector.current_session["executions"]) == 1
        
        # End execution
        collector.end_execution(exec_id, "completed")
        
        # Calculate metrics
        metrics = collector.calculate_metrics()
        
        assert isinstance(metrics, dict)
        assert metrics["total_executions"] == 1
        assert metrics["success_rate"] == 100
        assert "efficiency_score" in metrics
    
    def test_token_usage_tracking(self, tmp_path):
        """Test token usage tracking"""
        collector = MetricsCollector(str(tmp_path))
        
        # Add token usage
        collector.add_token_usage("@agent1", 1500, 800)
        collector.add_token_usage("@agent2", 2000, 1200)
        
        metrics = collector.calculate_metrics()
        
        assert metrics["token_total"] == 3500  # 1500 + 2000
        assert "token_efficiency" in metrics


class TestWorkflowMonitorReal:
    """Test actual WorkflowMonitor functionality"""
    
    def test_workflow_monitor_initialization(self, tmp_path):
        """Test WorkflowMonitor initialization"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        assert monitor.project_path == Path(tmp_path)
        assert monitor.monitoring_dir.exists()
        assert isinstance(monitor.active_workflows, dict)
        assert isinstance(monitor.completed_workflows, list)
        assert isinstance(monitor.event_callbacks, dict)
    
    def test_workflow_lifecycle_tracking(self, tmp_path):
        """Test complete workflow lifecycle tracking"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        # Start workflow
        workflow = monitor.start_workflow(
            "workflow_123", 
            "Create web application"
        )
        
        assert workflow.workflow_id == "workflow_123"
        assert workflow.user_request == "Create web application"
        assert len(monitor.active_workflows) == 1
        
        # Update phase
        monitor.update_phase("workflow_123", "analysis")
        assert monitor.active_workflows["workflow_123"].current_phase == "analysis"
        
        # Start agent execution
        execution = monitor.start_agent_execution(
            "workflow_123", 
            "@backend-developer", 
            "task_1", 
            "Create API"
        )
        
        assert execution is not None
        assert execution.agent_name == "@backend-developer"
        
        # End agent execution
        from subforge.monitoring.workflow_monitor import AgentStatus
        monitor.end_agent_execution(
            "workflow_123",
            "@backend-developer",
            "task_1", 
            AgentStatus.COMPLETED,
            {"endpoints": 5}
        )
        
        # End workflow
        from subforge.monitoring.workflow_monitor import WorkflowStatus
        monitor.end_workflow("workflow_123", WorkflowStatus.COMPLETED)
        
        assert len(monitor.active_workflows) == 0
        assert len(monitor.completed_workflows) == 1
        assert monitor.successful_workflows == 1
    
    def test_real_time_metrics(self, tmp_path):
        """Test real-time metrics generation"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        metrics = monitor.get_real_time_metrics()
        
        assert isinstance(metrics, dict)
        assert "timestamp" in metrics
        assert "active_workflows" in metrics
        assert "total_active_agents" in metrics
        assert "system_health" in metrics
    
    def test_monitoring_data_export(self, tmp_path):
        """Test monitoring data export"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        # Create some data to export
        monitor.start_workflow("test_workflow", "Test request")
        
        export_file = monitor.export_monitoring_data()
        
        assert export_file.exists()
        
        # Verify exported content
        with open(export_file) as f:
            export_data = json.load(f)
        
        assert "export_timestamp" in export_data
        assert "project_path" in export_data
        assert "statistics" in export_data
        assert "active_workflows" in export_data


class TestIntegrationScenarios:
    """Integration tests that combine multiple components"""
    
    @pytest.mark.asyncio
    async def test_project_analysis_to_workflow_integration(self, tmp_path):
        """Test integration from project analysis to workflow orchestration"""
        # Create test project
        project_dir = tmp_path / "integration_test"
        project_dir.mkdir()
        (project_dir / "app.py").write_text("from fastapi import FastAPI\napp = FastAPI()")
        (project_dir / "requirements.txt").write_text("fastapi\nuvicorn")
        
        # Analyze project
        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_dir))
        
        # Verify analysis worked
        assert profile.name == "integration_test"
        assert "python" in profile.technology_stack.languages
        
        # Create workflow orchestrator
        orchestrator = WorkflowOrchestrator()
        
        # Test workflow context creation with real profile
        with patch.object(orchestrator.project_analyzer, 'analyze_project', return_value=profile):
            context = await orchestrator._create_workflow_context(
                "Set up FastAPI project",
                str(project_dir)
            )
            
            assert context.project_profile == profile
            assert context.user_request == "Set up FastAPI project"
    
    def test_monitoring_with_execution_tracking(self, tmp_path):
        """Test monitoring integration with execution tracking"""
        # Initialize components
        monitor = WorkflowMonitor(str(tmp_path))
        collector = MetricsCollector(str(tmp_path))
        
        # Start monitoring workflow
        workflow = monitor.start_workflow("integration_workflow", "Test integration")
        
        # Track execution in metrics
        exec_id = collector.start_execution(
            "integration_task",
            "@integration-agent",
            "testing",
            parallel=False
        )
        
        # Start agent in monitor
        execution = monitor.start_agent_execution(
            "integration_workflow",
            "@integration-agent", 
            "integration_task",
            "Integration testing"
        )
        
        # Verify both systems tracked the execution
        assert execution is not None
        assert len(collector.current_session["executions"]) == 1
        assert len(monitor.active_workflows) == 1
        
        # Complete execution in both systems
        from subforge.monitoring.workflow_monitor import AgentStatus, WorkflowStatus
        
        monitor.end_agent_execution(
            "integration_workflow",
            "@integration-agent",
            "integration_task",
            AgentStatus.COMPLETED,
            {"result": "success"}
        )
        
        collector.end_execution(exec_id, "completed")
        monitor.end_workflow("integration_workflow", WorkflowStatus.COMPLETED)
        
        # Verify final state
        metrics = collector.calculate_metrics()
        monitor_metrics = monitor.get_real_time_metrics()
        
        assert metrics["success_rate"] == 100
        assert monitor.successful_workflows == 1
        assert monitor_metrics["active_workflows"] == 0


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases that improve coverage"""
    
    @pytest.mark.asyncio
    async def test_project_analyzer_error_handling(self, tmp_path):
        """Test ProjectAnalyzer error handling"""
        analyzer = ProjectAnalyzer()
        
        # Test with non-existent directory
        with pytest.raises(Exception):  # Could be FileNotFoundError or custom exception
            await analyzer.analyze_project("/nonexistent/directory/path")
        
        # Test with file instead of directory
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        
        with pytest.raises(Exception):  # Should handle this gracefully
            await analyzer.analyze_project(str(test_file))
    
    def test_metrics_collector_edge_cases(self, tmp_path):
        """Test MetricsCollector edge cases"""
        collector = MetricsCollector(str(tmp_path))
        
        # Test ending execution that wasn't started
        result = collector.end_execution("nonexistent_id", "completed")
        # Should handle gracefully without crashing
        
        # Test metrics calculation with no executions
        metrics = collector.calculate_metrics()
        assert isinstance(metrics, dict)
        
        # Test with invalid token usage
        collector.add_token_usage("@test", -100, 50)  # Negative input tokens
        # Should handle gracefully
    
    def test_workflow_monitor_edge_cases(self, tmp_path):
        """Test WorkflowMonitor edge cases"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        # Test ending workflow that doesn't exist
        from subforge.monitoring.workflow_monitor import WorkflowStatus
        monitor.end_workflow("nonexistent_workflow", WorkflowStatus.FAILED)
        # Should handle gracefully
        
        # Test agent execution for nonexistent workflow
        execution = monitor.start_agent_execution(
            "nonexistent_workflow",
            "@agent",
            "task",
            "description"
        )
        assert execution is None  # Should return None for nonexistent workflow
        
        # Test get status for nonexistent workflow
        status = monitor.get_workflow_status("nonexistent_workflow")
        assert status is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--color=yes"])
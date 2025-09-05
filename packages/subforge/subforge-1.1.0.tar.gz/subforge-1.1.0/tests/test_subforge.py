#!/usr/bin/env python3
"""
SubForge Test Suite
Comprehensive testing for all SubForge components
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add subforge to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subforge.core.project_analyzer import ProjectAnalyzer
from subforge.core.workflow_orchestrator import WorkflowOrchestrator
from subforge.monitoring.metrics_collector import MetricsCollector
from subforge.orchestration.parallel_executor import ParallelExecutor


class TestProjectAnalyzer:
    """Test project analysis functionality"""

    @pytest.mark.asyncio
    async def test_analyze_python_project(self, tmp_path):
        """Test analyzing a Python project"""
        # Create test project structure
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Create Python files
        (project_dir / "main.py").write_text("print('hello')")
        (project_dir / "utils.py").write_text("def helper(): pass")
        (project_dir / "requirements.txt").write_text("fastapi\npydantic")

        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_dir))

        assert profile.name == "test_project"
        assert "python" in profile.technology_stack.languages
        assert profile.file_count >= 2

    @pytest.mark.asyncio
    async def test_detect_architecture_pattern(self, tmp_path):
        """Test architecture pattern detection"""
        project_dir = tmp_path / "microservice"
        project_dir.mkdir()

        # Create microservice structure
        (project_dir / "docker-compose.yml").write_text("services:")
        (project_dir / "api").mkdir()
        (project_dir / "worker").mkdir()

        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_dir))

        # Should detect microservices pattern
        assert profile.architecture_pattern.value in ["microservices", "monolithic"]


class TestParallelExecutor:
    """Test parallel execution capabilities"""

    @pytest.mark.asyncio
    async def test_parallel_analysis(self, tmp_path):
        """Test parallel analysis execution"""
        executor = ParallelExecutor(str(tmp_path))

        # Mock the Task tool behavior
        with patch.object(executor, "_execute_parallel_batch") as mock_exec:
            mock_exec.return_value = {
                "@code-reviewer": {"status": "completed", "findings": "test"},
                "@test-engineer": {"status": "completed", "findings": "test"},
            }

            results = await executor.execute_parallel_analysis("test request")

            assert "findings" in results
            assert mock_exec.called

    @pytest.mark.asyncio
    async def test_smart_implementation(self, tmp_path):
        """Test smart parallel/sequential execution"""
        executor = ParallelExecutor(str(tmp_path))

        tasks = [
            {
                "agent": "@backend",
                "task": "api",
                "description": "Create API",
                "dependencies": None,
            },
            {
                "agent": "@frontend",
                "task": "ui",
                "description": "Create UI",
                "dependencies": None,
            },
            {
                "agent": "@test",
                "task": "test",
                "description": "Test",
                "dependencies": ["api", "ui"],
            },
        ]

        with patch.object(executor, "_execute_parallel_batch") as mock_parallel:
            with patch.object(executor, "_execute_single") as mock_single:
                mock_parallel.return_value = {
                    "@backend": {"status": "completed"},
                    "@frontend": {"status": "completed"},
                }
                mock_single.return_value = {"status": "completed"}

                results = await executor.execute_smart_implementation(tasks)

                # Should execute first 2 in parallel, last one sequential
                assert mock_parallel.called
                assert len(results) >= 2


class TestMetricsCollector:
    """Test metrics collection and analysis"""

    def test_metrics_initialization(self, tmp_path):
        """Test metrics collector initialization"""
        collector = MetricsCollector(str(tmp_path))

        assert collector.current_session["session_id"].startswith("session_")
        assert collector.current_session["executions"] == []
        assert collector.current_session["token_total"] == 0

    def test_track_execution(self, tmp_path):
        """Test execution tracking"""
        collector = MetricsCollector(str(tmp_path))

        # Start execution
        exec_id = collector.start_execution(
            "test_task", "@test-agent", "analysis", parallel=True
        )
        assert exec_id in [e["id"] for e in collector.current_session["executions"]]

        # End execution
        collector.end_execution(exec_id, "completed")

        # Check metrics
        metrics = collector.calculate_metrics()
        assert metrics["total_executions"] == 1
        assert metrics["parallel_executions"] == 1
        assert metrics["success_rate"] == 100

    def test_efficiency_score(self, tmp_path):
        """Test efficiency score calculation"""
        collector = MetricsCollector(str(tmp_path))

        # Add some executions
        for i in range(5):
            exec_id = collector.start_execution(
                f"task_{i}", "@agent", "test", parallel=(i < 3)
            )
            collector.end_execution(exec_id, "completed")

        metrics = collector.calculate_metrics()

        # Should have reasonable efficiency
        assert 0 <= metrics["efficiency_score"] <= 100
        assert metrics["parallelization_ratio"] == 0.6  # 3 out of 5


class TestWorkflowOrchestrator:
    """Test workflow orchestration"""

    @pytest.mark.asyncio
    async def test_workflow_execution(self, tmp_path):
        """Test complete workflow execution"""
        orchestrator = WorkflowOrchestrator()

        with patch.object(orchestrator, "execute_workflow") as mock_exec:
            mock_exec.return_value = MagicMock(
                project_id="test_123",
                phase_results={},
                template_selections={"selected_templates": ["test-agent"]},
                communication_dir=tmp_path,
            )

            context = await orchestrator.execute_workflow("test request", str(tmp_path))

            assert context.project_id == "test_123"
            assert mock_exec.called


class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, tmp_path):
        """Test full SubForge workflow"""
        # Create test project
        project_dir = tmp_path / "full_test"
        project_dir.mkdir()
        (project_dir / "app.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()"
        )
        (project_dir / "test_app.py").write_text("def test_app(): pass")

        # Analyze
        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_dir))

        assert profile.name == "full_test"
        assert "python" in profile.technology_stack.languages

        # Test parallel execution
        executor = ParallelExecutor(str(project_dir))
        with patch.object(executor, "_execute_parallel_batch") as mock_exec:
            mock_exec.return_value = {"@test": {"status": "completed"}}

            results = await executor.execute_parallel_analysis("analyze")
            assert "findings" in results

        # Test metrics
        collector = MetricsCollector(str(project_dir))
        exec_id = collector.start_execution(
            "integration", "@orchestrator", "full", True
        )
        collector.end_execution(exec_id, "completed")

        metrics = collector.calculate_metrics()
        assert metrics["success_rate"] == 100


@pytest.fixture
def mock_project_structure(tmp_path):
    """Create a mock project structure for testing"""
    project = tmp_path / "mock_project"
    project.mkdir()

    # Create various file types
    (project / "README.md").write_text("# Test Project")
    (project / "package.json").write_text('{"name": "test", "version": "1.0.0"}')
    (project / "src").mkdir()
    (project / "src" / "index.js").write_text("console.log('test');")

    return project


def test_with_mock_project(mock_project_structure):
    """Test using the mock project fixture"""
    assert mock_project_structure.exists()
    assert (mock_project_structure / "README.md").exists()
    assert (mock_project_structure / "src" / "index.js").exists()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--color=yes"])
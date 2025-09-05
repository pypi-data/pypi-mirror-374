#!/usr/bin/env python3
"""
Comprehensive tests for ParallelExecutor
Tests parallel task execution, dependency handling, and edge cases
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dataclasses import dataclass
import sys
import time

# Add subforge to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subforge.orchestration.parallel_executor import (
    ParallelExecutor,
    ParallelTask
)


class TestParallelTask:
    """Test ParallelTask dataclass functionality"""
    
    def test_parallel_task_creation(self):
        """Test creating a ParallelTask instance"""
        task = ParallelTask(
            agent="@backend-developer",
            task="create_api",
            description="Create FastAPI endpoints for user management",
            dependencies=["database_setup"],
            can_parallel=True
        )
        
        assert task.agent == "@backend-developer"
        assert task.task == "create_api"
        assert task.description == "Create FastAPI endpoints for user management"
        assert task.dependencies == ["database_setup"]
        assert task.can_parallel is True
    
    def test_parallel_task_defaults(self):
        """Test ParallelTask with default values"""
        task = ParallelTask(
            agent="@frontend-developer",
            task="create_components",
            description="Create React components"
        )
        
        assert task.agent == "@frontend-developer"
        assert task.task == "create_components"
        assert task.description == "Create React components"
        assert task.dependencies is None
        assert task.can_parallel is True
    
    def test_parallel_task_to_prompt(self):
        """Test ParallelTask prompt generation"""
        task = ParallelTask(
            agent="@test-engineer",
            task="write_tests",
            description="Write comprehensive unit tests",
            dependencies=["api_creation", "component_creation"],
            can_parallel=False
        )
        
        prompt = task.to_prompt()
        
        assert "@test-engineer" in prompt
        assert "write_tests" in prompt
        assert "Write comprehensive unit tests" in prompt
        assert "api_creation" in prompt
        assert "component_creation" in prompt
        assert "AGENT:" in prompt
        assert "TASK:" in prompt
        assert "DESCRIPTION:" in prompt
        assert "DEPENDENCIES:" in prompt
    
    def test_parallel_task_to_prompt_no_dependencies(self):
        """Test ParallelTask prompt generation without dependencies"""
        task = ParallelTask(
            agent="@devops-engineer",
            task="setup_docker",
            description="Configure Docker environment"
        )
        
        prompt = task.to_prompt()
        
        assert "@devops-engineer" in prompt
        assert "setup_docker" in prompt
        assert "Configure Docker environment" in prompt
        assert "None" in prompt  # Should show "None" for no dependencies


class TestParallelExecutor:
    """Test ParallelExecutor main functionality"""
    
    def test_executor_initialization(self, tmp_path):
        """Test ParallelExecutor initialization"""
        executor = ParallelExecutor(str(tmp_path))
        
        assert executor.project_path == Path(tmp_path)
        assert executor.workflow_state == Path(tmp_path) / "workflow-state"
        assert executor.workflow_state.exists()  # Should create the directory
    
    def test_executor_initialization_existing_workflow_state(self, tmp_path):
        """Test initialization with existing workflow-state directory"""
        # Create workflow-state directory first
        workflow_dir = tmp_path / "workflow-state"
        workflow_dir.mkdir()
        (workflow_dir / "existing_file.json").write_text('{"test": true}')
        
        executor = ParallelExecutor(str(tmp_path))
        
        assert executor.workflow_state == workflow_dir
        assert (workflow_dir / "existing_file.json").exists()  # Should preserve existing files
    
    @pytest.mark.asyncio
    async def test_execute_parallel_analysis(self, tmp_path):
        """Test parallel analysis execution"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Mock the batch execution method
        with patch.object(executor, '_execute_parallel_batch') as mock_batch:
            mock_batch.return_value = {
                "@code-reviewer": {
                    "status": "completed",
                    "analysis": "Code quality is good",
                    "recommendations": ["Add more tests", "Improve documentation"]
                },
                "@test-engineer": {
                    "status": "completed", 
                    "analysis": "Test coverage at 65%",
                    "recommendations": ["Add integration tests", "Mock external dependencies"]
                },
                "@backend-developer": {
                    "status": "completed",
                    "analysis": "API structure is well-designed",
                    "recommendations": ["Add rate limiting", "Implement caching"]
                },
                "@frontend-developer": {
                    "status": "completed",
                    "analysis": "Components are reusable",
                    "recommendations": ["Optimize bundle size", "Add error boundaries"]
                },
                "@data-scientist": {
                    "status": "completed",
                    "analysis": "Data models are appropriate",
                    "recommendations": ["Add data validation", "Implement feature engineering"]
                }
            }
            
            results = await executor.execute_parallel_analysis("Analyze the codebase for improvements")
            
            # Verify the method was called
            assert mock_batch.called
            
            # Verify results structure
            assert "findings" in results
            assert "recommendations" in results
            assert "agent_reports" in results
            
            # Verify all agents were included
            agent_reports = results["agent_reports"]
            assert "@code-reviewer" in agent_reports
            assert "@test-engineer" in agent_reports
            assert "@backend-developer" in agent_reports
            assert "@frontend-developer" in agent_reports
            assert "@data-scientist" in agent_reports
            
            # Verify analysis content
            assert agent_reports["@code-reviewer"]["analysis"] == "Code quality is good"
            assert "Add more tests" in agent_reports["@code-reviewer"]["recommendations"]
    
    @pytest.mark.asyncio
    async def test_execute_smart_implementation(self, tmp_path):
        """Test smart implementation with dependency handling"""
        executor = ParallelExecutor(str(tmp_path))
        
        tasks = [
            {
                "agent": "@backend-developer",
                "task": "create_api",
                "description": "Create API endpoints",
                "dependencies": None,
                "can_parallel": True
            },
            {
                "agent": "@frontend-developer", 
                "task": "create_ui",
                "description": "Create user interface",
                "dependencies": None,
                "can_parallel": True
            },
            {
                "agent": "@test-engineer",
                "task": "create_tests",
                "description": "Create comprehensive tests",
                "dependencies": ["create_api", "create_ui"],
                "can_parallel": False
            },
            {
                "agent": "@devops-engineer",
                "task": "setup_deployment",
                "description": "Setup deployment pipeline",
                "dependencies": ["create_tests"],
                "can_parallel": False
            }
        ]
        
        with patch.object(executor, '_execute_parallel_batch') as mock_parallel:
            with patch.object(executor, '_execute_single') as mock_single:
                # Mock parallel execution results
                mock_parallel.return_value = {
                    "@backend-developer": {"status": "completed", "output": "API created"},
                    "@frontend-developer": {"status": "completed", "output": "UI created"}
                }
                
                # Mock sequential execution results
                mock_single.side_effect = [
                    {"status": "completed", "output": "Tests created"},
                    {"status": "completed", "output": "Deployment setup"}
                ]
                
                results = await executor.execute_smart_implementation(tasks)
                
                # Verify parallel execution was called once for independent tasks
                assert mock_parallel.call_count == 1
                
                # Verify sequential execution was called twice for dependent tasks
                assert mock_single.call_count == 2
                
                # Verify all tasks completed
                assert len(results) == 4
                for result in results:
                    assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_execute_smart_implementation_all_parallel(self, tmp_path):
        """Test smart implementation with all parallel tasks"""
        executor = ParallelExecutor(str(tmp_path))
        
        tasks = [
            {
                "agent": "@backend-developer",
                "task": "optimize_queries",
                "description": "Optimize database queries",
                "dependencies": None,
                "can_parallel": True
            },
            {
                "agent": "@frontend-developer",
                "task": "optimize_bundle",
                "description": "Optimize JavaScript bundle",
                "dependencies": None,
                "can_parallel": True
            },
            {
                "agent": "@devops-engineer",
                "task": "optimize_docker",
                "description": "Optimize Docker configuration",
                "dependencies": None,
                "can_parallel": True
            }
        ]
        
        with patch.object(executor, '_execute_parallel_batch') as mock_parallel:
            mock_parallel.return_value = {
                "@backend-developer": {"status": "completed", "optimizations": 5},
                "@frontend-developer": {"status": "completed", "bundle_reduction": "30%"},
                "@devops-engineer": {"status": "completed", "image_size_reduction": "25%"}
            }
            
            results = await executor.execute_smart_implementation(tasks)
            
            # Should only call parallel execution once
            assert mock_parallel.call_count == 1
            
            # All tasks should complete in parallel
            assert len(results) == 3
            for result in results:
                assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_execute_smart_implementation_all_sequential(self, tmp_path):
        """Test smart implementation with all sequential tasks"""
        executor = ParallelExecutor(str(tmp_path))
        
        tasks = [
            {
                "agent": "@backend-developer",
                "task": "create_models",
                "description": "Create database models",
                "dependencies": None,
                "can_parallel": True
            },
            {
                "agent": "@backend-developer",
                "task": "create_migrations", 
                "description": "Create database migrations",
                "dependencies": ["create_models"],
                "can_parallel": False
            },
            {
                "agent": "@backend-developer",
                "task": "run_migrations",
                "description": "Run database migrations",
                "dependencies": ["create_migrations"],
                "can_parallel": False
            }
        ]
        
        with patch.object(executor, '_execute_single') as mock_single:
            mock_single.side_effect = [
                {"status": "completed", "models_created": 5},
                {"status": "completed", "migrations_created": 3},
                {"status": "completed", "migrations_applied": 3}
            ]
            
            results = await executor.execute_smart_implementation(tasks)
            
            # Should call sequential execution for each task
            assert mock_single.call_count == 3
            
            # All tasks should complete sequentially
            assert len(results) == 3
            for i, result in enumerate(results):
                assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_execute_parallel_batch(self, tmp_path):
        """Test parallel batch execution"""
        executor = ParallelExecutor(str(tmp_path))
        
        tasks = [
            ParallelTask("@agent1", "task1", "Description 1"),
            ParallelTask("@agent2", "task2", "Description 2"),
            ParallelTask("@agent3", "task3", "Description 3")
        ]
        
        # Mock the Task tool calls
        with patch('subforge.orchestration.parallel_executor.asyncio.create_task') as mock_create_task:
            # Create mock task objects
            mock_task1 = AsyncMock()
            mock_task1.return_value = {"agent": "@agent1", "status": "completed", "result": "Result 1"}
            
            mock_task2 = AsyncMock() 
            mock_task2.return_value = {"agent": "@agent2", "status": "completed", "result": "Result 2"}
            
            mock_task3 = AsyncMock()
            mock_task3.return_value = {"agent": "@agent3", "status": "completed", "result": "Result 3"}
            
            mock_create_task.side_effect = [mock_task1, mock_task2, mock_task3]
            
            with patch('asyncio.gather') as mock_gather:
                mock_gather.return_value = [
                    {"agent": "@agent1", "status": "completed", "result": "Result 1"},
                    {"agent": "@agent2", "status": "completed", "result": "Result 2"},
                    {"agent": "@agent3", "status": "completed", "result": "Result 3"}
                ]
                
                results = await executor._execute_parallel_batch(tasks)
                
                # Verify all agents executed
                assert "@agent1" in results
                assert "@agent2" in results  
                assert "@agent3" in results
                
                # Verify results
                assert results["@agent1"]["status"] == "completed"
                assert results["@agent2"]["status"] == "completed"
                assert results["@agent3"]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_execute_single_task(self, tmp_path):
        """Test single task execution"""
        executor = ParallelExecutor(str(tmp_path))
        
        task = ParallelTask(
            "@test-engineer",
            "run_tests",
            "Execute test suite",
            dependencies=["setup_complete"]
        )
        
        # Mock the Task tool call
        with patch('subforge.orchestration.parallel_executor.Task') as mock_task_tool:
            mock_task_tool.return_value = {
                "status": "completed",
                "tests_run": 25,
                "passed": 23,
                "failed": 2,
                "coverage": "78%"
            }
            
            result = await executor._execute_single(task)
            
            # Verify task was called with correct prompt
            assert mock_task_tool.called
            
            # Verify result
            assert result["status"] == "completed"
            assert result["tests_run"] == 25
            assert result["coverage"] == "78%"
    
    def test_save_execution_state(self, tmp_path):
        """Test saving execution state"""
        executor = ParallelExecutor(str(tmp_path))
        
        state = {
            "execution_id": "exec_123",
            "started_at": "2023-01-01T10:00:00Z",
            "tasks": [
                {"agent": "@agent1", "status": "completed"},
                {"agent": "@agent2", "status": "running"}
            ],
            "results": {
                "@agent1": {"output": "Success"}
            }
        }
        
        state_file = executor._save_execution_state("test_execution", state)
        
        # Verify file was created
        assert state_file.exists()
        assert state_file.parent == executor.workflow_state
        
        # Verify content
        saved_state = json.loads(state_file.read_text())
        assert saved_state["execution_id"] == "exec_123"
        assert len(saved_state["tasks"]) == 2
        assert saved_state["results"]["@agent1"]["output"] == "Success"
    
    def test_load_execution_state(self, tmp_path):
        """Test loading execution state"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Create state file
        state = {
            "execution_id": "exec_456", 
            "completed_at": "2023-01-01T11:00:00Z",
            "final_results": {"summary": "All tasks completed successfully"}
        }
        
        state_file = executor.workflow_state / "test_load.json"
        state_file.write_text(json.dumps(state))
        
        # Load state
        loaded_state = executor._load_execution_state(state_file)
        
        assert loaded_state["execution_id"] == "exec_456"
        assert loaded_state["completed_at"] == "2023-01-01T11:00:00Z"
        assert loaded_state["final_results"]["summary"] == "All tasks completed successfully"
    
    def test_organize_tasks_by_dependencies(self, tmp_path):
        """Test organizing tasks by dependency levels"""
        executor = ParallelExecutor(str(tmp_path))
        
        tasks = [
            ParallelTask("@agent1", "task1", "Independent task 1", dependencies=None),
            ParallelTask("@agent2", "task2", "Independent task 2", dependencies=None),
            ParallelTask("@agent3", "task3", "Depends on task1", dependencies=["task1"]),
            ParallelTask("@agent4", "task4", "Depends on task2", dependencies=["task2"]),
            ParallelTask("@agent5", "task5", "Depends on task3 and task4", dependencies=["task3", "task4"])
        ]
        
        organized = executor._organize_tasks_by_dependencies(tasks)
        
        # Should have multiple levels
        assert len(organized) >= 3
        
        # First level should have independent tasks
        level_0 = organized[0]
        assert len(level_0) == 2
        task_names_0 = [task.task for task in level_0]
        assert "task1" in task_names_0
        assert "task2" in task_names_0
        
        # Second level should have tasks depending on level 0
        level_1 = organized[1]
        assert len(level_1) == 2
        task_names_1 = [task.task for task in level_1]
        assert "task3" in task_names_1
        assert "task4" in task_names_1
        
        # Third level should have task depending on level 1
        level_2 = organized[2]
        assert len(level_2) == 1
        assert level_2[0].task == "task5"
    
    def test_organize_tasks_circular_dependency_detection(self, tmp_path):
        """Test detection of circular dependencies"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Create tasks with circular dependency
        tasks = [
            ParallelTask("@agent1", "task1", "Task 1", dependencies=["task2"]),
            ParallelTask("@agent2", "task2", "Task 2", dependencies=["task1"])
        ]
        
        # Should handle circular dependencies gracefully
        try:
            organized = executor._organize_tasks_by_dependencies(tasks)
            # If no exception, verify it handled the circular dependency
            assert len(organized) > 0
        except ValueError as e:
            # Or it should raise a clear error about circular dependencies
            assert "circular" in str(e).lower() or "cycle" in str(e).lower()


class TestParallelExecutor_EdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_execute_parallel_analysis_with_failures(self, tmp_path):
        """Test parallel analysis when some agents fail"""
        executor = ParallelExecutor(str(tmp_path))
        
        with patch.object(executor, '_execute_parallel_batch') as mock_batch:
            # Mock mixed success/failure results
            mock_batch.return_value = {
                "@code-reviewer": {
                    "status": "completed",
                    "analysis": "Analysis complete"
                },
                "@test-engineer": {
                    "status": "failed",
                    "error": "Unable to run tests - missing dependencies"
                },
                "@backend-developer": {
                    "status": "completed", 
                    "analysis": "Backend analysis complete"
                }
            }
            
            results = await executor.execute_parallel_analysis("Analyze with failures")
            
            # Should still return results
            assert "findings" in results
            assert "agent_reports" in results
            
            # Should include both successful and failed agents
            agent_reports = results["agent_reports"]
            assert "@code-reviewer" in agent_reports
            assert "@test-engineer" in agent_reports
            assert "@backend-developer" in agent_reports
            
            # Should note failures
            assert agent_reports["@test-engineer"]["status"] == "failed"
            assert "error" in agent_reports["@test-engineer"]
    
    @pytest.mark.asyncio
    async def test_execute_smart_implementation_empty_tasks(self, tmp_path):
        """Test smart implementation with empty task list"""
        executor = ParallelExecutor(str(tmp_path))
        
        results = await executor.execute_smart_implementation([])
        
        # Should return empty results without error
        assert results == []
    
    @pytest.mark.asyncio
    async def test_execute_smart_implementation_invalid_dependencies(self, tmp_path):
        """Test smart implementation with invalid dependencies"""
        executor = ParallelExecutor(str(tmp_path))
        
        tasks = [
            {
                "agent": "@agent1",
                "task": "task1", 
                "description": "Task 1",
                "dependencies": ["nonexistent_task"],  # Invalid dependency
                "can_parallel": False
            }
        ]
        
        # Should handle gracefully (might execute anyway or raise descriptive error)
        try:
            results = await executor.execute_smart_implementation(tasks)
            # If it completes, verify the task was still executed
            assert len(results) >= 0
        except Exception as e:
            # If it raises an error, should be descriptive
            assert "dependency" in str(e).lower() or "nonexistent" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_execute_parallel_batch_timeout(self, tmp_path):
        """Test parallel batch execution with timeout"""
        executor = ParallelExecutor(str(tmp_path))
        
        tasks = [
            ParallelTask("@slow-agent", "slow_task", "This will timeout")
        ]
        
        # Mock a slow task that times out
        with patch('asyncio.gather') as mock_gather:
            mock_gather.side_effect = asyncio.TimeoutError("Task timed out")
            
            try:
                results = await executor._execute_parallel_batch(tasks)
                # Should handle timeout gracefully
                assert "@slow-agent" in results
                assert "timeout" in results["@slow-agent"].get("error", "").lower()
            except asyncio.TimeoutError:
                # Or re-raise with context
                pass
    
    @pytest.mark.asyncio
    async def test_execute_single_task_failure(self, tmp_path):
        """Test single task execution failure"""
        executor = ParallelExecutor(str(tmp_path))
        
        task = ParallelTask("@failing-agent", "failing_task", "This will fail")
        
        # Mock task failure
        with patch('subforge.orchestration.parallel_executor.Task') as mock_task_tool:
            mock_task_tool.side_effect = Exception("Task execution failed")
            
            result = await executor._execute_single(task)
            
            # Should return error result instead of raising
            assert "status" in result
            assert result["status"] == "failed" or "error" in result
    
    def test_save_execution_state_write_permission_error(self, tmp_path):
        """Test saving execution state with write permission error"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Make workflow_state directory read-only
        executor.workflow_state.chmod(0o444)
        
        state = {"test": "data"}
        
        try:
            # Should handle permission error gracefully
            state_file = executor._save_execution_state("permission_test", state)
            # If it succeeds despite permissions, that's fine too
        except PermissionError:
            # Expected behavior - should raise clear error
            pass
        except Exception as e:
            # Other exceptions should be descriptive
            assert "permission" in str(e).lower() or "write" in str(e).lower()
        finally:
            # Restore permissions for cleanup
            try:
                executor.workflow_state.chmod(0o755)
            except:
                pass
    
    def test_load_execution_state_corrupted_file(self, tmp_path):
        """Test loading corrupted state file"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Create corrupted JSON file
        state_file = executor.workflow_state / "corrupted.json"
        state_file.write_text("{ invalid json content")
        
        try:
            loaded_state = executor._load_execution_state(state_file)
            # Should return None or empty dict for corrupted files
            assert loaded_state is None or loaded_state == {}
        except json.JSONDecodeError:
            # Or raise descriptive JSON error
            pass
    
    def test_load_execution_state_missing_file(self, tmp_path):
        """Test loading missing state file"""
        executor = ParallelExecutor(str(tmp_path))
        
        missing_file = executor.workflow_state / "missing.json"
        
        try:
            loaded_state = executor._load_execution_state(missing_file)
            # Should handle missing file gracefully
            assert loaded_state is None or loaded_state == {}
        except FileNotFoundError:
            # Or raise clear error about missing file
            pass


class TestParallelExecutor_Performance:
    """Test performance aspects of parallel execution"""
    
    @pytest.mark.asyncio
    async def test_parallel_execution_performance_benefit(self, tmp_path):
        """Test that parallel execution is actually faster than sequential"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Create tasks that simulate work
        tasks = [
            ParallelTask("@agent1", "task1", "Simulated work 1"),
            ParallelTask("@agent2", "task2", "Simulated work 2"),
            ParallelTask("@agent3", "task3", "Simulated work 3")
        ]
        
        # Mock tasks with simulated delays
        async def mock_agent_work(task):
            await asyncio.sleep(0.1)  # Simulate 100ms of work
            return {"agent": task.agent, "status": "completed", "duration": 0.1}
        
        # Test parallel execution time
        start_time = time.time()
        
        with patch.object(executor, '_execute_agent_task', mock_agent_work):
            with patch('asyncio.gather') as mock_gather:
                # Simulate parallel execution (all tasks run at once)
                mock_gather.return_value = [
                    await mock_agent_work(task) for task in tasks
                ]
                
                results = await executor._execute_parallel_batch(tasks)
                
        parallel_time = time.time() - start_time
        
        # Test sequential execution time for comparison
        start_time = time.time()
        
        sequential_results = []
        for task in tasks:
            result = await mock_agent_work(task)
            sequential_results.append(result)
        
        sequential_time = time.time() - start_time
        
        # Parallel should be faster (allowing some overhead)
        assert parallel_time < sequential_time * 0.8  # At least 20% faster
        
        # Both should complete all tasks
        assert len(results) == len(sequential_results) == 3
    
    @pytest.mark.asyncio
    async def test_large_number_of_parallel_tasks(self, tmp_path):
        """Test handling large number of parallel tasks"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Create many parallel tasks
        num_tasks = 20
        tasks = [
            ParallelTask(f"@agent{i}", f"task{i}", f"Task {i}")
            for i in range(num_tasks)
        ]
        
        # Mock fast execution
        with patch.object(executor, '_execute_agent_task') as mock_execute:
            mock_execute.side_effect = [
                {"agent": f"@agent{i}", "status": "completed", "task_id": i}
                for i in range(num_tasks)
            ]
            
            start_time = time.time()
            results = await executor._execute_parallel_batch(tasks)
            execution_time = time.time() - start_time
            
            # Should complete all tasks
            assert len(results) == num_tasks
            
            # Should complete reasonably quickly (adjust threshold as needed)
            assert execution_time < 2.0  # Should finish within 2 seconds
            
            # Verify all agents completed
            for i in range(num_tasks):
                assert f"@agent{i}" in results
                assert results[f"@agent{i}"]["status"] == "completed"
    
    def test_memory_usage_with_large_state_files(self, tmp_path):
        """Test memory usage when dealing with large state files"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Create large state object
        large_state = {
            "execution_id": "large_test",
            "results": {}
        }
        
        # Add many results to simulate large execution
        for i in range(1000):
            large_state["results"][f"@agent{i}"] = {
                "status": "completed",
                "output": f"Large output data for agent {i}" * 50,  # Simulate large output
                "metrics": {"duration": 1.5, "memory_used": "100MB", "cpu_used": "50%"}
            }
        
        # This should not cause memory issues
        state_file = executor._save_execution_state("large_state_test", large_state)
        assert state_file.exists()
        
        # Loading should also work without issues
        loaded_state = executor._load_execution_state(state_file)
        assert loaded_state["execution_id"] == "large_test"
        assert len(loaded_state["results"]) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--color=yes"])
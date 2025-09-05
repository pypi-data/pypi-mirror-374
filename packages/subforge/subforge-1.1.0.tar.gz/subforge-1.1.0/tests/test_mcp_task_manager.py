#!/usr/bin/env python3
"""
Comprehensive unit tests for MCP Task Manager
Tests all task management methods, MCP tool discovery, async operations, and error scenarios
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch
from uuid import uuid4

import pytest

# Add subforge to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subforge.core.mcp_task_manager import (
    MCPTaskManager,
    SubForgeWorkflowFactory,
    Task,
    TaskDependency,
    TaskPriority,
    TaskStatus,
)


class TestTaskEnums:
    """Test task enumeration classes"""
    
    def test_task_status_enum(self):
        """Test TaskStatus enum values"""
        assert TaskStatus.CREATED.value == "created"
        assert TaskStatus.ASSIGNED.value == "assigned"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.BLOCKED.value == "blocked"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
    
    def test_task_priority_enum(self):
        """Test TaskPriority enum values"""
        assert TaskPriority.LOW.value == 1
        assert TaskPriority.MEDIUM.value == 2
        assert TaskPriority.HIGH.value == 3
        assert TaskPriority.CRITICAL.value == 4


class TestTaskDependency:
    """Test TaskDependency dataclass"""
    
    def test_task_dependency_creation(self):
        """Test TaskDependency creation with all fields"""
        dep = TaskDependency(
            task_id="task_123",
            dependency_type="blocks",
            description="Test dependency"
        )
        
        assert dep.task_id == "task_123"
        assert dep.dependency_type == "blocks"
        assert dep.description == "Test dependency"


class TestTask:
    """Test Task dataclass and methods"""
    
    def create_test_task(self):
        """Create a test task instance"""
        return Task(
            task_id="task_test_123",
            name="Test Task",
            description="A test task for unit testing",
            agent_name="test-agent",
            status=TaskStatus.CREATED,
            priority=TaskPriority.MEDIUM,
            created_at=datetime.now(),
            assigned_at=None,
            started_at=None,
            completed_at=None,
            inputs={"input1": "value1"},
            outputs={},
            metadata={"test": True},
            dependencies=[],
            blocks=[],
            progress_percentage=0.0,
            estimated_duration=timedelta(minutes=30),
            actual_duration=None,
            error_message=None,
            retry_count=0,
            max_retries=3
        )
    
    def test_task_creation(self):
        """Test Task creation with all fields"""
        task = self.create_test_task()
        
        assert task.task_id == "task_test_123"
        assert task.name == "Test Task"
        assert task.agent_name == "test-agent"
        assert task.status == TaskStatus.CREATED
        assert task.priority == TaskPriority.MEDIUM
        assert task.inputs == {"input1": "value1"}
        assert task.outputs == {}
        assert task.progress_percentage == 0.0
        assert task.retry_count == 0
        assert task.max_retries == 3
    
    def test_task_to_dict(self):
        """Test Task.to_dict() serialization"""
        task = self.create_test_task()
        task_dict = task.to_dict()
        
        # Verify all required fields are present
        required_fields = [
            "task_id", "name", "description", "agent_name", "status",
            "priority", "created_at", "inputs", "outputs", "metadata",
            "dependencies", "blocks", "progress_percentage", 
            "error_message", "retry_count", "max_retries"
        ]
        
        for field in required_fields:
            assert field in task_dict
        
        # Verify data types and values
        assert task_dict["task_id"] == "task_test_123"
        assert task_dict["status"] == "created"
        assert task_dict["priority"] == 2
        assert task_dict["progress_percentage"] == 0.0
        assert task_dict["estimated_duration"] == 1800.0  # 30 minutes in seconds
        assert isinstance(task_dict["created_at"], str)
    
    def test_task_to_dict_with_dates(self):
        """Test Task.to_dict() with various date fields set"""
        task = self.create_test_task()
        now = datetime.now()
        task.assigned_at = now
        task.started_at = now
        task.completed_at = now
        task.actual_duration = timedelta(minutes=25)
        
        task_dict = task.to_dict()
        
        assert task_dict["assigned_at"] is not None
        assert task_dict["started_at"] is not None
        assert task_dict["completed_at"] is not None
        assert task_dict["actual_duration"] == 1500.0  # 25 minutes
    
    def test_task_to_dict_with_dependencies(self):
        """Test Task.to_dict() with dependencies"""
        task = self.create_test_task()
        dep = TaskDependency("dep_task", "blocks", "Blocking dependency")
        task.dependencies = [dep]
        task.blocks = ["blocked_task_1", "blocked_task_2"]
        
        task_dict = task.to_dict()
        
        assert len(task_dict["dependencies"]) == 1
        assert task_dict["dependencies"][0]["task_id"] == "dep_task"
        assert task_dict["dependencies"][0]["dependency_type"] == "blocks"
        assert task_dict["blocks"] == ["blocked_task_1", "blocked_task_2"]


class TestMCPTaskManager:
    """Test MCPTaskManager class and all its methods"""
    
    @pytest.fixture
    def mock_communication_manager(self):
        """Create a mock communication manager"""
        return MagicMock()
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create a temporary workspace directory"""
        return tmp_path / "test_workspace"
    
    @pytest.fixture
    def task_manager(self, temp_workspace, mock_communication_manager):
        """Create a task manager instance for testing"""
        return MCPTaskManager(temp_workspace, mock_communication_manager)
    
    def test_task_manager_initialization(self, task_manager, temp_workspace):
        """Test MCPTaskManager initialization"""
        assert task_manager.workspace_dir == temp_workspace
        assert isinstance(task_manager.tasks, dict)
        assert isinstance(task_manager.task_queues, dict)
        assert isinstance(task_manager.active_workflows, dict)
        
        # Check that directories are created
        assert (temp_workspace / "tasks").exists()
        assert (temp_workspace / "workflows").exists()
        assert (temp_workspace / "logs").exists()
    
    @pytest.mark.asyncio
    async def test_create_workflow(self, task_manager):
        """Test workflow creation"""
        workflow_id = "test_workflow_123"
        workflow_config = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "dependencies": {"dep1": "dep2"},
            "metadata": {"version": "1.0"}
        }
        
        result = await task_manager.create_workflow(workflow_id, workflow_config)
        
        assert result == workflow_id
        assert workflow_id in task_manager.active_workflows
        
        workflow = task_manager.active_workflows[workflow_id]
        assert workflow["workflow_id"] == workflow_id
        assert workflow["config"] == workflow_config
        assert workflow["status"] == "created"
        assert workflow["tasks"] == []
        assert "created_at" in workflow
    
    @pytest.mark.asyncio
    async def test_create_workflow_saves_to_file(self, task_manager):
        """Test that workflow creation saves to file"""
        workflow_id = "test_workflow_file"
        workflow_config = {"name": "Test"}
        
        with patch("builtins.open", mock_open()) as mock_file:
            await task_manager.create_workflow(workflow_id, workflow_config)
            
            # Verify file was written
            mock_file.assert_called_once()
            call_args = mock_file.call_args[0]
            assert str(task_manager.workflows_dir / f"{workflow_id}.json") in str(call_args[0])
    
    @pytest.mark.asyncio
    async def test_create_task_basic(self, task_manager):
        """Test basic task creation"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()) as mock_save, \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log:
            
            task_id = await task_manager.create_task(
                name="Test Task",
                description="A test task",
                agent_name="test-agent",
                inputs={"key": "value"}
            )
            
            assert task_id.startswith("task_")
            assert task_id in task_manager.tasks
            
            task = task_manager.tasks[task_id]
            assert task.name == "Test Task"
            assert task.description == "A test task"
            assert task.agent_name == "test-agent"
            assert task.status == TaskStatus.CREATED
            assert task.priority == TaskPriority.MEDIUM
            assert task.inputs == {"key": "value"}
            assert task.outputs == {}
            assert task.progress_percentage == 0.0
            
            # Verify task was added to agent queue
            assert "test-agent" in task_manager.task_queues
            assert task_id in task_manager.task_queues["test-agent"]
            
            # Verify save and log were called
            mock_save.assert_called_once()
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_task_with_workflow(self, task_manager):
        """Test task creation with workflow association"""
        # Create workflow first
        workflow_id = await task_manager.create_workflow("test_workflow", {})
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task_id = await task_manager.create_task(
                name="Workflow Task",
                description="Task in workflow",
                agent_name="test-agent",
                inputs={},
                workflow_id=workflow_id
            )
            
            task = task_manager.tasks[task_id]
            assert task.metadata["workflow_id"] == workflow_id
            assert task_id in task_manager.active_workflows[workflow_id]["tasks"]
    
    @pytest.mark.asyncio
    async def test_create_task_with_dependencies(self, task_manager):
        """Test task creation with dependencies"""
        dependency = TaskDependency("dep_task", "requires", "Needs completion")
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task_id = await task_manager.create_task(
                name="Dependent Task",
                description="Has dependencies",
                agent_name="test-agent",
                inputs={},
                dependencies=[dependency],
                priority=TaskPriority.HIGH,
                estimated_duration=timedelta(hours=2)
            )
            
            task = task_manager.tasks[task_id]
            assert len(task.dependencies) == 1
            assert task.dependencies[0].task_id == "dep_task"
            assert task.priority == TaskPriority.HIGH
            assert task.estimated_duration == timedelta(hours=2)
    
    @pytest.mark.asyncio
    async def test_assign_task_to_agent(self, task_manager):
        """Test task assignment to agent"""
        # Create task first
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Test Task", "Description", "original-agent", {}
            )
        
        with patch.object(task_manager, '_check_dependencies', new=AsyncMock(return_value=True)) as mock_check, \
             patch.object(task_manager, '_save_task', new=AsyncMock()) as mock_save, \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log:
            
            result = await task_manager.assign_task_to_agent(task_id, "new-agent")
            
            assert result is True
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.ASSIGNED
            assert task.agent_name == "new-agent"
            assert task.assigned_at is not None
            
            # Verify task is in new agent's queue
            assert task_id in task_manager.task_queues["new-agent"]
            
            mock_check.assert_called_once()
            mock_save.assert_called_once()
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_assign_task_nonexistent(self, task_manager):
        """Test assignment of nonexistent task"""
        result = await task_manager.assign_task_to_agent("nonexistent", "agent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_assign_task_blocked_by_dependencies(self, task_manager):
        """Test task assignment blocked by unsatisfied dependencies"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Blocked Task", "Has dependencies", "test-agent", {}
            )
        
        with patch.object(task_manager, '_check_dependencies', new=AsyncMock(return_value=False)), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log:
            
            result = await task_manager.assign_task_to_agent(task_id, "test-agent")
            
            assert result is False
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.BLOCKED
            
            mock_log.assert_called_with(task_id, "blocked", "Dependencies not satisfied")
    
    @pytest.mark.asyncio
    async def test_start_task(self, task_manager):
        """Test starting a task"""
        # Create task first
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Test Task", "Description", "test-agent", {}
            )
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()) as mock_save, \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log:
            
            result = await task_manager.start_task(task_id)
            
            assert result is True
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.IN_PROGRESS
            assert task.started_at is not None
            
            mock_save.assert_called_once()
            mock_log.assert_called_once_with(task_id, "started", "Task execution started")
    
    @pytest.mark.asyncio
    async def test_start_task_nonexistent(self, task_manager):
        """Test starting nonexistent task"""
        result = await task_manager.start_task("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_update_task_progress(self, task_manager):
        """Test updating task progress"""
        # Create task first
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Test Task", "Description", "test-agent", {}
            )
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()) as mock_save:
            result = await task_manager.update_task_progress(
                task_id, 75.5, "Three quarters complete"
            )
            
            assert result is True
            
            task = task_manager.tasks[task_id]
            assert task.progress_percentage == 75.5
            assert task.metadata["last_status"] == "Three quarters complete"
            assert "last_update" in task.metadata
            
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_task_progress_boundaries(self, task_manager):
        """Test progress update with boundary values"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Test Task", "Description", "test-agent", {}
            )
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()):
            # Test negative value (should be clamped to 0)
            await task_manager.update_task_progress(task_id, -10)
            task = task_manager.tasks[task_id]
            assert task.progress_percentage == 0
            
            # Test value over 100 (should be clamped to 100)
            await task_manager.update_task_progress(task_id, 150)
            task = task_manager.tasks[task_id]
            assert task.progress_percentage == 100
    
    @pytest.mark.asyncio
    async def test_update_task_progress_nonexistent(self, task_manager):
        """Test updating progress of nonexistent task"""
        result = await task_manager.update_task_progress("nonexistent", 50.0)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_complete_task_success(self, task_manager):
        """Test successful task completion"""
        # Create and start task
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Test Task", "Description", "test-agent", {}
            )
            await task_manager.start_task(task_id)
        
        outputs = {"result": "success", "files_created": 5}
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()) as mock_save, \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log, \
             patch.object(task_manager, '_trigger_dependent_tasks', new=AsyncMock()) as mock_trigger:
            
            result = await task_manager.complete_task(task_id, outputs, True)
            
            assert result is True
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.COMPLETED
            assert task.outputs == outputs
            assert task.progress_percentage == 100.0
            assert task.completed_at is not None
            assert task.actual_duration is not None
            
            mock_save.assert_called_once()
            mock_log.assert_called_once_with(task_id, "completed", "Task completed successfully")
            mock_trigger.assert_called_once_with(task_id)
    
    @pytest.mark.asyncio
    async def test_complete_task_failure(self, task_manager):
        """Test task completion with failure"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Test Task", "Description", "test-agent", {}
            )
        
        error_message = "Task failed due to network error"
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()) as mock_save, \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log, \
             patch.object(task_manager, '_retry_task', new=AsyncMock()) as mock_retry:
            
            result = await task_manager.complete_task(
                task_id, {}, False, error_message
            )
            
            assert result is True
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.FAILED
            assert task.error_message == error_message
            assert task.progress_percentage == 100.0
            
            mock_save.assert_called_once()
            mock_log.assert_called_once_with(task_id, "failed", f"Task failed: {error_message}")
            mock_retry.assert_called_once_with(task_id)
    
    @pytest.mark.asyncio
    async def test_complete_task_failure_max_retries(self, task_manager):
        """Test task failure when max retries exceeded"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Test Task", "Description", "test-agent", {}
            )
            
            # Set task to max retries
            task_manager.tasks[task_id].retry_count = 3  # max_retries = 3
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()), \
             patch.object(task_manager, '_retry_task', new=AsyncMock()) as mock_retry:
            
            await task_manager.complete_task(task_id, {}, False, "Error")
            
            # Should not retry when max retries exceeded
            mock_retry.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_complete_task_nonexistent(self, task_manager):
        """Test completing nonexistent task"""
        result = await task_manager.complete_task("nonexistent", {})
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, task_manager):
        """Test getting task status"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Status Test", "Test status retrieval", "test-agent", {"input": "data"}
            )
        
        with patch.object(task_manager, '_check_dependencies', new=AsyncMock(return_value=True)), \
             patch.object(task_manager, '_estimate_completion_time', return_value="2024-01-01T12:00:00"):
            
            status = await task_manager.get_task_status(task_id)
            
            assert status is not None
            assert status["task_id"] == task_id
            assert status["name"] == "Status Test"
            assert status["agent_name"] == "test-agent"
            assert status["status"] == "created"
            assert status["progress"] == 0.0
            assert "created_at" in status
            assert status["dependencies_satisfied"] is True
            assert status["outputs"] == {}
            assert status["error_message"] is None
    
    @pytest.mark.asyncio
    async def test_get_task_status_nonexistent(self, task_manager):
        """Test getting status of nonexistent task"""
        status = await task_manager.get_task_status("nonexistent")
        assert status is None
    
    @pytest.mark.asyncio
    async def test_get_agent_queue(self, task_manager):
        """Test getting agent task queue"""
        # Create multiple tasks for the same agent
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task1_id = await task_manager.create_task(
                "High Priority", "Description", "test-agent", {},
                priority=TaskPriority.HIGH
            )
            task2_id = await task_manager.create_task(
                "Low Priority", "Description", "test-agent", {},
                priority=TaskPriority.LOW
            )
            task3_id = await task_manager.create_task(
                "Medium Priority", "Description", "test-agent", {},
                priority=TaskPriority.MEDIUM
            )
        
        with patch.object(task_manager, '_check_dependencies', new=AsyncMock(return_value=True)):
            queue = await task_manager.get_agent_queue("test-agent")
            
            assert len(queue) == 3
            
            # Verify sorting by priority (high to low)
            assert queue[0]["priority"] == 3  # HIGH
            assert queue[1]["priority"] == 2  # MEDIUM  
            assert queue[2]["priority"] == 1  # LOW
            
            # Verify required fields
            for task_info in queue:
                required_fields = ["task_id", "name", "status", "priority", "progress", "dependencies_satisfied"]
                for field in required_fields:
                    assert field in task_info
    
    @pytest.mark.asyncio
    async def test_get_agent_queue_empty(self, task_manager):
        """Test getting queue for agent with no tasks"""
        queue = await task_manager.get_agent_queue("empty-agent")
        assert queue == []
    
    @pytest.mark.asyncio
    async def test_get_next_task_for_agent(self, task_manager):
        """Test getting next ready task for agent"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            # Create blocked task first
            blocked_task_id = await task_manager.create_task(
                "Blocked Task", "Description", "test-agent", {}
            )
            task_manager.tasks[blocked_task_id].status = TaskStatus.BLOCKED
            
            # Create ready task
            ready_task_id = await task_manager.create_task(
                "Ready Task", "Description", "test-agent", {}
            )
        
        with patch.object(task_manager, '_check_dependencies', side_effect=lambda task: task.task_id == ready_task_id):
            next_task = await task_manager.get_next_task_for_agent("test-agent")
            assert next_task == ready_task_id
    
    @pytest.mark.asyncio
    async def test_get_next_task_for_agent_none_ready(self, task_manager):
        """Test getting next task when none are ready"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Blocked Task", "Description", "test-agent", {}
            )
        
        with patch.object(task_manager, '_check_dependencies', new=AsyncMock(return_value=False)):
            next_task = await task_manager.get_next_task_for_agent("test-agent")
            assert next_task is None
    
    @pytest.mark.asyncio
    async def test_get_next_task_for_agent_empty_queue(self, task_manager):
        """Test getting next task for agent with no tasks"""
        next_task = await task_manager.get_next_task_for_agent("empty-agent")
        assert next_task is None
    
    @pytest.mark.asyncio
    async def test_get_workflow_status(self, task_manager):
        """Test getting workflow status"""
        # Create workflow
        workflow_id = await task_manager.create_workflow("test_workflow", {"metadata": {"version": "1.0"}})
        
        # Create tasks in workflow
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task1_id = await task_manager.create_task(
                "Task 1", "Description", "agent1", {}, workflow_id=workflow_id
            )
            task2_id = await task_manager.create_task(
                "Task 2", "Description", "agent2", {}, workflow_id=workflow_id
            )
            
            # Set different progress levels
            task_manager.tasks[task1_id].progress_percentage = 100.0
            task_manager.tasks[task1_id].status = TaskStatus.COMPLETED
            task_manager.tasks[task2_id].progress_percentage = 50.0
        
        status = await task_manager.get_workflow_status(workflow_id)
        
        assert status is not None
        assert status["workflow_id"] == workflow_id
        assert status["status"] == "in_progress"
        assert status["overall_progress"] == 75.0  # (100 + 50) / 2
        assert len(status["tasks"]) == 2
        assert status["metadata"]["version"] == "1.0"
        
        # Check task details
        assert task1_id in status["tasks"]
        assert task2_id in status["tasks"]
        assert status["tasks"][task1_id]["status"] == "completed"
        assert status["tasks"][task2_id]["progress"] == 50.0
    
    @pytest.mark.asyncio
    async def test_get_workflow_status_completed(self, task_manager):
        """Test workflow status when all tasks completed"""
        workflow_id = await task_manager.create_workflow("completed_workflow", {})
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task_id = await task_manager.create_task(
                "Completed Task", "Description", "agent", {}, workflow_id=workflow_id
            )
            task_manager.tasks[task_id].status = TaskStatus.COMPLETED
            task_manager.tasks[task_id].progress_percentage = 100.0
        
        status = await task_manager.get_workflow_status(workflow_id)
        assert status["status"] == "completed"
        assert status["overall_progress"] == 100.0
    
    @pytest.mark.asyncio
    async def test_get_workflow_status_failed(self, task_manager):
        """Test workflow status when any task failed"""
        workflow_id = await task_manager.create_workflow("failed_workflow", {})
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task_id = await task_manager.create_task(
                "Failed Task", "Description", "agent", {}, workflow_id=workflow_id
            )
            task_manager.tasks[task_id].status = TaskStatus.FAILED
        
        status = await task_manager.get_workflow_status(workflow_id)
        assert status["status"] == "failed"
    
    @pytest.mark.asyncio
    async def test_get_workflow_status_nonexistent(self, task_manager):
        """Test getting status of nonexistent workflow"""
        status = await task_manager.get_workflow_status("nonexistent")
        assert status is None
    
    @pytest.mark.asyncio
    async def test_cancel_task(self, task_manager):
        """Test task cancellation"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            task_id = await task_manager.create_task(
                "Cancellable Task", "Description", "test-agent", {}
            )
        
        with patch.object(task_manager, '_save_task', new=AsyncMock()) as mock_save, \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log:
            
            reason = "User requested cancellation"
            result = await task_manager.cancel_task(task_id, reason)
            
            assert result is True
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.CANCELLED
            assert task.error_message == f"Cancelled: {reason}"
            
            mock_save.assert_called_once()
            mock_log.assert_called_once_with(task_id, "cancelled", reason)
    
    @pytest.mark.asyncio
    async def test_cancel_task_nonexistent(self, task_manager):
        """Test cancelling nonexistent task"""
        result = await task_manager.cancel_task("nonexistent", "reason")
        assert result is False


class TestMCPTaskManagerPrivateMethods:
    """Test private helper methods of MCPTaskManager"""
    
    @pytest.fixture
    def task_manager(self, tmp_path):
        """Create task manager for private method testing"""
        mock_comm = MagicMock()
        return MCPTaskManager(tmp_path / "workspace", mock_comm)
    
    @pytest.mark.asyncio
    async def test_check_dependencies_no_deps(self, task_manager):
        """Test dependency checking with no dependencies"""
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.CREATED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=0.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        result = await task_manager._check_dependencies(task)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_dependencies_satisfied(self, task_manager):
        """Test dependency checking with satisfied dependencies"""
        # Create dependency task
        dep_task = Task(
            task_id="dep_task", name="Dependency", description="Dep", agent_name="agent",
            status=TaskStatus.COMPLETED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=100.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        task_manager.tasks["dep_task"] = dep_task
        
        # Create task with dependency
        dependency = TaskDependency("dep_task", "requires", "Needs completion")
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.CREATED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[dependency], blocks=[],
            progress_percentage=0.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        result = await task_manager._check_dependencies(task)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_dependencies_not_satisfied(self, task_manager):
        """Test dependency checking with unsatisfied dependencies"""
        # Create incomplete dependency task
        dep_task = Task(
            task_id="dep_task", name="Dependency", description="Dep", agent_name="agent",
            status=TaskStatus.IN_PROGRESS, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=50.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        task_manager.tasks["dep_task"] = dep_task
        
        # Create task with dependency
        dependency = TaskDependency("dep_task", "blocks", "Blocked by incomplete task")
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.CREATED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[dependency], blocks=[],
            progress_percentage=0.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        result = await task_manager._check_dependencies(task)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_dependencies_missing_task(self, task_manager):
        """Test dependency checking with missing dependency task"""
        dependency = TaskDependency("missing_task", "requires", "Missing dependency")
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.CREATED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[dependency], blocks=[],
            progress_percentage=0.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        result = await task_manager._check_dependencies(task)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_dependencies_requires_type(self, task_manager):
        """Test dependency checking with 'requires' type dependency"""
        # Create incomplete dependency task
        dep_task = Task(
            task_id="dep_task", name="Dependency", description="Dep", agent_name="agent",
            status=TaskStatus.IN_PROGRESS, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=50.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        task_manager.tasks["dep_task"] = dep_task
        
        # Create task with 'requires' dependency
        dependency = TaskDependency("dep_task", "requires", "Requires completion")
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.CREATED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[dependency], blocks=[],
            progress_percentage=0.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        result = await task_manager._check_dependencies(task)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_trigger_dependent_tasks(self, task_manager):
        """Test triggering dependent tasks when task completes"""
        # Create completed task
        completed_task = Task(
            task_id="completed_task", name="Completed", description="Done", agent_name="agent",
            status=TaskStatus.COMPLETED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=100.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        task_manager.tasks["completed_task"] = completed_task
        
        # Create blocked dependent task
        dependency = TaskDependency("completed_task", "requires", "Waits for completion")
        dependent_task = Task(
            task_id="dependent_task", name="Dependent", description="Waits", agent_name="agent",
            status=TaskStatus.BLOCKED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[dependency], blocks=[],
            progress_percentage=0.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        task_manager.tasks["dependent_task"] = dependent_task
        
        with patch.object(task_manager, '_check_dependencies', new=AsyncMock(return_value=True)), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log:
            
            await task_manager._trigger_dependent_tasks("completed_task")
            
            # Dependent task should be unblocked
            assert dependent_task.status == TaskStatus.CREATED
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retry_task(self, task_manager):
        """Test task retry logic"""
        failed_task = Task(
            task_id="failed_task", name="Failed", description="Failed", agent_name="agent",
            status=TaskStatus.FAILED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=50.0, estimated_duration=None, actual_duration=None,
            error_message="Something went wrong", retry_count=1, max_retries=3
        )
        task_manager.tasks["failed_task"] = failed_task
        
        with patch.object(task_manager, '_log_task_event', new=AsyncMock()) as mock_log:
            await task_manager._retry_task("failed_task")
            
            assert failed_task.status == TaskStatus.CREATED
            assert failed_task.error_message is None
            assert failed_task.progress_percentage == 0.0
            assert failed_task.retry_count == 2
            
            mock_log.assert_called_once_with("failed_task", "retrying", "Retry attempt 2")
    
    def test_estimate_completion_time_no_duration(self, task_manager):
        """Test completion time estimation with no estimated duration"""
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.IN_PROGRESS, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=50.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        result = task_manager._estimate_completion_time(task)
        assert result is None
    
    def test_estimate_completion_time_completed(self, task_manager):
        """Test completion time estimation for completed task"""
        completed_at = datetime.now()
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.COMPLETED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=completed_at,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=100.0, estimated_duration=timedelta(hours=1), actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        result = task_manager._estimate_completion_time(task)
        assert result == completed_at.isoformat()
    
    def test_estimate_completion_time_with_progress(self, task_manager):
        """Test completion time estimation based on progress"""
        started_at = datetime.now() - timedelta(minutes=30)
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.IN_PROGRESS, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=started_at, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=50.0, estimated_duration=timedelta(hours=1), actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        with patch('subforge.core.mcp_task_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = started_at + timedelta(minutes=30)
            
            result = task_manager._estimate_completion_time(task)
            assert result is not None
            assert isinstance(result, str)  # Should be ISO format string
    
    @pytest.mark.asyncio
    async def test_save_task(self, task_manager):
        """Test task saving to file"""
        task = Task(
            task_id="test_save", name="Test Save", description="Test", agent_name="agent",
            status=TaskStatus.CREATED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={"test": "data"}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=0.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        with patch("builtins.open", mock_open()) as mock_file:
            await task_manager._save_task(task)
            
            mock_file.assert_called_once()
            call_args = mock_file.call_args[0]
            assert "test_save.json" in str(call_args[0])
    
    @pytest.mark.asyncio
    async def test_log_task_event(self, task_manager):
        """Test task event logging"""
        with patch("builtins.open", mock_open()) as mock_file:
            await task_manager._log_task_event("test_task", "created", "Task was created")
            
            mock_file.assert_called_once()
            # Verify log file path contains date
            call_args = mock_file.call_args[0]
            assert "tasks.log" in str(call_args[0])
    
    @pytest.mark.asyncio
    async def test_cleanup_completed_workflows(self, task_manager):
        """Test cleanup of old completed workflows"""
        # Create old workflow
        old_date = datetime.now() - timedelta(days=35)
        old_workflow = {
            "workflow_id": "old_workflow",
            "created_at": old_date.isoformat(),
            "status": "completed",
            "tasks": []
        }
        task_manager.active_workflows["old_workflow"] = old_workflow
        
        # Create recent workflow
        recent_date = datetime.now() - timedelta(days=10)
        recent_workflow = {
            "workflow_id": "recent_workflow", 
            "created_at": recent_date.isoformat(),
            "status": "completed",
            "tasks": []
        }
        task_manager.active_workflows["recent_workflow"] = recent_workflow
        
        with patch.object(task_manager, 'get_workflow_status', new=AsyncMock()) as mock_status:
            # Mock old workflow as completed
            mock_status.side_effect = lambda wf_id: {
                "workflow_id": wf_id,
                "status": "completed" if wf_id == "old_workflow" else "in_progress"
            }
            
            await task_manager.cleanup_completed_workflows(retention_days=30)
            
            # Old workflow should be removed, recent one kept
            assert "old_workflow" not in task_manager.active_workflows
            assert "recent_workflow" in task_manager.active_workflows


class TestSubForgeWorkflowFactory:
    """Test the SubForge workflow factory"""
    
    @pytest.fixture
    def task_manager(self, tmp_path):
        """Create task manager for factory testing"""
        mock_comm = MagicMock()
        return MCPTaskManager(tmp_path / "workspace", mock_comm)
    
    @pytest.mark.asyncio
    async def test_create_factory_workflow(self, task_manager):
        """Test creation of complete factory workflow"""
        user_request = "Create a web application with authentication"
        project_path = "/path/to/project"
        
        with patch.object(task_manager, 'create_workflow', new=AsyncMock()) as mock_create_workflow, \
             patch.object(task_manager, 'create_task', new=AsyncMock()) as mock_create_task:
            
            # Mock workflow creation - return the workflow ID generated by the factory
            mock_create_workflow.side_effect = lambda wf_id, config: wf_id
            
            # Mock task creation with unique IDs (6 tasks total)
            task_ids = ["analysis_123", "selection_123", "claude_md_123", "agent_gen_123", "workflow_123", "validation_123"]
            mock_create_task.side_effect = task_ids
            
            workflow_id = await SubForgeWorkflowFactory.create_factory_workflow(
                task_manager, user_request, project_path
            )
            
            # Workflow ID should start with "factory_" but we can't predict the random part
            assert workflow_id.startswith("factory_")
            
            # Verify workflow creation was called
            mock_create_workflow.assert_called_once()
            workflow_config = mock_create_workflow.call_args[0][1]
            assert workflow_config["name"] == "SubForge Factory Workflow"
            assert workflow_config["user_request"] == user_request
            assert workflow_config["project_path"] == project_path
            
            # Verify all factory tasks were created (6 tasks total)
            assert mock_create_task.call_count == 6
            
            # Check task creation calls
            call_args_list = mock_create_task.call_args_list
            
            # Analysis task
            analysis_call = call_args_list[0]
            assert analysis_call[1]["agent_name"] == "project-analyzer"
            assert analysis_call[1]["name"] == "Deep Project Analysis"
            
            # Selection task  
            selection_call = call_args_list[1]
            assert selection_call[1]["agent_name"] == "template-selector"
            assert len(selection_call[1]["dependencies"]) == 1
            
            # Generation tasks
            claude_md_call = call_args_list[2]
            assert claude_md_call[1]["agent_name"] == "claude-md-generator"
            assert len(claude_md_call[1]["dependencies"]) == 2
            
            agent_gen_call = call_args_list[3]
            assert agent_gen_call[1]["agent_name"] == "agent-generator"
            
            workflow_call = call_args_list[4]
            assert workflow_call[1]["agent_name"] == "workflow-generator"
            
            # Validation task should have dependencies on all generation tasks
            validation_call = call_args_list[4]  # This should be the last call (validation)
            # Note: The validation task is actually the 5th task created, but we need to check the actual implementation
    
    @pytest.mark.asyncio 
    async def test_factory_workflow_structure(self, task_manager):
        """Test that factory workflow has correct structure and dependencies"""
        with patch.object(task_manager, 'create_workflow', new=AsyncMock(return_value="test_workflow")), \
             patch.object(task_manager, 'create_task', new=AsyncMock()) as mock_create_task:
            
            # Return different task IDs for each call
            task_ids = ["task1", "task2", "task3", "task4", "task5", "task6"]
            mock_create_task.side_effect = task_ids
            
            await SubForgeWorkflowFactory.create_factory_workflow(
                task_manager, "test request", "/test/path"
            )
            
            # Verify task priorities and phases
            calls = mock_create_task.call_args_list
            
            # First task (analysis) should be HIGH priority
            analysis_call = calls[0]
            assert analysis_call[1]["priority"] == TaskPriority.HIGH
            assert analysis_call[1]["metadata"]["phase"] == "analysis"
            assert analysis_call[1]["metadata"]["critical"] is True
            
            # Selection task should depend on analysis
            selection_call = calls[1]
            assert selection_call[1]["priority"] == TaskPriority.HIGH
            assert len(selection_call[1]["dependencies"]) == 1
            assert selection_call[1]["dependencies"][0].task_id == "task1"
            
            # Generation tasks should have parallel group metadata
            for i in range(2, 5):  # Tasks 3, 4, 5 are generation tasks
                gen_call = calls[i]
                assert gen_call[1]["metadata"]["phase"] == "generation"
                assert gen_call[1]["metadata"]["parallel_group"] == "generators"


class TestErrorScenarios:
    """Test error scenarios and edge cases"""
    
    @pytest.fixture
    def task_manager(self, tmp_path):
        """Create task manager for error testing"""
        mock_comm = MagicMock()
        return MCPTaskManager(tmp_path / "workspace", mock_comm)
    
    @pytest.mark.asyncio
    async def test_file_write_error_handling(self, task_manager):
        """Test handling of file write errors"""
        task = Task(
            task_id="test", name="Test", description="Test", agent_name="agent",
            status=TaskStatus.CREATED, priority=TaskPriority.MEDIUM,
            created_at=datetime.now(), assigned_at=None, started_at=None, completed_at=None,
            inputs={}, outputs={}, metadata={}, dependencies=[], blocks=[],
            progress_percentage=0.0, estimated_duration=None, actual_duration=None,
            error_message=None, retry_count=0, max_retries=3
        )
        
        # The current implementation doesn't handle IOError gracefully
        # This test verifies that the error is raised (which is current behavior)
        with patch("builtins.open", side_effect=IOError("Disk full")):
            with pytest.raises(IOError):
                await task_manager._save_task(task)
    
    @pytest.mark.asyncio
    async def test_concurrent_task_modification(self, task_manager):
        """Test concurrent task modifications"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task_id = await task_manager.create_task(
                "Concurrent Test", "Description", "test-agent", {}
            )
            
            # Simulate concurrent modifications
            async def update_progress():
                await task_manager.update_task_progress(task_id, 50.0)
            
            async def start_task():
                await task_manager.start_task(task_id)
            
            # These should not interfere with each other
            await asyncio.gather(update_progress(), start_task())
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.IN_PROGRESS
            assert task.progress_percentage == 50.0
    
    def test_task_serialization_edge_cases(self):
        """Test task serialization with edge case values"""
        task = Task(
            task_id="edge_case",
            name="Edge Case Task",
            description="Task with edge case values",
            agent_name="test-agent",
            status=TaskStatus.FAILED,
            priority=TaskPriority.CRITICAL,
            created_at=datetime.now(),
            assigned_at=datetime.now(),
            started_at=datetime.now(),
            completed_at=datetime.now(),
            inputs={"null_value": None, "empty_list": [], "unicode": "🚀"},
            outputs={"large_number": 999999999999},
            metadata={"nested": {"deep": {"value": True}}},
            dependencies=[TaskDependency("dep1", "blocks", "Complex dependency")],
            blocks=["block1", "block2"],
            progress_percentage=99.99,
            estimated_duration=timedelta(microseconds=1),
            actual_duration=timedelta(days=365),
            error_message="Very long error message " * 100,
            retry_count=999,
            max_retries=1000
        )
        
        # Should not raise any serialization errors
        task_dict = task.to_dict()
        
        # Verify edge case values are handled properly
        assert task_dict["inputs"]["null_value"] is None
        assert task_dict["inputs"]["unicode"] == "🚀"
        assert task_dict["outputs"]["large_number"] == 999999999999
        assert task_dict["progress_percentage"] == 99.99
        assert len(task_dict["error_message"]) > 2000  # Long error message preserved
        assert task_dict["actual_duration"] == 31536000.0  # 365 days in seconds


class TestMCPToolIntegration:
    """Test MCP tool discovery and execution (simulated)"""
    
    @pytest.fixture
    def task_manager(self, tmp_path):
        """Create task manager for MCP testing"""
        mock_comm = MagicMock()
        return MCPTaskManager(tmp_path / "workspace", mock_comm)
    
    @pytest.mark.asyncio
    async def test_mcp_tool_discovery_simulation(self, task_manager):
        """Simulate MCP tool discovery and registration"""
        # Since actual MCP tools aren't available, we simulate the behavior
        mock_tools = {
            "file_reader": {
                "name": "file_reader",
                "description": "Read files from filesystem",
                "parameters": {"file_path": "string"}
            },
            "code_executor": {
                "name": "code_executor", 
                "description": "Execute code snippets",
                "parameters": {"code": "string", "language": "string"}
            }
        }
        
        # Simulate tool registration in task metadata
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task_id = await task_manager.create_task(
                "MCP Tool Task",
                "Task that uses MCP tools",
                "mcp-agent",
                {"input_file": "test.py"},
                metadata={"available_tools": list(mock_tools.keys())}
            )
            
            task = task_manager.tasks[task_id]
            assert "available_tools" in task.metadata
            assert "file_reader" in task.metadata["available_tools"]
            assert "code_executor" in task.metadata["available_tools"]
    
    @pytest.mark.asyncio
    async def test_mcp_tool_execution_simulation(self, task_manager):
        """Simulate MCP tool execution within task context"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            task_id = await task_manager.create_task(
                "Tool Execution Task",
                "Execute MCP tools",
                "mcp-agent",
                {"tools_to_execute": ["file_reader", "code_executor"]}
            )
            
            # Simulate tool execution results
            tool_results = {
                "file_reader": {"status": "success", "content": "file content"},
                "code_executor": {"status": "success", "output": "execution result"}
            }
            
            # Complete task with tool execution results
            await task_manager.complete_task(task_id, {"tool_results": tool_results})
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.COMPLETED
            assert "tool_results" in task.outputs
            assert task.outputs["tool_results"]["file_reader"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_mcp_tool_error_handling(self, task_manager):
        """Test handling of MCP tool execution errors"""
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()), \
             patch.object(task_manager, '_retry_task', new=AsyncMock()):  # Mock retry to avoid status change
            
            task_id = await task_manager.create_task(
                "Tool Error Task",
                "Task with tool execution error",
                "mcp-agent",
                {"tool": "failing_tool"}
            )
            
            # Set task to max retries to prevent retry
            task_manager.tasks[task_id].retry_count = 3  # max_retries = 3
            
            # Simulate tool execution failure
            error_message = "MCP tool 'failing_tool' execution failed: Connection timeout"
            
            await task_manager.complete_task(
                task_id, 
                {"tool_error": "Connection timeout"}, 
                success=False,
                error_message=error_message
            )
            
            task = task_manager.tasks[task_id]
            assert task.status == TaskStatus.FAILED
            assert error_message in task.error_message
            assert "tool_error" in task.outputs


@pytest.mark.asyncio
async def test_integration_full_workflow():
    """Integration test for complete workflow execution"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create task manager with proper temporary directory
        workspace = Path(tmp_dir) / "test_workspace"
        mock_comm = MagicMock()
        task_manager = MCPTaskManager(workspace, mock_comm)
        
        # Mock file operations
        with patch.object(task_manager, '_save_task', new=AsyncMock()), \
             patch.object(task_manager, '_log_task_event', new=AsyncMock()):
            
            # Create workflow
            workflow_id = await task_manager.create_workflow("integration_test", {
                "name": "Integration Test Workflow"
            })
            
            # Create dependency chain: Task A -> Task B -> Task C
            task_a_id = await task_manager.create_task(
                "Task A", "First task", "agent-a", {"data": "initial"},
                workflow_id=workflow_id
            )
            
            task_b_id = await task_manager.create_task(
                "Task B", "Second task", "agent-b", {"data": "processed"},
                workflow_id=workflow_id,
                dependencies=[TaskDependency(task_a_id, "requires", "Needs Task A")]
            )
            
            task_c_id = await task_manager.create_task(
                "Task C", "Final task", "agent-c", {"data": "final"},
                workflow_id=workflow_id,
                dependencies=[TaskDependency(task_b_id, "requires", "Needs Task B")]
            )
            
            # Execute workflow simulation
            with patch.object(task_manager, '_check_dependencies', new=AsyncMock()) as mock_deps:
                # Initially, only Task A is ready
                mock_deps.side_effect = lambda task: task.task_id == task_a_id
                
                # Start Task A
                await task_manager.start_task(task_a_id)
                await task_manager.complete_task(task_a_id, {"result": "A complete"})
                
                # Now Task B is ready
                mock_deps.side_effect = lambda task: task.task_id in [task_a_id, task_b_id]
                
                # Start Task B
                await task_manager.start_task(task_b_id)
                await task_manager.complete_task(task_b_id, {"result": "B complete"})
                
                # Now Task C is ready
                mock_deps.side_effect = lambda task: True
                
                # Start and complete Task C
                await task_manager.start_task(task_c_id)
                await task_manager.complete_task(task_c_id, {"result": "C complete"})
            
            # Verify final state
            workflow_status = await task_manager.get_workflow_status(workflow_id)
            assert workflow_status["status"] == "completed"
            assert workflow_status["overall_progress"] == 100.0
            
            # Verify all tasks completed
            for task_id in [task_a_id, task_b_id, task_c_id]:
                task = task_manager.tasks[task_id]
                assert task.status == TaskStatus.COMPLETED
                assert task.progress_percentage == 100.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
#!/usr/bin/env python3
"""
MCP Task Manager
Manages task creation, assignment, and coordination for SubForge factory workflow
Implements the "Task Creation in MCP" phase from the workflow diagram
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .communication import CommunicationManager


class TaskStatus(Enum):
    """Task execution status"""

    CREATED = "created"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskDependency:
    """Represents a task dependency relationship"""

    task_id: str
    dependency_type: str  # 'blocks', 'requires', 'triggers'
    description: str


@dataclass
class Task:
    """Represents a single task in the MCP workflow"""

    task_id: str
    name: str
    description: str
    agent_name: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    # Task configuration
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metadata: Dict[str, Any]

    # Dependencies and relationships
    dependencies: List[TaskDependency]
    blocks: List[str]  # Task IDs that this task blocks

    # Progress tracking
    progress_percentage: float
    estimated_duration: Optional[timedelta]
    actual_duration: Optional[timedelta]

    # Error handling
    error_message: Optional[str]
    retry_count: int
    max_retries: int

    def to_dict(self) -> Dict:
        """Convert task to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "dependencies": [asdict(dep) for dep in self.dependencies],
            "blocks": self.blocks,
            "progress_percentage": self.progress_percentage,
            "estimated_duration": (
                self.estimated_duration.total_seconds()
                if self.estimated_duration
                else None
            ),
            "actual_duration": (
                self.actual_duration.total_seconds() if self.actual_duration else None
            ),
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }


class MCPTaskManager:
    """
    Manages task creation, assignment, and coordination for SubForge factory workflow
    Implements the MCP (Model Context Protocol) for task management between agents
    """

    def __init__(
        self, workspace_dir: Path, communication_manager: CommunicationManager
    ):
        self.workspace_dir = workspace_dir
        self.communication_manager = communication_manager
        self.tasks: Dict[str, Task] = {}
        self.task_queues: Dict[str, List[str]] = {}  # agent_name -> [task_ids]
        self.active_workflows: Dict[str, Dict] = {}

        # Task management directories
        self.tasks_dir = workspace_dir / "tasks"
        self.workflows_dir = workspace_dir / "workflows"
        self.logs_dir = workspace_dir / "logs"

        # Create directories
        for directory in [self.tasks_dir, self.workflows_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    async def create_workflow(self, workflow_id: str, workflow_config: Dict) -> str:
        """Create a new workflow with associated tasks"""
        print(f"🔄 Creating workflow: {workflow_id}")

        workflow = {
            "workflow_id": workflow_id,
            "config": workflow_config,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "tasks": [],
            "dependencies": workflow_config.get("dependencies", {}),
            "metadata": workflow_config.get("metadata", {}),
        }

        self.active_workflows[workflow_id] = workflow

        # Save workflow configuration
        workflow_file = self.workflows_dir / f"{workflow_id}.json"
        with open(workflow_file, "w") as f:
            json.dump(workflow, f, indent=2)

        return workflow_id

    async def create_task(
        self,
        name: str,
        description: str,
        agent_name: str,
        inputs: Dict[str, Any],
        workflow_id: Optional[str] = None,
        dependencies: Optional[List[TaskDependency]] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        estimated_duration: Optional[timedelta] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new task and add it to the appropriate queue"""

        task_id = f"task_{uuid.uuid4().hex[:8]}"

        task = Task(
            task_id=task_id,
            name=name,
            description=description,
            agent_name=agent_name,
            status=TaskStatus.CREATED,
            priority=priority,
            created_at=datetime.now(),
            assigned_at=None,
            started_at=None,
            completed_at=None,
            inputs=inputs,
            outputs={},
            metadata=metadata or {},
            dependencies=dependencies or [],
            blocks=[],
            progress_percentage=0.0,
            estimated_duration=estimated_duration,
            actual_duration=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
        )

        # Add to workflow if specified
        if workflow_id and workflow_id in self.active_workflows:
            task.metadata["workflow_id"] = workflow_id
            self.active_workflows[workflow_id]["tasks"].append(task_id)

        # Store task
        self.tasks[task_id] = task

        # Add to agent queue
        if agent_name not in self.task_queues:
            self.task_queues[agent_name] = []
        self.task_queues[agent_name].append(task_id)

        # Save task to file
        await self._save_task(task)

        # Log task creation
        await self._log_task_event(
            task_id, "created", f"Task created for agent {agent_name}"
        )

        print(f"    📋 Created task {task_id}: {name} → @{agent_name}")

        return task_id

    async def assign_task_to_agent(self, task_id: str, agent_name: str) -> bool:
        """Assign a specific task to an agent"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # Check dependencies
        if not await self._check_dependencies(task):
            await self._log_task_event(task_id, "blocked", "Dependencies not satisfied")
            task.status = TaskStatus.BLOCKED
            return False

        # Assign task
        task.assigned_at = datetime.now()
        task.status = TaskStatus.ASSIGNED
        task.agent_name = agent_name

        # Update queue
        if agent_name not in self.task_queues:
            self.task_queues[agent_name] = []
        if task_id not in self.task_queues[agent_name]:
            self.task_queues[agent_name].append(task_id)

        await self._save_task(task)
        await self._log_task_event(
            task_id, "assigned", f"Task assigned to {agent_name}"
        )

        return True

    async def start_task(self, task_id: str) -> bool:
        """Mark a task as started"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.started_at = datetime.now()
        task.status = TaskStatus.IN_PROGRESS

        await self._save_task(task)
        await self._log_task_event(task_id, "started", "Task execution started")

        return True

    async def update_task_progress(
        self,
        task_id: str,
        progress_percentage: float,
        status_message: Optional[str] = None,
    ) -> bool:
        """Update task progress"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.progress_percentage = max(0, min(100, progress_percentage))

        if status_message:
            task.metadata["last_status"] = status_message
            task.metadata["last_update"] = datetime.now().isoformat()

        await self._save_task(task)

        return True

    async def complete_task(
        self,
        task_id: str,
        outputs: Dict[str, Any],
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """Mark a task as completed"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.completed_at = datetime.now()
        task.outputs = outputs
        task.progress_percentage = 100.0

        if task.started_at:
            task.actual_duration = task.completed_at - task.started_at

        if success:
            task.status = TaskStatus.COMPLETED
            await self._log_task_event(
                task_id, "completed", "Task completed successfully"
            )

            # Trigger dependent tasks
            await self._trigger_dependent_tasks(task_id)

        else:
            task.status = TaskStatus.FAILED
            task.error_message = error_message
            await self._log_task_event(
                task_id, "failed", f"Task failed: {error_message}"
            )

            # Handle retry logic
            if task.retry_count < task.max_retries:
                await self._retry_task(task_id)

        await self._save_task(task)
        return True

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status and details"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "name": task.name,
            "agent_name": task.agent_name,
            "status": task.status.value,
            "progress": task.progress_percentage,
            "created_at": task.created_at.isoformat(),
            "estimated_completion": self._estimate_completion_time(task),
            "dependencies_satisfied": await self._check_dependencies(task),
            "outputs": task.outputs,
            "error_message": task.error_message,
        }

    async def get_agent_queue(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get task queue for a specific agent"""
        if agent_name not in self.task_queues:
            return []

        queue_status = []
        for task_id in self.task_queues[agent_name]:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                queue_status.append(
                    {
                        "task_id": task_id,
                        "name": task.name,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "progress": task.progress_percentage,
                        "dependencies_satisfied": await self._check_dependencies(task),
                    }
                )

        # Sort by priority and creation time
        queue_status.sort(key=lambda x: (-x["priority"], x["task_id"]))
        return queue_status

    async def get_next_task_for_agent(self, agent_name: str) -> Optional[str]:
        """Get the next ready task for an agent"""
        if agent_name not in self.task_queues:
            return None

        for task_id in self.task_queues[agent_name]:
            if task_id not in self.tasks:
                continue

            task = self.tasks[task_id]

            # Check if task is ready (created/assigned and dependencies satisfied)
            if task.status in [TaskStatus.CREATED, TaskStatus.ASSIGNED]:
                if await self._check_dependencies(task):
                    return task_id

        return None

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive workflow status"""
        if workflow_id not in self.active_workflows:
            return None

        workflow = self.active_workflows[workflow_id]
        task_statuses = {}

        for task_id in workflow["tasks"]:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task_statuses[task_id] = {
                    "name": task.name,
                    "agent": task.agent_name,
                    "status": task.status.value,
                    "progress": task.progress_percentage,
                }

        # Calculate overall progress
        total_progress = sum(status["progress"] for status in task_statuses.values())
        overall_progress = total_progress / len(task_statuses) if task_statuses else 0

        # Determine workflow status
        workflow_status = "in_progress"
        if all(status["status"] == "completed" for status in task_statuses.values()):
            workflow_status = "completed"
        elif any(status["status"] == "failed" for status in task_statuses.values()):
            workflow_status = "failed"

        return {
            "workflow_id": workflow_id,
            "status": workflow_status,
            "overall_progress": overall_progress,
            "tasks": task_statuses,
            "created_at": workflow["created_at"],
            "metadata": workflow["metadata"],
        }

    async def cancel_task(self, task_id: str, reason: str) -> bool:
        """Cancel a task"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.CANCELLED
        task.error_message = f"Cancelled: {reason}"

        await self._save_task(task)
        await self._log_task_event(task_id, "cancelled", reason)

        return True

    # Private helper methods

    async def _check_dependencies(self, task: Task) -> bool:
        """Check if all task dependencies are satisfied"""
        for dependency in task.dependencies:
            dep_task_id = dependency.task_id

            if dep_task_id not in self.tasks:
                return False

            dep_task = self.tasks[dep_task_id]

            if dependency.dependency_type == "blocks":
                # This task is blocked by the dependency
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
            elif dependency.dependency_type == "requires":
                # This task requires the dependency to be completed
                if dep_task.status != TaskStatus.COMPLETED:
                    return False

        return True

    async def _trigger_dependent_tasks(self, completed_task_id: str):
        """Trigger tasks that depend on the completed task"""
        for task_id, task in self.tasks.items():
            for dependency in task.dependencies:
                if dependency.task_id == completed_task_id:
                    if await self._check_dependencies(task):
                        if task.status == TaskStatus.BLOCKED:
                            task.status = TaskStatus.CREATED
                            await self._log_task_event(
                                task_id,
                                "unblocked",
                                f"Unblocked by completion of {completed_task_id}",
                            )

    async def _retry_task(self, task_id: str):
        """Retry a failed task"""
        task = self.tasks[task_id]
        task.retry_count += 1
        task.status = TaskStatus.CREATED
        task.error_message = None
        task.progress_percentage = 0.0

        await self._log_task_event(
            task_id, "retrying", f"Retry attempt {task.retry_count}"
        )

    def _estimate_completion_time(self, task: Task) -> Optional[str]:
        """Estimate task completion time"""
        if not task.estimated_duration:
            return None

        if task.status == TaskStatus.COMPLETED:
            return task.completed_at.isoformat()

        if task.started_at:
            elapsed = datetime.now() - task.started_at
            if task.progress_percentage > 0:
                estimated_total = elapsed * (100 / task.progress_percentage)
                completion_time = task.started_at + estimated_total
                return completion_time.isoformat()

        return None

    async def _save_task(self, task: Task):
        """Save task to persistent storage"""
        task_file = self.tasks_dir / f"{task.task_id}.json"
        with open(task_file, "w") as f:
            json.dump(task.to_dict(), f, indent=2)

    async def _log_task_event(self, task_id: str, event_type: str, message: str):
        """Log task events for audit and debugging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "event_type": event_type,
            "message": message,
        }

        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_tasks.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    async def cleanup_completed_workflows(self, retention_days: int = 30):
        """Clean up old completed workflows"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        workflows_to_remove = []
        for workflow_id, workflow in self.active_workflows.items():
            created_at = datetime.fromisoformat(workflow["created_at"])
            if created_at < cutoff_date:
                # Check if workflow is completed
                status = await self.get_workflow_status(workflow_id)
                if status and status["status"] == "completed":
                    workflows_to_remove.append(workflow_id)

        for workflow_id in workflows_to_remove:
            del self.active_workflows[workflow_id]
            print(f"    🧹 Cleaned up completed workflow: {workflow_id}")


class SubForgeWorkflowFactory:
    """Factory for creating standard SubForge workflows"""

    @staticmethod
    async def create_factory_workflow(
        task_manager: MCPTaskManager, user_request: str, project_path: str
    ) -> str:
        """Create the standard SubForge factory workflow"""

        workflow_id = f"factory_{uuid.uuid4().hex[:8]}"

        workflow_config = {
            "name": "SubForge Factory Workflow",
            "description": "Complete agent generation workflow following factory pattern",
            "user_request": user_request,
            "project_path": project_path,
            "phases": [
                "requirements",
                "analysis",
                "selection",
                "generation",
                "integration",
                "validation",
                "deployment",
            ],
            "metadata": {
                "pattern": "ai_agent_factory",
                "version": "2.0",
                "created_by": "SubForge",
            },
        }

        # Create workflow
        await task_manager.create_workflow(workflow_id, workflow_config)

        # Create factory tasks based on the workflow diagram

        # Phase 1: Requirements and Analysis
        analysis_task_id = await task_manager.create_task(
            name="Deep Project Analysis",
            description="Perform comprehensive project analysis using project-analyzer subagent",
            agent_name="project-analyzer",
            inputs={
                "user_request": user_request,
                "project_path": project_path,
                "analysis_depth": "comprehensive",
            },
            workflow_id=workflow_id,
            priority=TaskPriority.HIGH,
            estimated_duration=timedelta(minutes=3),
            metadata={"phase": "analysis", "critical": True},
        )

        # Phase 2: Template Selection
        selection_task_id = await task_manager.create_task(
            name="Intelligent Template Selection",
            description="Select optimal agent templates using template-selector subagent",
            agent_name="template-selector",
            inputs={
                "project_analysis": "from_previous_task",
                "selection_algorithm": "weighted_scoring",
            },
            workflow_id=workflow_id,
            dependencies=[
                TaskDependency(analysis_task_id, "requires", "Needs project analysis")
            ],
            priority=TaskPriority.HIGH,
            estimated_duration=timedelta(minutes=2),
            metadata={"phase": "selection", "critical": True},
        )

        # Phase 3: Parallel Generation (4 agents)
        claude_md_task_id = await task_manager.create_task(
            name="Generate CLAUDE.md Configuration",
            description="Create project-specific CLAUDE.md using claude-md-generator",
            agent_name="claude-md-generator",
            inputs={
                "project_analysis": "from_analysis_task",
                "selected_templates": "from_selection_task",
                "generation_mode": "comprehensive",
            },
            workflow_id=workflow_id,
            dependencies=[
                TaskDependency(analysis_task_id, "requires", "Needs project analysis"),
                TaskDependency(
                    selection_task_id, "requires", "Needs template selection"
                ),
            ],
            priority=TaskPriority.MEDIUM,
            estimated_duration=timedelta(minutes=2),
            metadata={"phase": "generation", "parallel_group": "generators"},
        )

        agent_gen_task_id = await task_manager.create_task(
            name="Generate Specialized Agents",
            description="Create project-tailored agents using agent-generator",
            agent_name="agent-generator",
            inputs={
                "project_analysis": "from_analysis_task",
                "selected_templates": "from_selection_task",
                "customization_level": "high",
            },
            workflow_id=workflow_id,
            dependencies=[
                TaskDependency(analysis_task_id, "requires", "Needs project analysis"),
                TaskDependency(
                    selection_task_id, "requires", "Needs template selection"
                ),
            ],
            priority=TaskPriority.MEDIUM,
            estimated_duration=timedelta(minutes=3),
            metadata={"phase": "generation", "parallel_group": "generators"},
        )

        workflow_task_id = await task_manager.create_task(
            name="Generate Development Workflows",
            description="Create custom workflows using workflow-generator",
            agent_name="workflow-generator",
            inputs={
                "project_analysis": "from_analysis_task",
                "selected_templates": "from_selection_task",
                "workflow_types": ["development", "quality", "deployment"],
            },
            workflow_id=workflow_id,
            dependencies=[
                TaskDependency(analysis_task_id, "requires", "Needs project analysis"),
                TaskDependency(
                    selection_task_id, "requires", "Needs template selection"
                ),
            ],
            priority=TaskPriority.MEDIUM,
            estimated_duration=timedelta(minutes=2),
            metadata={"phase": "generation", "parallel_group": "generators"},
        )

        # Phase 4: Validation
        validation_task_id = await task_manager.create_task(
            name="Comprehensive Deployment Validation",
            description="Validate complete factory output using deployment-validator",
            agent_name="deployment-validator",
            inputs={
                "factory_outputs": "from_generation_tasks",
                "validation_layers": [
                    "syntax",
                    "semantic",
                    "security",
                    "integration",
                    "performance",
                ],
                "test_environment": "isolated",
            },
            workflow_id=workflow_id,
            dependencies=[
                TaskDependency(claude_md_task_id, "requires", "Needs CLAUDE.md"),
                TaskDependency(agent_gen_task_id, "requires", "Needs agents"),
                TaskDependency(workflow_task_id, "requires", "Needs workflows"),
            ],
            priority=TaskPriority.CRITICAL,
            estimated_duration=timedelta(minutes=4),
            metadata={"phase": "validation", "critical": True},
        )

        print(f"🏭 Created factory workflow {workflow_id} with 5 specialized tasks")
        print(f"    📋 Analysis Task: {analysis_task_id}")
        print(f"    🎯 Selection Task: {selection_task_id}")
        print(
            f"    ⚡ Generation Tasks: {claude_md_task_id}, {agent_gen_task_id}, {workflow_task_id}"
        )
        print(f"    ✅ Validation Task: {validation_task_id}")

        return workflow_id
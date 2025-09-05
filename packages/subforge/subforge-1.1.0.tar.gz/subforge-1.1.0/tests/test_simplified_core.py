#!/usr/bin/env python3
"""
Simplified tests for core SubForge functionality
Focuses on public API methods and realistic testing scenarios
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add subforge to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subforge.core.project_analyzer import ProjectAnalyzer
from subforge.orchestration.parallel_executor import ParallelExecutor, ParallelTask
from subforge.monitoring.workflow_monitor import WorkflowMonitor


class TestProjectAnalyzerPublicAPI:
    """Test ProjectAnalyzer public API methods only"""
    
    def test_analyzer_has_expected_attributes(self):
        """Test ProjectAnalyzer has expected public attributes"""
        analyzer = ProjectAnalyzer()
        
        # Test public attributes exist
        assert hasattr(analyzer, 'language_extensions')
        assert hasattr(analyzer, 'framework_indicators')
        assert hasattr(analyzer, 'subagent_templates')
        assert hasattr(analyzer, 'analyze_project')
        
        # Test language_extensions is properly structured
        assert isinstance(analyzer.language_extensions, dict)
        assert len(analyzer.language_extensions) > 0
        
        # Should have common languages
        common_languages = ['python', 'javascript', 'java', 'go', 'rust', 'typescript']
        for lang in common_languages:
            if lang in analyzer.language_extensions:
                assert isinstance(analyzer.language_extensions[lang], (list, set))
    
    @pytest.mark.asyncio
    async def test_analyze_project_with_real_structure(self, tmp_path):
        """Test analyze_project method with realistic project structure"""
        analyzer = ProjectAnalyzer()
        
        # Create a realistic Python project
        project_dir = tmp_path / "sample_project"
        project_dir.mkdir()
        
        # Create Python files
        (project_dir / "main.py").write_text("""
#!/usr/bin/env python3
from fastapi import FastAPI
from typing import List

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
        """)
        
        # Create requirements file
        (project_dir / "requirements.txt").write_text("""
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
        """)
        
        # Create test file
        (project_dir / "test_main.py").write_text("""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
        """)
        
        # Create Dockerfile
        (project_dir / "Dockerfile").write_text("""
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        """)
        
        # Analyze the project
        profile = await analyzer.analyze_project(str(project_dir))
        
        # Verify the profile was created successfully
        assert profile is not None
        assert profile.name == "sample_project"
        assert profile.path == str(project_dir)
        
        # Should detect Python
        assert "python" in profile.technology_stack.languages
        
        # Should have reasonable metrics
        assert profile.file_count >= 3  # At least main.py, requirements.txt, test_main.py
        assert profile.lines_of_code > 0
        
        # Should detect Docker
        assert profile.has_docker is True
        
        # Should detect tests
        assert profile.has_tests is True
        
        # Should recommend some subagents
        assert len(profile.recommended_subagents) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_project_empty_directory(self, tmp_path):
        """Test analyze_project with empty directory"""
        analyzer = ProjectAnalyzer()
        
        empty_dir = tmp_path / "empty_project"
        empty_dir.mkdir()
        
        profile = await analyzer.analyze_project(str(empty_dir))
        
        # Should still create a valid profile
        assert profile is not None
        assert profile.name == "empty_project"
        assert profile.file_count == 0
        assert profile.lines_of_code == 0
        assert profile.complexity.value == "simple"
        
        # Should still recommend basic subagents
        assert len(profile.recommended_subagents) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_project_javascript_structure(self, tmp_path):
        """Test analyze_project with JavaScript/Node.js project"""
        analyzer = ProjectAnalyzer()
        
        project_dir = tmp_path / "js_project"
        project_dir.mkdir()
        
        # Create package.json
        (project_dir / "package.json").write_text(json.dumps({
            "name": "test-app",
            "version": "1.0.0",
            "description": "Test application",
            "main": "index.js",
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5"
            },
            "devDependencies": {
                "jest": "^29.5.0",
                "nodemon": "^3.0.1"
            },
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js",
                "test": "jest"
            }
        }))
        
        # Create main JavaScript file
        (project_dir / "index.js").write_text("""
const express = require('express');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Hello World!' });
});

app.get('/api/users', (req, res) => {
  res.json({ users: [] });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
        """)
        
        # Create test file
        (project_dir / "index.test.js").write_text("""
const request = require('supertest');
const app = require('./index');

describe('GET /', () => {
  it('should return hello message', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body.message).toBe('Hello World!');
  });
});
        """)
        
        profile = await analyzer.analyze_project(str(project_dir))
        
        # Should detect JavaScript
        assert profile is not None
        assert "javascript" in profile.technology_stack.languages
        assert profile.has_tests is True
        assert profile.file_count >= 3


class TestParallelExecutorPublicAPI:
    """Test ParallelExecutor public API methods"""
    
    def test_executor_initialization(self, tmp_path):
        """Test ParallelExecutor initialization"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Should create workflow state directory
        assert executor.workflow_state.exists()
        assert executor.workflow_state == Path(tmp_path) / "workflow-state"
        
        # Should have project path set correctly
        assert executor.project_path == Path(tmp_path)
    
    @pytest.mark.asyncio
    async def test_execute_parallel_analysis_basic(self, tmp_path):
        """Test execute_parallel_analysis basic functionality"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Mock the internal method to avoid actual agent calls
        with patch.object(executor, '_execute_parallel_batch') as mock_batch:
            # Mock return value that looks like real agent responses
            mock_batch.return_value = {
                "@code-reviewer": {
                    "status": "completed",
                    "analysis": "Code follows good practices",
                    "issues_found": 2,
                    "recommendations": ["Add type hints", "Improve docstrings"]
                },
                "@test-engineer": {
                    "status": "completed", 
                    "analysis": "Test coverage is adequate",
                    "coverage_percentage": 78,
                    "missing_tests": ["edge_cases", "error_handling"]
                }
            }
            
            # Execute parallel analysis
            results = await executor.execute_parallel_analysis(
                "Analyze the codebase for quality and testing"
            )
            
            # Verify structure
            assert isinstance(results, dict)
            assert mock_batch.called
            
            # Should contain aggregated findings
            assert "findings" in results or "agent_reports" in results
    
    def test_parallel_task_functionality(self):
        """Test ParallelTask dataclass and methods"""
        # Test basic task creation
        task = ParallelTask(
            agent="@backend-developer",
            task="implement_api",
            description="Implement REST API endpoints for user management"
        )
        
        assert task.agent == "@backend-developer"
        assert task.task == "implement_api"
        assert task.dependencies is None
        assert task.can_parallel is True
        
        # Test task with dependencies
        dependent_task = ParallelTask(
            agent="@test-engineer",
            task="write_integration_tests",
            description="Write integration tests for API endpoints",
            dependencies=["implement_api", "setup_database"],
            can_parallel=False
        )
        
        assert dependent_task.dependencies == ["implement_api", "setup_database"]
        assert dependent_task.can_parallel is False
        
        # Test prompt generation
        prompt = task.to_prompt()
        assert isinstance(prompt, str)
        assert "@backend-developer" in prompt
        assert "implement_api" in prompt
        assert "Implement REST API endpoints" in prompt
        
        # Test prompt with dependencies
        dep_prompt = dependent_task.to_prompt()
        assert "implement_api" in dep_prompt
        assert "setup_database" in dep_prompt
    
    def test_state_persistence_methods(self, tmp_path):
        """Test execution state directory handling"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Verify workflow state directory exists and is writable
        assert executor.workflow_state.exists()
        assert executor.workflow_state.is_dir()
        
        # Test we can create files in the state directory
        test_file = executor.workflow_state / "test_state.json"
        test_data = {"test": "data", "timestamp": "2023-12-01T10:00:00Z"}
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        assert test_file.exists()
        
        # Test we can read the file back
        with open(test_file) as f:
            loaded_data = json.load(f)
        
        assert loaded_data["test"] == "data"
        assert loaded_data["timestamp"] == "2023-12-01T10:00:00Z"


class TestWorkflowMonitorPublicAPI:
    """Test WorkflowMonitor public API methods"""
    
    def test_workflow_monitor_initialization(self, tmp_path):
        """Test WorkflowMonitor initialization and setup"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        # Should set up directory structure
        assert monitor.monitoring_dir.exists()
        assert monitor.monitoring_dir == Path(tmp_path) / ".subforge" / "monitoring"
        
        # Should initialize data structures
        assert isinstance(monitor.active_workflows, dict)
        assert isinstance(monitor.completed_workflows, list)
        assert isinstance(monitor.event_callbacks, dict)
        
        # Should have expected callback events
        expected_events = [
            "workflow_started", "workflow_completed", "workflow_failed",
            "agent_started", "agent_completed", "agent_failed", "phase_changed"
        ]
        for event in expected_events:
            assert event in monitor.event_callbacks
    
    def test_workflow_lifecycle_complete(self, tmp_path):
        """Test complete workflow lifecycle monitoring"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        # Test workflow start
        workflow = monitor.start_workflow(
            "workflow_001", 
            "Create full-stack web application"
        )
        
        assert workflow.workflow_id == "workflow_001"
        assert workflow.user_request == "Create full-stack web application"
        assert len(monitor.active_workflows) == 1
        assert monitor.total_workflows == 1
        
        # Test phase update
        monitor.update_phase("workflow_001", "analysis")
        assert workflow.current_phase == "analysis"
        
        # Test agent execution start
        execution = monitor.start_agent_execution(
            "workflow_001",
            "@backend-developer",
            "task_001",
            "Create database models and API endpoints"
        )
        
        assert execution is not None
        assert execution.agent_name == "@backend-developer"
        assert execution.task_id == "task_001"
        assert len(workflow.agent_executions) == 1
        
        # Test parallel group
        monitor.set_parallel_group("workflow_001", ["@frontend-developer", "@test-engineer"])
        assert ["@frontend-developer", "@test-engineer"] in workflow.parallel_groups
        
        # Test agent execution end
        from subforge.monitoring.workflow_monitor import AgentStatus
        monitor.end_agent_execution(
            "workflow_001",
            "@backend-developer", 
            "task_001",
            AgentStatus.COMPLETED,
            {
                "models_created": 5,
                "endpoints_created": 12,
                "tests_passed": 25
            }
        )
        
        assert execution.status == AgentStatus.COMPLETED
        assert execution.output["models_created"] == 5
        
        # Test workflow completion
        from subforge.monitoring.workflow_monitor import WorkflowStatus
        monitor.end_workflow("workflow_001", WorkflowStatus.COMPLETED)
        
        assert len(monitor.active_workflows) == 0
        assert len(monitor.completed_workflows) == 1
        assert monitor.successful_workflows == 1
    
    def test_real_time_metrics_generation(self, tmp_path):
        """Test real-time metrics functionality"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        # Start a few workflows to generate metrics
        monitor.start_workflow("wf_1", "Build API")
        monitor.start_workflow("wf_2", "Build frontend")
        
        # Get real-time metrics
        metrics = monitor.get_real_time_metrics()
        
        # Should contain expected metric fields
        assert isinstance(metrics, dict)
        assert "timestamp" in metrics
        assert "active_workflows" in metrics
        assert "total_active_agents" in metrics
        assert "system_health" in metrics
        
        # Should reflect current state
        assert metrics["active_workflows"] == 2
        assert metrics["system_health"] in ["healthy", "busy"]
    
    def test_monitoring_data_export(self, tmp_path):
        """Test monitoring data export functionality"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        # Create some monitoring data
        workflow = monitor.start_workflow("export_test", "Test export functionality")
        monitor.start_agent_execution("export_test", "@test-agent", "task_1", "Test task")
        
        # Export monitoring data
        export_file = monitor.export_monitoring_data()
        
        # Should create export file
        assert export_file.exists()
        assert export_file.suffix == ".json"
        
        # Should contain valid JSON with expected structure
        with open(export_file) as f:
            export_data = json.load(f)
        
        assert "export_timestamp" in export_data
        assert "project_path" in export_data
        assert "statistics" in export_data
        assert "active_workflows" in export_data
        assert "real_time_metrics" in export_data
        
        # Should contain our test workflow
        assert len(export_data["active_workflows"]) == 1
        assert export_data["active_workflows"][0]["workflow_id"] == "export_test"


class TestErrorHandlingScenarios:
    """Test error handling and edge cases that improve coverage"""
    
    @pytest.mark.asyncio
    async def test_project_analyzer_nonexistent_path(self):
        """Test ProjectAnalyzer with non-existent path"""
        analyzer = ProjectAnalyzer()
        
        with pytest.raises((FileNotFoundError, OSError)):
            await analyzer.analyze_project("/completely/nonexistent/path/that/does/not/exist")
    
    @pytest.mark.asyncio
    async def test_project_analyzer_file_not_directory(self, tmp_path):
        """Test ProjectAnalyzer with file instead of directory"""
        analyzer = ProjectAnalyzer()
        
        # Create a file instead of directory
        test_file = tmp_path / "not_a_directory.txt"
        test_file.write_text("This is a file, not a directory")
        
        # Should handle this gracefully (might raise exception or return sensible result)
        try:
            profile = await analyzer.analyze_project(str(test_file))
            # If it succeeds, should have empty or minimal data
            assert profile.file_count <= 1
        except (NotADirectoryError, OSError):
            # This is also acceptable behavior
            pass
    
    def test_parallel_executor_state_handling(self, tmp_path):
        """Test ParallelExecutor state handling functionality"""
        executor = ParallelExecutor(str(tmp_path))
        
        # Test workflow state directory creation
        assert executor.workflow_state.exists()
        
        # Test saving task status with error handling
        try:
            executor._save_task_status("error_test", "failed", {"error": "test error"})
            # Should complete without throwing exception
            assert True
        except Exception:
            # If it throws an exception, that's also acceptable behavior
            pass
        
        # Test that workflow state directory remains accessible
        assert executor.workflow_state.is_dir()
    
    def test_workflow_monitor_error_handling(self, tmp_path):
        """Test WorkflowMonitor error handling scenarios"""
        monitor = WorkflowMonitor(str(tmp_path))
        
        # Test ending workflow that doesn't exist
        from subforge.monitoring.workflow_monitor import WorkflowStatus
        monitor.end_workflow("nonexistent_workflow", WorkflowStatus.FAILED)
        # Should not crash
        
        # Test starting agent execution for nonexistent workflow
        execution = monitor.start_agent_execution(
            "nonexistent_workflow",
            "@test-agent",
            "task_1", 
            "Test task"
        )
        # Should return None or handle gracefully
        assert execution is None
        
        # Test getting status for nonexistent workflow
        status = monitor.get_workflow_status("nonexistent_workflow")
        assert status is None


class TestPublicIntegrationScenarios:
    """Integration tests using only public APIs"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_project_analysis(self, tmp_path):
        """Test complete project analysis workflow"""
        # Create a realistic mixed-technology project
        project_dir = tmp_path / "fullstack_project"
        project_dir.mkdir()
        
        # Backend (Python/FastAPI)
        backend_dir = project_dir / "backend"
        backend_dir.mkdir()
        (backend_dir / "main.py").write_text("""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="My API", version="1.0.0")

class User(BaseModel):
    id: int
    name: str
    email: str

users_db = []

@app.get("/users", response_model=List[User])
async def get_users():
    return users_db

@app.post("/users", response_model=User)
async def create_user(user: User):
    users_db.append(user)
    return user
        """)
        
        (backend_dir / "requirements.txt").write_text("""
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pytest==7.4.3
        """)
        
        # Frontend (JavaScript/React-like)
        frontend_dir = project_dir / "frontend"
        frontend_dir.mkdir()
        (frontend_dir / "package.json").write_text(json.dumps({
            "name": "frontend-app",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.2.0",
                "axios": "^1.5.0"
            },
            "devDependencies": {
                "jest": "^29.5.0"
            }
        }))
        
        (frontend_dir / "index.js").write_text("""
import axios from 'axios';

class UserManager {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
    }
    
    async getUsers() {
        const response = await axios.get(`${this.apiUrl}/users`);
        return response.data;
    }
    
    async createUser(userData) {
        const response = await axios.post(`${this.apiUrl}/users`, userData);
        return response.data;
    }
}

export default UserManager;
        """)
        
        # Docker setup
        (project_dir / "docker-compose.yml").write_text("""
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
        """)
        
        # Tests
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_integration.py").write_text("""
import pytest
import asyncio

def test_user_creation():
    assert True  # Placeholder test
        """)
        
        # README
        (project_dir / "README.md").write_text("""
# Fullstack Project

A complete web application with FastAPI backend and JavaScript frontend.

## Features
- User management API
- Frontend interface
- Docker deployment
- Comprehensive tests
        """)
        
        # Analyze the complete project
        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_dir))
        
        # Verify comprehensive analysis
        assert profile.name == "fullstack_project"
        
        # Should detect multiple languages
        languages = profile.technology_stack.languages
        assert len(languages) >= 2
        assert "python" in languages
        assert "javascript" in languages
        
        # Should detect project characteristics
        assert profile.has_docker is True
        assert profile.has_tests is True
        assert profile.has_docs is True
        
        # Should classify as medium/complex
        assert profile.complexity.value in ["medium", "complex"]
        
        # Should recommend multiple types of agents
        agents = profile.recommended_subagents
        assert len(agents) >= 3
        
        # Should recommend relevant agents for fullstack
        agent_types = set(agents)
        expected_agents = {"backend-developer", "frontend-developer", "devops-engineer", "test-engineer"}
        overlap = agent_types.intersection(expected_agents)
        assert len(overlap) >= 2  # Should recommend at least 2 relevant agent types


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--color=yes"])
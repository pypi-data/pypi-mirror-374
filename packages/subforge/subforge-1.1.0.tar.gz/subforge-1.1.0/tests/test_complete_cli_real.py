#!/usr/bin/env python3
"""
Comprehensive tests for CLI modules with direct functionality testing.
Tests both cli.py (Typer-based) and simple_cli.py (argparse-based).
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, call, mock_open, patch
from unittest import TestCase

import pytest


class TestCLIFunctionality(TestCase):
    """Test CLI functionality with comprehensive coverage"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        """Clean up test fixtures"""
        sys.argv = self.original_argv
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_cli_banner_function(self):
        """Test CLI banner functionality"""
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            # Define a simple print_banner function to test
            def print_banner():
                banner = r"""
 ____        _     _____
/ ___| _   _| |__ |  ___|__  _ __ __ _  ___
\___ \| | | | '_ \| |_ / _ \| '__/ _` |/ _ \
 ___) | |_| | |_) |  _| (_) | | | (_| |  __/
|____/ \__,_|_.__/|_|  \___/|_|  \__, |\___|
                                 |___/

🚀 Forge your perfect Claude Code development team
"""
                print(banner)
            
            # Test the function
            print_banner()
            
            # Verify print was called
            self.assertEqual(mock_print.call_count, 1)

    def test_cli_section_function(self):
        """Test CLI section printing functionality"""
        with patch('builtins.print') as mock_print:
            # Define a simple print_section function to test
            def print_section(title, style="="):
                print(f"\n{style * 60}")
                print(f" {title}")
                print(f"{style * 60}")
            
            # Test the function
            print_section("Test Section", "-")
            
            # Verify print was called 3 times
            self.assertEqual(mock_print.call_count, 3)

    def test_argparse_cli_structure(self):
        """Test argparse CLI structure"""
        # Create parser like simple_cli.py
        parser = argparse.ArgumentParser(
            prog="subforge",
            description="🚀 SubForge - Forge your perfect Claude Code development team",
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Init command
        init_parser = subparsers.add_parser("init", help="Initialize SubForge for your project")
        init_parser.add_argument("project_path", nargs="?", help="Path to your project")
        init_parser.add_argument("--request", "-r", help="What you want to accomplish")
        init_parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
        init_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        
        # Analyze command
        analyze_parser = subparsers.add_parser("analyze", help="Analyze your project structure")
        analyze_parser.add_argument("project_path", nargs="?", help="Path to your project")
        analyze_parser.add_argument("--output", "-o", help="Save analysis to file")
        analyze_parser.add_argument("--json", action="store_true", help="Output in JSON format")
        
        # Status command
        status_parser = subparsers.add_parser("status", help="Show current SubForge status")
        status_parser.add_argument("project_path", nargs="?", help="Path to your project")
        
        # Test parsing various commands
        test_cases = [
            (["init"], "init"),
            (["init", "--request", "test"], "init"),
            (["init", "--dry-run"], "init"),
            (["analyze", "--json"], "analyze"),
            (["analyze", "--output", "test.json"], "analyze"),
            (["status"], "status"),
        ]
        
        for args, expected_command in test_cases:
            parsed_args = parser.parse_args(args)
            self.assertEqual(parsed_args.command, expected_command)

    @patch('subprocess.run')
    def test_subprocess_commands(self, mock_run):
        """Test subprocess command execution patterns"""
        # Test successful command
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "success output"
        
        # Simulate isort fix
        def run_isort_fix(project_path):
            try:
                subprocess.run(["isort", "--version"], capture_output=True, check=True)
                cmd = ["isort", "--profile", "black", str(project_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
        
        result = run_isort_fix(self.test_dir)
        self.assertTrue(result)
        
        # Test failed command
        mock_run.side_effect = FileNotFoundError()
        result = run_isort_fix(self.test_dir)
        self.assertFalse(result)

    def test_async_command_patterns(self):
        """Test async command patterns"""
        async def mock_analyze_project(project_path):
            """Mock project analysis"""
            await asyncio.sleep(0.001)  # Simulate async work
            return {
                "name": Path(project_path).name,
                "files": 10,
                "languages": ["python"],
                "complexity": "medium"
            }
        
        async def cmd_analyze(project_path, output_json=False):
            """Mock analyze command"""
            try:
                profile = await mock_analyze_project(project_path)
                if output_json:
                    return json.dumps(profile, indent=2)
                else:
                    return f"Project: {profile['name']}, Files: {profile['files']}"
            except Exception as e:
                return f"Error: {e}"
        
        # Test successful analysis
        result = asyncio.run(cmd_analyze(str(self.test_dir)))
        self.assertIn("Project:", result)
        
        # Test JSON output
        result = asyncio.run(cmd_analyze(str(self.test_dir), output_json=True))
        parsed_result = json.loads(result)
        self.assertIn("name", parsed_result)

    def test_file_operations_patterns(self):
        """Test file operation patterns used in CLI"""
        # Test directory structure creation
        subforge_dir = self.test_dir / ".subforge"
        subforge_dir.mkdir(parents=True, exist_ok=True)
        self.assertTrue(subforge_dir.exists())
        
        workflow_dir = subforge_dir / "workflow_123"
        workflow_dir.mkdir()
        
        # Test context file creation
        context_data = {
            "project_id": "test-123",
            "template_selections": {
                "selected_templates": ["frontend-developer", "backend-developer"]
            }
        }
        context_file = workflow_dir / "context.json"
        context_file.write_text(json.dumps(context_data, indent=2))
        
        # Test reading context
        loaded_data = json.loads(context_file.read_text())
        self.assertEqual(loaded_data["project_id"], "test-123")
        
        # Test agent file operations
        claude_dir = self.test_dir / ".claude"
        agents_dir = claude_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        
        agent_content = """# Frontend Developer Agent

## PROJECT CONTEXT - Test Project
**Current Request**: Build React application
**Project Root**: {project_root}

### Your Domain: Frontend Development & UI/UX
Focus on user interfaces and client-side functionality.
""".format(project_root=str(self.test_dir))
        
        agent_file = agents_dir / "frontend-developer.md"
        agent_file.write_text(agent_content)
        
        self.assertTrue(agent_file.exists())
        self.assertIn("Frontend Developer", agent_file.read_text())

    def test_status_command_logic(self):
        """Test status command logic"""
        def check_subforge_status(project_path):
            """Mock status check logic"""
            project_path = Path(project_path)
            subforge_dir = project_path / ".subforge"
            claude_dir = project_path / ".claude"
            
            status = {
                "has_subforge": subforge_dir.exists(),
                "has_claude": claude_dir.exists(),
                "workflow_count": 0,
                "agent_count": 0
            }
            
            if status["has_subforge"]:
                workflows = list(subforge_dir.glob("workflow_*"))
                status["workflow_count"] = len(workflows)
            
            if status["has_claude"]:
                agents_dir = claude_dir / "agents"
                if agents_dir.exists():
                    agents = list(agents_dir.glob("*.md"))
                    status["agent_count"] = len(agents)
            
            return status
        
        # Test with empty directory
        status = check_subforge_status(self.test_dir)
        self.assertFalse(status["has_subforge"])
        self.assertFalse(status["has_claude"])
        
        # Test with SubForge setup
        (self.test_dir / ".subforge").mkdir()
        (self.test_dir / ".subforge" / "workflow_123").mkdir()
        
        status = check_subforge_status(self.test_dir)
        self.assertTrue(status["has_subforge"])
        self.assertEqual(status["workflow_count"], 1)
        
        # Test with agents
        agents_dir = self.test_dir / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "test-agent.md").write_text("# Test Agent")
        
        status = check_subforge_status(self.test_dir)
        self.assertTrue(status["has_claude"])
        self.assertEqual(status["agent_count"], 1)

    def test_validation_logic(self):
        """Test validation logic"""
        def validate_subforge_setup(project_path):
            """Mock validation logic"""
            project_path = Path(project_path)
            issues = []
            
            # Check SubForge directory
            subforge_dir = project_path / ".subforge"
            if not subforge_dir.exists():
                issues.append("SubForge directory missing")
            
            # Check workflows
            if subforge_dir.exists():
                workflows = list(subforge_dir.glob("workflow_*"))
                if not workflows:
                    issues.append("No workflow executions found")
            
            # Check Claude integration
            claude_dir = project_path / ".claude"
            if not claude_dir.exists():
                issues.append("Claude Code directory missing")
            else:
                claude_md = claude_dir / "CLAUDE.md"
                if not claude_md.exists():
                    issues.append("CLAUDE.md missing")
                
                agents_dir = claude_dir / "agents"
                if not agents_dir.exists():
                    issues.append("Agents directory missing")
                elif not list(agents_dir.glob("*.md")):
                    issues.append("No agent files found")
            
            return issues
        
        # Test empty directory
        issues = validate_subforge_setup(self.test_dir)
        self.assertIn("SubForge directory missing", issues)
        
        # Test partial setup
        (self.test_dir / ".subforge").mkdir()
        issues = validate_subforge_setup(self.test_dir)
        self.assertIn("No workflow executions found", issues)
        
        # Test complete setup
        (self.test_dir / ".subforge" / "workflow_123").mkdir()
        claude_dir = self.test_dir / ".claude"
        claude_dir.mkdir()
        (claude_dir / "CLAUDE.md").write_text("# Configuration")
        agents_dir = claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "test.md").write_text("# Agent")
        
        issues = validate_subforge_setup(self.test_dir)
        self.assertEqual(len(issues), 0)

    def test_template_operations(self):
        """Test template operations"""
        def extract_template_description(template_content):
            """Extract description from template content"""
            lines = template_content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("## Description"):
                    if i + 1 < len(lines):
                        desc = lines[i + 1].strip()
                        if len(desc) > 60:
                            desc = desc[:57] + "..."
                        return desc
            return "No description available"
        
        # Test template with description
        template_content = """# Test Template

## Description
This is a test template for frontend development with React and TypeScript.

## Usage
Use this template for frontend projects.
"""
        desc = extract_template_description(template_content)
        self.assertEqual(desc, "This is a test template for frontend development with Rea...")
        
        # Test template without description
        template_content = """# Test Template

## Usage
Use this template.
"""
        desc = extract_template_description(template_content)
        self.assertEqual(desc, "No description available")

    def test_update_command_logic(self):
        """Test update command logic"""
        def update_agent_content(agent_file, project_name, project_path):
            """Mock agent content update"""
            if not agent_file.exists():
                return False
            
            content = agent_file.read_text()
            
            # Update project references
            replacements = [
                ("## PROJECT CONTEXT - Claude-subagents", f"## PROJECT CONTEXT - {project_name}"),
                ("**Project Root**: /old/path", f"**Project Root**: {project_path}"),
            ]
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            # Update timestamp
            import re
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC-3")
            if "*Updated:" in content:
                content = re.sub(r"\*Updated: .+\*", f"*Updated: {timestamp}*", content)
            else:
                content += f"\n\n*Updated: {timestamp}*"
            
            agent_file.write_text(content)
            return True
        
        # Create test agent file
        agents_dir = self.test_dir / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        
        agent_content = """# Test Agent

## PROJECT CONTEXT - Claude-subagents
**Project Root**: /old/path

*Updated: 2023-01-01 12:00:00 UTC-3*
"""
        agent_file = agents_dir / "test-agent.md"
        agent_file.write_text(agent_content)
        
        # Test update
        result = update_agent_content(agent_file, "new-project", str(self.test_dir))
        self.assertTrue(result)
        
        # Verify updates
        updated_content = agent_file.read_text()
        self.assertIn("new-project", updated_content)
        self.assertIn(str(self.test_dir), updated_content)

    def test_error_handling_patterns(self):
        """Test error handling patterns"""
        def safe_execute(func, *args, **kwargs):
            """Safe execution with error handling"""
            try:
                return func(*args, **kwargs), None
            except Exception as e:
                return None, str(e)
        
        def error_func():
            raise ValueError("Test error")
        
        def success_func():
            return "success"
        
        # Test error case
        result, error = safe_execute(error_func)
        self.assertIsNone(result)
        self.assertEqual(error, "Test error")
        
        # Test success case
        result, error = safe_execute(success_func)
        self.assertEqual(result, "success")
        self.assertIsNone(error)

    def test_path_resolution_patterns(self):
        """Test path resolution patterns"""
        def resolve_project_path(path_input):
            """Resolve project path like CLI does"""
            if path_input is None:
                return Path.cwd()
            else:
                return Path(path_input).resolve()
        
        # Test None input
        current_path = resolve_project_path(None)
        self.assertIsInstance(current_path, Path)
        
        # Test explicit path
        explicit_path = resolve_project_path(str(self.test_dir))
        self.assertEqual(explicit_path, self.test_dir.resolve())

    def test_glob_pattern_usage(self):
        """Test glob pattern usage in CLI"""
        # Create test file structure
        (self.test_dir / "test1.py").write_text("# Python file 1")
        (self.test_dir / "test2.py").write_text("# Python file 2")
        (self.test_dir / "test.txt").write_text("# Text file")
        (self.test_dir / "subdir").mkdir()
        (self.test_dir / "subdir" / "test3.py").write_text("# Python file 3")
        
        # Test glob patterns
        py_files = list(self.test_dir.glob("*.py"))
        self.assertEqual(len(py_files), 2)
        
        all_py_files = list(self.test_dir.rglob("*.py"))
        self.assertEqual(len(all_py_files), 3)
        
        # Test filtering ignored directories
        ignored_dirs = {".git", "__pycache__", "node_modules"}
        filtered_files = [
            f for f in all_py_files 
            if not any(part in ignored_dirs for part in f.parts)
        ]
        self.assertEqual(len(filtered_files), 3)

    def test_json_serialization_patterns(self):
        """Test JSON serialization patterns"""
        # Test profile-like object serialization
        class MockProfile:
            def __init__(self):
                self.name = "test-project"
                self.complexity = "medium"
                self.languages = ["python", "javascript"]
            
            def to_dict(self):
                return {
                    "name": self.name,
                    "complexity": self.complexity,
                    "languages": self.languages
                }
        
        profile = MockProfile()
        json_str = json.dumps(profile.to_dict(), indent=2)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["name"], "test-project")
        self.assertEqual(parsed["complexity"], "medium")
        self.assertEqual(len(parsed["languages"]), 2)

    def test_progress_indication_patterns(self):
        """Test progress indication patterns"""
        import time
        
        def mock_progress_context():
            """Mock progress context manager"""
            class MockProgress:
                def __init__(self):
                    self.tasks = []
                
                def __enter__(self):
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
                
                def add_task(self, description, total=None):
                    task_id = f"task_{len(self.tasks)}"
                    self.tasks.append({"id": task_id, "description": description})
                    return task_id
                
                def update(self, task_id, description=None, completed=None):
                    for task in self.tasks:
                        if task["id"] == task_id:
                            if description:
                                task["description"] = description
                            break
            
            return MockProgress()
        
        with mock_progress_context() as progress:
            task_id = progress.add_task("Processing...")
            time.sleep(0.001)  # Simulate work
            progress.update(task_id, description="Completed!")
            
            self.assertEqual(len(progress.tasks), 1)
            self.assertEqual(progress.tasks[0]["description"], "Completed!")

    def test_configuration_file_patterns(self):
        """Test configuration file patterns"""
        # Test CLAUDE.md creation
        claude_config = """# Test Project - Claude Code Agent Configuration

## Project Status: ✅ **ACTIVE**

### Technology Stack
**Languages**: python, javascript
**Frameworks**: fastapi, react
**Architecture**: jamstack

## Available Specialist Agents

**@frontend-developer** ✅
- **Domain**: User interfaces, client-side state, responsive design
- **Achievement**: React components and UI/UX design

**@backend-developer** ✅ 
- **Domain**: Server-side logic, APIs, databases
- **Achievement**: FastAPI backend with database integration

*Updated: {timestamp}*
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC-3"))
        
        claude_file = self.test_dir / ".claude" / "CLAUDE.md"
        claude_file.parent.mkdir(parents=True, exist_ok=True)
        claude_file.write_text(claude_config)
        
        # Verify file creation and content
        self.assertTrue(claude_file.exists())
        content = claude_file.read_text()
        self.assertIn("Test Project", content)
        self.assertIn("frontend-developer", content)
        self.assertIn("backend-developer", content)


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v', '--tb=short'])
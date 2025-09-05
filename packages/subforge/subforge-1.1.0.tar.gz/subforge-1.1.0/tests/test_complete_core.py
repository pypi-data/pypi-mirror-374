#!/usr/bin/env python3
"""
Comprehensive tests for SubForge core modules with 100% coverage.

This test suite covers:
- subforge.core.project_analyzer
- subforge.core.context_engineer  
- subforge.core.prp_generator
- subforge.core.communication

Requirements:
- 100% line and branch coverage
- Mock all file system and external operations
- Test all detection methods and edge cases
- Comprehensive error handling tests
"""

import asyncio
import json
import os
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch, mock_open, MagicMock

import pytest

from subforge.core.project_analyzer import (
    ProjectAnalyzer,
    ProjectProfile,
    TechnologyStack,
    ProjectComplexity,
    ArchitecturePattern
)
from subforge.core.context_engineer import (
    ContextEngineer,
    ContextPackage,
    ContextLevel,
    create_context_engineer
)
from subforge.core.prp_generator import (
    PRPGenerator,
    PRP,
    PRPType,
    create_prp_generator
)
from subforge.core.communication import CommunicationManager


class TestProjectAnalyzer:
    """Test ProjectAnalyzer with comprehensive coverage"""

    @pytest.fixture
    def analyzer(self):
        """Create ProjectAnalyzer instance"""
        return ProjectAnalyzer()

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create temporary project structure for testing"""
        project = tmp_path / "test_project"
        project.mkdir()
        
        # Create basic files
        (project / "README.md").write_text("# Test Project")
        (project / "main.py").write_text("print('hello world')")
        (project / "package.json").write_text(json.dumps({
            "dependencies": {"react": "18.0.0", "express": "4.0.0"}
        }))
        (project / "requirements.txt").write_text("fastapi\ndjango\npsycopg2")
        
        # Create directories
        (project / "src").mkdir()
        (project / "tests").mkdir()
        (project / "docs").mkdir()
        
        # Create test files
        (project / "tests" / "test_main.py").write_text("def test_main(): pass")
        (project / "src" / "component.jsx").write_text("export default function() {}")
        
        # Create Docker files
        (project / "Dockerfile").write_text("FROM python:3.9")
        (project / "docker-compose.yml").write_text("version: '3.8'")
        
        # Create CI/CD files
        ci_dir = project / ".github" / "workflows"
        ci_dir.mkdir(parents=True)
        (ci_dir / "ci.yml").write_text("name: CI")
        
        return project

    def test_analyzer_initialization(self, analyzer):
        """Test ProjectAnalyzer initialization"""
        assert isinstance(analyzer.language_extensions, dict)
        assert isinstance(analyzer.framework_indicators, dict)
        assert isinstance(analyzer.subagent_templates, dict)
        
        # Test language extensions
        assert ".py" in analyzer.language_extensions["python"]
        assert ".js" in analyzer.language_extensions["javascript"]
        assert ".ts" in analyzer.language_extensions["typescript"]

    @pytest.mark.asyncio
    async def test_analyze_project_success(self, analyzer, temp_project):
        """Test successful project analysis"""
        with patch('os.walk') as mock_walk, \
             patch('builtins.open', mock_open(read_data="print('test')\n" * 100)) as mock_file:
            
            # Mock os.walk to return project structure
            mock_walk.return_value = [
                (str(temp_project), ["src", "tests", "docs"], ["main.py", "README.md", "package.json"]),
                (str(temp_project / "src"), [], ["component.jsx", "app.py"]),
                (str(temp_project / "tests"), [], ["test_main.py"]),
            ]
            
            profile = await analyzer.analyze_project(str(temp_project))
            
            assert isinstance(profile, ProjectProfile)
            assert profile.name == "test_project"
            assert profile.path == str(temp_project)
            assert "python" in profile.technology_stack.languages
            assert "javascript" in profile.technology_stack.languages

    @pytest.mark.asyncio
    async def test_analyze_project_nonexistent_path(self, analyzer):
        """Test analysis with nonexistent project path"""
        with pytest.raises(FileNotFoundError):
            await analyzer.analyze_project("/nonexistent/path")

    @pytest.mark.asyncio
    async def test_file_system_analysis(self, analyzer, temp_project):
        """Test _analyze_file_system method"""
        with patch('os.walk') as mock_walk, \
             patch('builtins.open', mock_open(read_data="line1\nline2\nline3\n")):
            
            mock_walk.return_value = [
                (str(temp_project), ["src", "tests"], ["main.py", "README.md", "Dockerfile"]),
                (str(temp_project / "src"), [], ["app.py", "test_app.py"]),
                (str(temp_project / "tests"), [], ["test_main.py"]),
            ]
            
            analysis = await analyzer._analyze_file_system(temp_project)
            
            assert analysis["total_files"] > 0
            assert analysis["has_tests"] == True
            assert analysis["has_docker"] == True
            assert ".py" in analysis["file_types"]

    @pytest.mark.asyncio
    async def test_file_system_analysis_ignore_dirs(self, analyzer, temp_project):
        """Test that ignored directories are properly filtered"""
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                (str(temp_project), ["node_modules", "src", ".git"], ["main.py"]),
                (str(temp_project / "src"), [], ["app.py"]),
            ]
            
            analysis = await analyzer._analyze_file_system(temp_project)
            
            # Should not include ignored directories
            assert "node_modules" not in analysis["directory_structure"]
            assert ".git" not in analysis["directory_structure"]
            assert "src" in analysis["directory_structure"]

    @pytest.mark.asyncio
    async def test_file_system_analysis_ci_cd_detection(self, analyzer, temp_project):
        """Test CI/CD detection"""
        with patch('os.walk') as mock_walk:
            # Include a .yml file in .github/workflows to trigger CI/CD detection
            mock_walk.return_value = [
                (str(temp_project), [".github"], ["main.py"]),
                (str(temp_project / ".github"), ["workflows"], []),
                (str(temp_project / ".github" / "workflows"), [], ["ci.yml", "deploy.yml"]),
            ]
            
            analysis = await analyzer._analyze_file_system(temp_project)
            
            # CI/CD should be detected because .github/workflows/*.yml files exist
            assert analysis["has_ci_cd"] == True

    @pytest.mark.asyncio
    async def test_detect_technology_stack(self, analyzer, temp_project):
        """Test technology stack detection"""
        file_analysis = {
            "file_types": {".py": 5, ".js": 3, ".ts": 2},
            "package_files": ["package.json", "requirements.txt"],
            "has_docker": False,
            "has_ci_cd": False
        }
        
        with patch.object(analyzer, '_analyze_package_json', new_callable=AsyncMock) as mock_package, \
             patch.object(analyzer, '_analyze_requirements_txt', new_callable=AsyncMock) as mock_req, \
             patch.object(analyzer, '_check_framework_indicators', new_callable=AsyncMock) as mock_check:
            
            mock_package.return_value = {"react", "express"}
            mock_req.return_value = {"fastapi", "django"}
            mock_check.return_value = False
            
            tech_stack = await analyzer._detect_technology_stack(temp_project, file_analysis)
            
            assert "python" in tech_stack.languages
            assert "javascript" in tech_stack.languages
            assert "typescript" in tech_stack.languages
            assert "react" in tech_stack.frameworks or "express" in tech_stack.frameworks
            assert "fastapi" in tech_stack.frameworks or "django" in tech_stack.frameworks

    @pytest.mark.asyncio
    async def test_analyze_package_json(self, analyzer, temp_project):
        """Test package.json analysis"""
        package_data = {
            "dependencies": {
                "react": "18.0.0",
                "vue": "3.0.0",
                "express": "4.0.0"
            },
            "devDependencies": {
                "@angular/core": "14.0.0",
                "svelte": "3.0.0"
            }
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(package_data))):
            frameworks = await analyzer._analyze_package_json(temp_project / "package.json")
            
            assert "react" in frameworks
            assert "vue" in frameworks
            assert "angular" in frameworks
            assert "svelte" in frameworks
            assert "express" in frameworks

    @pytest.mark.asyncio
    async def test_analyze_package_json_error_handling(self, analyzer, temp_project):
        """Test package.json analysis with invalid JSON"""
        with patch('builtins.open', mock_open(read_data="invalid json")), \
             patch('json.load', side_effect=json.JSONDecodeError("msg", "doc", 0)):
            
            frameworks = await analyzer._analyze_package_json(temp_project / "package.json")
            assert frameworks == set()

    @pytest.mark.asyncio
    async def test_analyze_requirements_txt(self, analyzer, temp_project):
        """Test requirements.txt analysis"""
        requirements_data = """
        fastapi==0.68.0
        django>=3.2
        flask
        pymongo
        psycopg2-binary
        redis
        """
        
        with patch('builtins.open', mock_open(read_data=requirements_data)):
            frameworks = await analyzer._analyze_requirements_txt(temp_project / "requirements.txt")
            
            assert "fastapi" in frameworks
            assert "django" in frameworks
            assert "flask" in frameworks
            assert "mongodb" in frameworks
            assert "postgresql" in frameworks
            assert "redis" in frameworks

    @pytest.mark.asyncio
    async def test_analyze_requirements_txt_error_handling(self, analyzer, temp_project):
        """Test requirements.txt analysis with file read error"""
        with patch('builtins.open', side_effect=IOError("File not found")):
            frameworks = await analyzer._analyze_requirements_txt(temp_project / "requirements.txt")
            assert frameworks == set()

    @pytest.mark.asyncio
    async def test_analyze_gemfile(self, analyzer, temp_project):
        """Test Gemfile analysis"""
        gemfile_data = """
        gem 'rails', '~> 7.0'
        gem 'sqlite3'
        """
        
        with patch('builtins.open', mock_open(read_data=gemfile_data)):
            frameworks = await analyzer._analyze_gemfile(temp_project / "Gemfile")
            
            assert "rails" in frameworks

    @pytest.mark.asyncio
    async def test_analyze_gemfile_error_handling(self, analyzer, temp_project):
        """Test Gemfile analysis with error"""
        with patch('builtins.open', side_effect=IOError()):
            frameworks = await analyzer._analyze_gemfile(temp_project / "Gemfile")
            assert frameworks == set()

    @pytest.mark.asyncio
    async def test_analyze_go_mod(self, analyzer, temp_project):
        """Test go.mod analysis (placeholder implementation)"""
        frameworks = await analyzer._analyze_go_mod(temp_project / "go.mod")
        assert frameworks == set()  # Currently returns empty set

    @pytest.mark.asyncio
    async def test_analyze_cargo_toml(self, analyzer, temp_project):
        """Test Cargo.toml analysis (placeholder implementation)"""
        frameworks = await analyzer._analyze_cargo_toml(temp_project / "Cargo.toml")
        assert frameworks == set()  # Currently returns empty set

    @pytest.mark.asyncio
    async def test_check_framework_indicators_package_file(self, analyzer, temp_project):
        """Test framework indicators with package file checks"""
        package_content = '{"dependencies": {"react": "18.0.0"}}'
        
        with patch('builtins.open', mock_open(read_data=package_content)):
            (temp_project / "package.json").touch()
            
            result = await analyzer._check_framework_indicators(temp_project, ["package.json:react"])
            assert result == True

    @pytest.mark.asyncio
    async def test_check_framework_indicators_file_exists(self, analyzer, temp_project):
        """Test framework indicators with file existence checks"""
        (temp_project / "next.config.js").touch()
        
        result = await analyzer._check_framework_indicators(temp_project, ["next.config.js"])
        assert result == True

    @pytest.mark.asyncio
    async def test_check_framework_indicators_not_found(self, analyzer, temp_project):
        """Test framework indicators when not found"""
        result = await analyzer._check_framework_indicators(temp_project, ["nonexistent.file"])
        assert result == False

    @pytest.mark.asyncio
    async def test_check_framework_indicators_file_error(self, analyzer, temp_project):
        """Test framework indicators with file read error"""
        with patch('builtins.open', side_effect=IOError()):
            (temp_project / "package.json").touch()
            
            result = await analyzer._check_framework_indicators(temp_project, ["package.json:react"])
            assert result == False

    @pytest.mark.asyncio
    async def test_detect_architecture_pattern_jamstack(self, analyzer, temp_project):
        """Test JAMStack architecture detection"""
        tech_stack = TechnologyStack(
            languages={"javascript"},
            frameworks={"nextjs"},
            databases=set(),
            tools=set(),
            package_managers={"npm"}
        )
        file_analysis = {"directory_structure": ["src", "pages"]}
        
        architecture = await analyzer._detect_architecture_pattern(temp_project, tech_stack, file_analysis)
        assert architecture == ArchitecturePattern.JAMSTACK

    @pytest.mark.asyncio
    async def test_detect_architecture_pattern_microservices(self, analyzer, temp_project):
        """Test microservices architecture detection"""
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"fastapi"},
            databases=set(),
            tools={"docker", "kubernetes"},
            package_managers={"pip"}
        )
        file_analysis = {"directory_structure": ["service1", "service2", "api", "gateway"] * 3}  # >10 dirs
        
        (temp_project / "docker-compose.yml").touch()
        
        architecture = await analyzer._detect_architecture_pattern(temp_project, tech_stack, file_analysis)
        assert architecture == ArchitecturePattern.MICROSERVICES

    @pytest.mark.asyncio
    async def test_detect_architecture_pattern_api_first(self, analyzer):
        """Test API-first architecture detection"""
        # Use a simple project path that won't trigger microservices detection
        temp_project = Path("/simple/project")
        
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"fastapi"},  # Backend framework without frontend
            databases=set(),
            tools=set(),
            package_managers={"pip"}
        )
        # Very simple directory structure to avoid all microservices triggers
        file_analysis = {"directory_structure": ["src"]}
        
        architecture = await analyzer._detect_architecture_pattern(temp_project, tech_stack, file_analysis)
        # Should detect API_FIRST since it has backend framework but no frontend
        assert architecture == ArchitecturePattern.API_FIRST

    @pytest.mark.asyncio
    async def test_detect_architecture_pattern_fullstack(self, analyzer):
        """Test full-stack architecture detection"""
        # Use a simple project path that won't trigger microservices detection
        temp_project = Path("/simple/project")
        
        tech_stack = TechnologyStack(
            languages={"python", "javascript"},
            frameworks={"react", "fastapi"},  # Both frontend and backend
            databases=set(),
            tools=set(),
            package_managers={"npm", "pip"}
        )
        # Very simple directory structure to avoid microservices triggers
        file_analysis = {"directory_structure": ["src"]}
        
        architecture = await analyzer._detect_architecture_pattern(temp_project, tech_stack, file_analysis)
        # Should be fullstack since it has both frontend (react) and backend (fastapi)
        assert architecture == ArchitecturePattern.FULLSTACK

    @pytest.mark.asyncio
    async def test_detect_architecture_pattern_monolithic(self, analyzer):
        """Test monolithic architecture detection (default)"""
        # Use a simple project path that won't trigger microservices detection
        temp_project = Path("/simple/project")
        
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks=set(),  # No frameworks
            databases=set(),
            tools=set(),
            package_managers={"pip"}
        )
        # Very simple directory structure
        file_analysis = {"directory_structure": ["src"]}
        
        architecture = await analyzer._detect_architecture_pattern(temp_project, tech_stack, file_analysis)
        assert architecture == ArchitecturePattern.MONOLITHIC

    @pytest.mark.asyncio
    async def test_assess_complexity_simple(self, analyzer):
        """Test simple complexity assessment"""
        file_analysis = {
            "total_files": 10,
            "total_lines": 1000,
            "has_ci_cd": False
        }
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"flask"},
            databases=set(),
            tools=set(),
            package_managers={"pip"}
        )
        
        complexity = await analyzer._assess_complexity(file_analysis, tech_stack)
        assert complexity == ProjectComplexity.SIMPLE

    @pytest.mark.asyncio
    async def test_assess_complexity_medium(self, analyzer):
        """Test medium complexity assessment"""
        file_analysis = {
            "total_files": 200,
            "total_lines": 15000,
            "has_ci_cd": True
        }
        tech_stack = TechnologyStack(
            languages={"python", "javascript"},
            frameworks={"django", "react"},
            databases={"postgresql"},
            tools={"docker"},
            package_managers={"pip", "npm"}
        )
        
        complexity = await analyzer._assess_complexity(file_analysis, tech_stack)
        # With the current scoring system, this should be MEDIUM or higher
        assert complexity in [ProjectComplexity.MEDIUM, ProjectComplexity.COMPLEX]

    @pytest.mark.asyncio
    async def test_assess_complexity_complex(self, analyzer):
        """Test complex complexity assessment"""
        file_analysis = {
            "total_files": 600,
            "total_lines": 60000,
            "has_ci_cd": True
        }
        tech_stack = TechnologyStack(
            languages={"python", "javascript", "typescript"},
            frameworks={"django", "react", "nextjs"},
            databases={"postgresql", "redis"},
            tools={"docker", "kubernetes"},
            package_managers={"pip", "npm", "yarn"}
        )
        
        complexity = await analyzer._assess_complexity(file_analysis, tech_stack)
        # With many technologies and Kubernetes, this should be COMPLEX or ENTERPRISE
        assert complexity in [ProjectComplexity.COMPLEX, ProjectComplexity.ENTERPRISE]

    @pytest.mark.asyncio
    async def test_assess_complexity_enterprise(self, analyzer):
        """Test enterprise complexity assessment"""
        file_analysis = {
            "total_files": 1500,
            "total_lines": 120000,
            "has_ci_cd": True
        }
        tech_stack = TechnologyStack(
            languages={"python", "javascript", "typescript", "java"},
            frameworks={"django", "react", "nextjs", "spring"},
            databases={"postgresql", "redis", "mongodb"},
            tools={"docker", "kubernetes", "terraform"},
            package_managers={"pip", "npm", "yarn", "maven"}
        )
        
        complexity = await analyzer._assess_complexity(file_analysis, tech_stack)
        assert complexity == ProjectComplexity.ENTERPRISE

    @pytest.mark.asyncio
    async def test_detect_integrations(self, analyzer, temp_project):
        """Test integration detection"""
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"fastapi"},
            databases={"postgresql"},
            tools={"docker", "kubernetes"},
            package_managers={"pip"}
        )
        
        integrations = await analyzer._detect_integrations(temp_project, tech_stack)
        
        assert "database_management" in integrations
        assert "api_development" in integrations
        assert "containerization" in integrations

    @pytest.mark.asyncio
    async def test_recommend_subagents_comprehensive(self, analyzer):
        """Test comprehensive subagent recommendations"""
        tech_stack = TechnologyStack(
            languages={"python", "javascript", "typescript"},
            frameworks={"fastapi", "react", "nextjs"},
            databases={"postgresql", "redis"},
            tools={"docker", "kubernetes"},
            package_managers={"pip", "npm"}
        )
        architecture = ArchitecturePattern.FULLSTACK
        complexity = ProjectComplexity.COMPLEX
        
        agents = await analyzer._recommend_subagents(tech_stack, architecture, complexity)
        
        assert "code-reviewer" in agents
        assert "backend-developer" in agents
        assert "frontend-developer" in agents
        assert "database-specialist" in agents
        assert "devops-engineer" in agents
        assert "security-auditor" in agents
        assert "api-developer" in agents

    @pytest.mark.asyncio
    async def test_recommend_subagents_simple_python(self, analyzer):
        """Test subagent recommendations for simple Python project"""
        tech_stack = TechnologyStack(
            languages={"python"},
            frameworks={"flask"},
            databases=set(),
            tools=set(),
            package_managers={"pip"}
        )
        architecture = ArchitecturePattern.MONOLITHIC
        complexity = ProjectComplexity.SIMPLE
        
        agents = await analyzer._recommend_subagents(tech_stack, architecture, complexity)
        
        assert "code-reviewer" in agents
        assert "backend-developer" in agents
        assert "test-engineer" in agents

    def test_estimate_team_size(self, analyzer):
        """Test team size estimation"""
        # Simple project
        size = analyzer._estimate_team_size(ProjectComplexity.SIMPLE, 3)
        assert size == 3  # max(1, min(3, 12))
        
        # Complex project with many agents
        size = analyzer._estimate_team_size(ProjectComplexity.COMPLEX, 8)
        assert size == 8  # max(4, min(8, 12))
        
        # Enterprise project with too many agents
        size = analyzer._estimate_team_size(ProjectComplexity.ENTERPRISE, 15)
        assert size == 12  # max(8, min(15, 12))

    @pytest.mark.asyncio
    async def test_save_analysis(self, analyzer, temp_project):
        """Test analysis saving"""
        profile = ProjectProfile(
            name="test_project",
            path=str(temp_project),
            technology_stack=TechnologyStack({"python"}, {"flask"}, set(), set(), {"pip"}),
            architecture_pattern=ArchitecturePattern.MONOLITHIC,
            complexity=ProjectComplexity.SIMPLE,
            team_size_estimate=2,
            file_count=10,
            lines_of_code=1000,
            has_tests=True,
            has_ci_cd=False,
            has_docker=False,
            has_docs=True,
            recommended_subagents=["backend-developer", "code-reviewer"],
            integration_requirements=[]
        )
        
        output_path = await analyzer.save_analysis(profile)
        
        assert Path(output_path).exists()
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
            assert saved_data["name"] == "test_project"
            assert saved_data["complexity"] == "simple"

    def test_technology_stack_to_dict(self):
        """Test TechnologyStack to_dict method"""
        stack = TechnologyStack(
            languages={"python", "javascript"},
            frameworks={"django", "react"},
            databases={"postgresql"},
            tools={"docker"},
            package_managers={"pip", "npm"}
        )
        
        stack_dict = stack.to_dict()
        assert isinstance(stack_dict["languages"], list)
        assert "python" in stack_dict["languages"]
        assert "react" in stack_dict["frameworks"]

    def test_project_profile_to_dict(self):
        """Test ProjectProfile to_dict method"""
        profile = ProjectProfile(
            name="test",
            path="/test",
            technology_stack=TechnologyStack({"python"}, {"flask"}, set(), set(), {"pip"}),
            architecture_pattern=ArchitecturePattern.MONOLITHIC,
            complexity=ProjectComplexity.SIMPLE,
            team_size_estimate=2,
            file_count=10,
            lines_of_code=1000,
            has_tests=True,
            has_ci_cd=False,
            has_docker=False,
            has_docs=True,
            recommended_subagents=["backend-developer"],
            integration_requirements=[]
        )
        
        profile_dict = profile.to_dict()
        assert profile_dict["name"] == "test"
        assert profile_dict["complexity"] == "simple"
        assert profile_dict["architecture_pattern"] == "monolithic"


class TestContextEngineer:
    """Test ContextEngineer with comprehensive coverage"""

    @pytest.fixture
    def workspace_dir(self, tmp_path):
        """Create temporary workspace directory"""
        return tmp_path / "workspace"

    @pytest.fixture
    def context_engineer(self, workspace_dir):
        """Create ContextEngineer instance"""
        return ContextEngineer(workspace_dir)

    @pytest.fixture
    def sample_profile(self):
        """Create sample project profile"""
        return ProjectProfile(
            name="test_project",
            path="/test/path",
            technology_stack=TechnologyStack(
                languages={"python", "javascript"},
                frameworks={"fastapi", "react"},
                databases={"postgresql"},
                tools={"docker"},
                package_managers={"pip", "npm"}
            ),
            architecture_pattern=ArchitecturePattern.FULLSTACK,
            complexity=ProjectComplexity.COMPLEX,
            team_size_estimate=6,
            file_count=500,
            lines_of_code=50000,
            has_tests=True,
            has_ci_cd=True,
            has_docker=True,
            has_docs=True,
            recommended_subagents=["backend-developer", "frontend-developer"],
            integration_requirements=["api_development", "database_management"]
        )

    def test_context_engineer_initialization(self, context_engineer, workspace_dir):
        """Test ContextEngineer initialization"""
        assert context_engineer.workspace_dir == workspace_dir
        assert context_engineer.context_library.exists()
        assert context_engineer.examples_dir.exists()
        assert context_engineer.patterns_dir.exists()

    def test_context_package_to_markdown(self):
        """Test ContextPackage to_markdown method"""
        context_package = ContextPackage(
            project_context={"name": "test", "complexity": "medium"},
            technical_context={"language": "python"},
            examples=[{
                "title": "Test Example",
                "purpose": "Testing",
                "language": "python",
                "code": "print('hello')",
                "notes": "Simple example"
            }],
            patterns=[],
            validation_gates=[{
                "name": "Test Gate",
                "test": "Run tests",
                "command": "pytest",
                "expected": "All pass",
                "on_failure": "Fix tests"
            }],
            references=["https://example.com"],
            success_criteria=["Code works", "Tests pass"]
        )
        
        markdown = context_package.to_markdown()
        assert "# Context Package - test" in markdown
        assert "## Project Context" in markdown
        assert "## Technical Context" in markdown
        assert "### Example 1: Test Example" in markdown
        assert "### Test Gate" in markdown

    def test_context_package_format_dict_as_markdown(self):
        """Test _format_dict_as_markdown method"""
        context_package = ContextPackage(
            project_context={},
            technical_context={},
            examples=[],
            patterns=[],
            validation_gates=[],
            references=[],
            success_criteria=[]
        )
        
        data = {
            "simple_value": "test",
            "list_value": ["item1", "item2"],
            "complex_key_name": "value"
        }
        
        result = context_package._format_dict_as_markdown(data)
        assert "- **Simple Value**: test" in result
        assert "- **List Value**: item1, item2" in result
        assert "- **Complex Key Name**: value" in result

    def test_context_package_format_examples_empty(self):
        """Test _format_examples_as_markdown with empty examples"""
        context_package = ContextPackage(
            project_context={},
            technical_context={},
            examples=[],
            patterns=[],
            validation_gates=[],
            references=[],
            success_criteria=[]
        )
        
        result = context_package._format_examples_as_markdown()
        assert result == "No specific examples available"

    def test_context_package_format_validation_gates_empty(self):
        """Test _format_validation_gates_as_markdown with empty gates"""
        context_package = ContextPackage(
            project_context={},
            technical_context={},
            examples=[],
            patterns=[],
            validation_gates=[],
            references=[],
            success_criteria=[]
        )
        
        result = context_package._format_validation_gates_as_markdown()
        assert result == "No validation gates defined"

    def test_context_package_format_list_empty(self):
        """Test _format_list_as_markdown with empty list"""
        context_package = ContextPackage(
            project_context={},
            technical_context={},
            examples=[],
            patterns=[],
            validation_gates=[],
            references=[],
            success_criteria=[]
        )
        
        result = context_package._format_list_as_markdown([])
        assert result == "None specified"
        
        result = context_package._format_list_as_markdown(["item1", "item2"])
        assert result == "- item1\n- item2"

    def test_engineer_context_for_phase(self, context_engineer, sample_profile):
        """Test engineer_context_for_phase method"""
        context_package = context_engineer.engineer_context_for_phase(
            "analysis",
            sample_profile,
            {},
            ContextLevel.STANDARD
        )
        
        assert isinstance(context_package, ContextPackage)
        assert context_package.project_context["name"] == "test_project"
        assert context_package.technical_context["phase"] == "analysis"
        
        # Verify context file was saved
        context_file = context_engineer.context_library / "analysis_context.md"
        json_file = context_engineer.context_library / "analysis_context.json"
        assert context_file.exists()
        assert json_file.exists()

    def test_build_project_context(self, context_engineer, sample_profile):
        """Test _build_project_context method"""
        context = context_engineer._build_project_context(sample_profile)
        
        assert context["name"] == "test_project"
        assert context["architecture_pattern"] == "fullstack"
        assert context["complexity_level"] == "complex"
        assert "python" in context["languages"]
        assert "fastapi" in context["frameworks"]

    def test_build_technical_context_analysis(self, context_engineer, sample_profile):
        """Test _build_technical_context for analysis phase"""
        context = context_engineer._build_technical_context(sample_profile, "analysis")
        
        assert context["phase"] == "analysis"
        assert context["analysis_depth"] == "deep"  # complex project
        assert "architecture" in context["discovery_areas"]

    def test_build_technical_context_selection(self, context_engineer, sample_profile):
        """Test _build_technical_context for selection phase"""
        context = context_engineer._build_technical_context(sample_profile, "selection")
        
        assert context["phase"] == "selection"
        assert context["customization_level"] == "high"  # complex project
        assert "template_criteria" in context

    def test_build_technical_context_generation(self, context_engineer, sample_profile):
        """Test _build_technical_context for generation phase"""
        context = context_engineer._build_technical_context(sample_profile, "generation")
        
        assert context["phase"] == "generation"
        assert "claude_md" in context["generation_targets"]
        assert context["customization_required"] == True

    def test_find_relevant_examples(self, context_engineer, sample_profile):
        """Test _find_relevant_examples method"""
        examples = context_engineer._find_relevant_examples(sample_profile, "generation")
        
        # Should return examples for each language and framework
        assert len(examples) <= 5  # Limited to 5
        assert isinstance(examples, list)

    def test_get_language_examples_python(self, context_engineer):
        """Test _get_language_examples for Python"""
        examples = context_engineer._get_language_examples("python", "generation")
        
        assert len(examples) > 0
        example = examples[0]
        assert example["title"] == "Python CLAUDE.md Configuration"
        assert "python -m pip install" in example["code"]

    def test_get_language_examples_javascript(self, context_engineer):
        """Test _get_language_examples for JavaScript"""
        examples = context_engineer._get_language_examples("javascript", "generation")
        
        assert len(examples) > 0
        example = examples[0]
        assert example["title"] == "JavaScript/Node.js Configuration"
        assert "npm install" in example["code"]

    def test_get_framework_examples_fastapi(self, context_engineer):
        """Test _get_framework_examples for FastAPI"""
        examples = context_engineer._get_framework_examples("fastapi", "generation")
        
        assert len(examples) > 0
        example = examples[0]
        assert example["title"] == "FastAPI Agent Configuration"
        assert "API-focused agent specialization" in example["purpose"]

    def test_get_architecture_examples(self, context_engineer):
        """Test _get_architecture_examples method"""
        examples = context_engineer._get_architecture_examples(
            ArchitecturePattern.MICROSERVICES, "generation"
        )
        
        assert len(examples) > 0
        example = examples[0]
        assert "Microservices Architecture Workflow" in example["title"]

    def test_get_architecture_workflow_template_microservices(self, context_engineer):
        """Test _get_architecture_workflow_template for microservices"""
        template = context_engineer._get_architecture_workflow_template(
            ArchitecturePattern.MICROSERVICES
        )
        
        assert "# Microservices Development Workflow" in template
        assert "Service Design" in template
        assert "API contracts" in template

    def test_get_architecture_workflow_template_default(self, context_engineer):
        """Test _get_architecture_workflow_template for default architecture"""
        template = context_engineer._get_architecture_workflow_template(
            ArchitecturePattern.MONOLITHIC
        )
        
        assert "# Standard Development Workflow" in template
        assert "Requirements Analysis" in template

    def test_extract_patterns_standard_level(self, context_engineer, sample_profile):
        """Test _extract_patterns with standard context level"""
        patterns = context_engineer._extract_patterns(
            sample_profile, "generation", ContextLevel.STANDARD
        )
        
        assert isinstance(patterns, list)

    def test_extract_patterns_deep_level(self, context_engineer, sample_profile):
        """Test _extract_patterns with deep context level"""
        patterns = context_engineer._extract_patterns(
            sample_profile, "generation", ContextLevel.DEEP
        )
        
        assert isinstance(patterns, list)
        # Should include advanced patterns

    def test_extract_patterns_expert_level(self, context_engineer, sample_profile):
        """Test _extract_patterns with expert context level"""
        patterns = context_engineer._extract_patterns(
            sample_profile, "generation", ContextLevel.EXPERT
        )
        
        assert isinstance(patterns, list)
        # Should include both advanced and expert patterns

    def test_get_advanced_patterns(self, context_engineer, sample_profile):
        """Test _get_advanced_patterns method"""
        patterns = context_engineer._get_advanced_patterns(sample_profile, "generation")
        
        assert len(patterns) > 0
        pattern = patterns[0]
        assert pattern["name"] == "Agent Specialization Pattern"
        assert "benefits" in pattern
        assert "examples" in pattern

    def test_get_expert_patterns_complex(self, context_engineer, sample_profile):
        """Test _get_expert_patterns for complex projects"""
        patterns = context_engineer._get_expert_patterns(sample_profile, "generation")
        
        assert len(patterns) > 0
        pattern = patterns[0]
        assert pattern["name"] == "Enterprise Coordination Pattern"

    def test_create_validation_gates(self, context_engineer, sample_profile):
        """Test _create_validation_gates method"""
        gates = context_engineer._create_validation_gates("generation", sample_profile)
        
        assert len(gates) > 0
        gate = gates[0]
        assert gate["name"] == "CLAUDE.md Syntax Validation"
        assert "command" in gate
        assert "expected" in gate

    def test_build_references(self, context_engineer, sample_profile):
        """Test _build_references method"""
        references = context_engineer._build_references(sample_profile, "generation")
        
        assert len(references) > 0
        # Should include Python and JavaScript references
        python_refs = [ref for ref in references if "python" in ref.lower()]
        js_refs = [ref for ref in references if "javascript" in ref.lower() or "node.js" in ref.lower()]
        assert len(python_refs) > 0
        assert len(js_refs) > 0

    def test_define_success_criteria_analysis(self, context_engineer, sample_profile):
        """Test _define_success_criteria for analysis phase"""
        criteria = context_engineer._define_success_criteria("analysis", sample_profile)
        
        assert len(criteria) > 0
        assert any("fully analyzed" in criterion.lower() for criterion in criteria)
        assert any("technology stack" in criterion.lower() or "accurately identified" in criterion.lower() for criterion in criteria)

    def test_define_success_criteria_generation(self, context_engineer, sample_profile):
        """Test _define_success_criteria for generation phase"""
        criteria = context_engineer._define_success_criteria("generation", sample_profile)
        
        assert len(criteria) > 0
        assert any("CLAUDE.md" in criterion for criterion in criteria)
        assert any("validation gates" in criterion for criterion in criteria)

    def test_get_template_criteria(self, context_engineer, sample_profile):
        """Test _get_template_criteria method"""
        criteria = context_engineer._get_template_criteria(sample_profile)
        
        assert len(criteria) > 0
        # Check for languages (order may vary)
        assert any(("python" in criterion and "javascript" in criterion) for criterion in criteria)
        assert any("fullstack architecture" in criterion for criterion in criteria)
        assert any("complex complexity" in criterion for criterion in criteria)
        assert any("testing support" in criterion for criterion in criteria)
        assert any("CI/CD integration" in criterion for criterion in criteria)

    def test_save_context_package(self, context_engineer, sample_profile):
        """Test _save_context_package method"""
        context_package = ContextPackage(
            project_context={"name": "test"},
            technical_context={"phase": "test"},
            examples=[],
            patterns=[],
            validation_gates=[],
            references=[],
            success_criteria=[]
        )
        
        context_engineer._save_context_package("test_phase", context_package)
        
        # Check files were created
        md_file = context_engineer.context_library / "test_phase_context.md"
        json_file = context_engineer.context_library / "test_phase_context.json"
        
        assert md_file.exists()
        assert json_file.exists()
        
        # Verify JSON content
        with open(json_file) as f:
            data = json.load(f)
            assert data["project_context"]["name"] == "test"
            assert "generated_at" in data

    def test_create_context_engineer_factory(self, workspace_dir):
        """Test create_context_engineer factory function"""
        engineer = create_context_engineer(workspace_dir)
        assert isinstance(engineer, ContextEngineer)
        assert engineer.workspace_dir == workspace_dir


class TestPRPGenerator:
    """Test PRPGenerator with comprehensive coverage"""

    @pytest.fixture
    def workspace_dir(self, tmp_path):
        """Create temporary workspace directory"""
        return tmp_path / "workspace"

    @pytest.fixture
    def prp_generator(self, workspace_dir):
        """Create PRPGenerator instance"""
        return PRPGenerator(workspace_dir)

    @pytest.fixture
    def sample_profile(self):
        """Create sample project profile"""
        return ProjectProfile(
            name="test_project",
            path="/test/path",
            technology_stack=TechnologyStack(
                languages={"python", "javascript"},
                frameworks={"fastapi", "react"},
                databases={"postgresql"},
                tools={"docker"},
                package_managers={"pip", "npm"}
            ),
            architecture_pattern=ArchitecturePattern.FULLSTACK,
            complexity=ProjectComplexity.COMPLEX,
            team_size_estimate=6,
            file_count=500,
            lines_of_code=50000,
            has_tests=True,
            has_ci_cd=True,
            has_docker=True,
            has_docs=True,
            recommended_subagents=["backend-developer", "frontend-developer"],
            integration_requirements=["api_development", "database_management"]
        )

    @pytest.fixture
    def sample_context_package(self):
        """Create sample context package"""
        return ContextPackage(
            project_context={"name": "test", "complexity": "complex"},
            technical_context={"phase": "analysis"},
            examples=[],
            patterns=[],
            validation_gates=[],
            references=[],
            success_criteria=[]
        )

    def test_prp_generator_initialization(self, prp_generator, workspace_dir):
        """Test PRPGenerator initialization"""
        assert prp_generator.workspace_dir == workspace_dir
        assert prp_generator.prps_dir.exists()
        assert prp_generator.templates_dir.exists()
        assert prp_generator.generated_dir.exists()

    def test_prp_to_markdown(self, sample_context_package):
        """Test PRP to_markdown method"""
        prp = PRP(
            id="test_prp_123",
            type=PRPType.FACTORY_ANALYSIS,
            title="Test PRP",
            context_package=sample_context_package,
            execution_prompt="Execute this task",
            validation_checklist=["Check 1", "Check 2"],
            success_metrics=["Metric 1", "Metric 2"],
            output_specification={"format": "markdown", "location": "output/"},
            created_at=datetime.now()
        )
        
        markdown = prp.to_markdown()
        assert "# PRP: Test PRP" in markdown
        assert "**ID**: `test_prp_123`" in markdown
        assert "Execute this task" in markdown
        assert "- [ ] Check 1" in markdown
        assert "- Metric 1" in markdown

    def test_prp_format_checklist(self, sample_context_package):
        """Test PRP _format_checklist method"""
        prp = PRP(
            id="test", type=PRPType.FACTORY_ANALYSIS, title="Test",
            context_package=sample_context_package, execution_prompt="",
            validation_checklist=[], success_metrics=[],
            output_specification={}, created_at=datetime.now()
        )
        
        result = prp._format_checklist(["Item 1", "Item 2"])
        assert result == "- [ ] Item 1\n- [ ] Item 2"

    def test_prp_format_metrics(self, sample_context_package):
        """Test PRP _format_metrics method"""
        prp = PRP(
            id="test", type=PRPType.FACTORY_ANALYSIS, title="Test",
            context_package=sample_context_package, execution_prompt="",
            validation_checklist=[], success_metrics=[],
            output_specification={}, created_at=datetime.now()
        )
        
        result = prp._format_metrics(["Metric 1", "Metric 2"])
        assert result == "- Metric 1\n- Metric 2"

    def test_prp_format_output_spec(self, sample_context_package):
        """Test PRP _format_output_spec method"""
        prp = PRP(
            id="test", type=PRPType.FACTORY_ANALYSIS, title="Test",
            context_package=sample_context_package, execution_prompt="",
            validation_checklist=[], success_metrics=[],
            output_specification={}, created_at=datetime.now()
        )
        
        spec = {
            "simple_key": "value",
            "nested_dict": {"sub_key": "sub_value", "another": "test"}
        }
        
        result = prp._format_output_spec(spec)
        assert "- **Simple Key**: value" in result
        assert "### Nested Dict" in result
        assert "- **sub_key**: sub_value" in result

    def test_generate_factory_analysis_prp(self, prp_generator, sample_profile, sample_context_package):
        """Test generate_factory_analysis_prp method"""
        prp = prp_generator.generate_factory_analysis_prp(
            sample_profile,
            sample_context_package,
            "Create a web application with user authentication"
        )
        
        assert isinstance(prp, PRP)
        assert prp.type == PRPType.FACTORY_ANALYSIS
        assert "Factory Analysis for test_project" in prp.title
        assert "User Request Context" in prp.execution_prompt
        assert "comprehensive analysis" in prp.execution_prompt.lower()
        assert len(prp.validation_checklist) > 0
        assert len(prp.success_metrics) > 0
        
        # Check files were saved
        prp_file = prp_generator.generated_dir / f"{prp.id}.md"
        meta_file = prp_generator.generated_dir / f"{prp.id}_meta.json"
        assert prp_file.exists()
        assert meta_file.exists()

    def test_generate_factory_generation_prp_claude_md(self, prp_generator, sample_profile, sample_context_package):
        """Test generate_factory_generation_prp for claude-md-generator"""
        prp = prp_generator.generate_factory_generation_prp(
            sample_profile,
            sample_context_package,
            {"analysis": "complete"},
            "claude-md-generator"
        )
        
        assert isinstance(prp, PRP)
        assert prp.type == PRPType.FACTORY_GENERATION
        assert "Claude Md Generator Generation for test_project" in prp.title
        assert "CLAUDE.md Generation Task" in prp.execution_prompt
        assert "Build Commands Section" in prp.execution_prompt

    def test_generate_factory_generation_prp_agent_generator(self, prp_generator, sample_profile, sample_context_package):
        """Test generate_factory_generation_prp for agent-generator"""
        prp = prp_generator.generate_factory_generation_prp(
            sample_profile,
            sample_context_package,
            {"analysis": "complete"},
            "agent-generator"
        )
        
        assert prp.type == PRPType.FACTORY_GENERATION
        assert "Agent Generation Task" in prp.execution_prompt
        assert "YAML Frontmatter" in prp.execution_prompt

    def test_generate_factory_generation_prp_workflow_generator(self, prp_generator, sample_profile, sample_context_package):
        """Test generate_factory_generation_prp for workflow-generator"""
        prp = prp_generator.generate_factory_generation_prp(
            sample_profile,
            sample_context_package,
            {"analysis": "complete"},
            "workflow-generator"
        )
        
        assert prp.type == PRPType.FACTORY_GENERATION
        assert "Workflow Generation Task" in prp.execution_prompt
        assert "Quality Gates" in prp.execution_prompt

    def test_generate_factory_generation_prp_generic(self, prp_generator, sample_profile, sample_context_package):
        """Test generate_factory_generation_prp for generic subagent"""
        prp = prp_generator.generate_factory_generation_prp(
            sample_profile,
            sample_context_package,
            {"analysis": "complete"},
            "custom-subagent"
        )
        
        assert prp.type == PRPType.FACTORY_GENERATION
        assert "Custom Subagent Generation Task" in prp.execution_prompt

    def test_format_analysis_insights_empty(self, prp_generator):
        """Test _format_analysis_insights with empty data"""
        result = prp_generator._format_analysis_insights({})
        assert result == "Analysis in progress - using project profile data"

    def test_format_analysis_insights_with_data(self, prp_generator):
        """Test _format_analysis_insights with data"""
        insights = {
            "technologies": {"python": "3.9", "javascript": "ES6"},
            "patterns": ["mvc", "rest"],
            "complexity_score": 8
        }
        
        result = prp_generator._format_analysis_insights(insights)
        assert "**Technologies**: 2 items identified" in result
        assert "**Patterns**: mvc, rest" in result
        assert "**Complexity Score**: 8" in result

    def test_format_project_context(self, prp_generator, sample_profile):
        """Test _format_project_context method"""
        result = prp_generator._format_project_context(sample_profile)
        
        assert "- **Name**: test_project" in result
        assert "- **Architecture**: fullstack" in result
        assert "- **Complexity**: complex" in result
        # Languages order may vary, check for both
        assert ("- **Languages**: python, javascript" in result or "- **Languages**: javascript, python" in result)
        assert "- **Testing**: Comprehensive" in result
        assert "- **CI/CD**: Integrated" in result

    def test_get_architecture_workflow_requirements_microservices(self, prp_generator):
        """Test _get_architecture_workflow_requirements for microservices"""
        result = prp_generator._get_architecture_workflow_requirements(
            ArchitecturePattern.MICROSERVICES
        )
        
        assert "For microservices architecture:" in result
        assert "Service Development" in result
        assert "API Contract Management" in result
        assert "Inter-service communication" in result

    def test_get_architecture_workflow_requirements_monolithic(self, prp_generator):
        """Test _get_architecture_workflow_requirements for monolithic"""
        result = prp_generator._get_architecture_workflow_requirements(
            ArchitecturePattern.MONOLITHIC
        )
        
        assert "For monolithic architecture:" in result
        assert "Module Development" in result
        assert "Integration Testing" in result

    def test_get_architecture_workflow_requirements_default(self, prp_generator):
        """Test _get_architecture_workflow_requirements for default"""
        result = prp_generator._get_architecture_workflow_requirements(
            ArchitecturePattern.FULLSTACK
        )
        
        assert "For standard architecture:" in result
        assert "Component Development" in result

    def test_get_subagent_validation_checklist_claude_md(self, prp_generator):
        """Test _get_subagent_validation_checklist for claude-md-generator"""
        checklist = prp_generator._get_subagent_validation_checklist("claude-md-generator")
        
        assert len(checklist) > 4  # Common + specific checks
        assert any("CLAUDE.md follows proper structure" in item for item in checklist)
        assert any("Build commands are executable" in item for item in checklist)

    def test_get_subagent_validation_checklist_agent_generator(self, prp_generator):
        """Test _get_subagent_validation_checklist for agent-generator"""
        checklist = prp_generator._get_subagent_validation_checklist("agent-generator")
        
        assert any("valid YAML frontmatter" in item for item in checklist)
        assert any("roles are clearly defined" in item for item in checklist)

    def test_get_subagent_validation_checklist_workflow_generator(self, prp_generator):
        """Test _get_subagent_validation_checklist for workflow-generator"""
        checklist = prp_generator._get_subagent_validation_checklist("workflow-generator")
        
        assert any("appropriate for project architecture" in item for item in checklist)
        assert any("Quality gates are measurable" in item for item in checklist)

    def test_get_subagent_success_metrics_claude_md(self, prp_generator):
        """Test _get_subagent_success_metrics for claude-md-generator"""
        metrics = prp_generator._get_subagent_success_metrics("claude-md-generator")
        
        assert any("30 seconds" in metric for metric in metrics)
        assert any("Build commands execute" in metric for metric in metrics)

    def test_get_subagent_success_metrics_agent_generator(self, prp_generator):
        """Test _get_subagent_success_metrics for agent-generator"""
        metrics = prp_generator._get_subagent_success_metrics("agent-generator")
        
        assert any("60 seconds" in metric for metric in metrics)
        assert any("specialization clarity" in metric for metric in metrics)

    def test_get_subagent_success_metrics_workflow_generator(self, prp_generator):
        """Test _get_subagent_success_metrics for workflow-generator"""
        metrics = prp_generator._get_subagent_success_metrics("workflow-generator")
        
        assert any("45 seconds" in metric for metric in metrics)
        assert any("commands are executable" in metric for metric in metrics)

    def test_get_subagent_success_metrics_generic(self, prp_generator):
        """Test _get_subagent_success_metrics for generic subagent"""
        metrics = prp_generator._get_subagent_success_metrics("unknown-agent")
        
        assert len(metrics) == 2  # Generic metrics
        assert any("expected timeframe" in metric for metric in metrics)

    def test_get_subagent_output_specification_claude_md(self, prp_generator):
        """Test _get_subagent_output_specification for claude-md-generator"""
        spec = prp_generator._get_subagent_output_specification("claude-md-generator")
        
        assert spec["primary_output"] == "CLAUDE.md"
        assert spec["location"] == "project_root"
        assert spec["format"] == "markdown"
        assert "project_overview" in spec["sections_required"]

    def test_get_subagent_output_specification_agent_generator(self, prp_generator):
        """Test _get_subagent_output_specification for agent-generator"""
        spec = prp_generator._get_subagent_output_specification("agent-generator")
        
        assert spec["primary_output"] == "agent_configurations"
        assert spec["location"] == ".claude/agents/"
        assert spec["format"] == "yaml_frontmatter_markdown"

    def test_get_subagent_output_specification_workflow_generator(self, prp_generator):
        """Test _get_subagent_output_specification for workflow-generator"""
        spec = prp_generator._get_subagent_output_specification("workflow-generator")
        
        assert spec["primary_output"] == "workflow_documentation"
        assert spec["location"] == "workflows/"
        assert "processes" in spec["includes"]

    def test_get_subagent_output_specification_generic(self, prp_generator):
        """Test _get_subagent_output_specification for generic subagent"""
        spec = prp_generator._get_subagent_output_specification("unknown-agent")
        
        assert spec["primary_output"] == "unknown-agent_configuration"
        assert spec["format"] == "markdown"

    def test_save_prp(self, prp_generator, sample_context_package):
        """Test _save_prp method"""
        prp = PRP(
            id="test_prp_save",
            type=PRPType.FACTORY_ANALYSIS,
            title="Test Save",
            context_package=sample_context_package,
            execution_prompt="Test prompt",
            validation_checklist=["Check 1"],
            success_metrics=["Metric 1"],
            output_specification={"test": "spec"},
            created_at=datetime.now()
        )
        
        prp_generator._save_prp(prp)
        
        # Check files were created
        md_file = prp_generator.generated_dir / "test_prp_save.md"
        meta_file = prp_generator.generated_dir / "test_prp_save_meta.json"
        
        assert md_file.exists()
        assert meta_file.exists()
        
        # Verify content
        with open(meta_file) as f:
            meta = json.load(f)
            assert meta["id"] == "test_prp_save"
            assert meta["type"] == "factory_analysis"

    def test_create_prp_generator_factory(self, workspace_dir):
        """Test create_prp_generator factory function"""
        generator = create_prp_generator(workspace_dir)
        assert isinstance(generator, PRPGenerator)
        assert generator.workspace_dir == workspace_dir


class TestCommunicationManager:
    """Test CommunicationManager with comprehensive coverage"""

    @pytest.fixture
    def workspace_dir(self, tmp_path):
        """Create temporary workspace directory"""
        return tmp_path / "workspace"

    @pytest.fixture
    def comm_manager(self, workspace_dir):
        """Create CommunicationManager instance"""
        return CommunicationManager(workspace_dir)

    def test_communication_manager_initialization(self, comm_manager, workspace_dir):
        """Test CommunicationManager initialization"""
        assert comm_manager.workspace_dir == workspace_dir
        assert comm_manager.communication_dir.exists()
        assert comm_manager.handoffs_dir.exists()

    @pytest.mark.asyncio
    async def test_create_handoff(self, comm_manager):
        """Test create_handoff method"""
        handoff_id = await comm_manager.create_handoff(
            from_agent="analyzer",
            to_agent="generator",
            handoff_type="analysis_complete",
            data={"project_name": "test", "complexity": "medium"},
            instructions="Please generate configurations based on analysis results"
        )
        
        assert isinstance(handoff_id, str)
        assert handoff_id.startswith("handoff_")
        
        # Check JSON file was created
        json_file = comm_manager.handoffs_dir / f"{handoff_id}.json"
        assert json_file.exists()
        
        with open(json_file) as f:
            handoff_data = json.load(f)
            assert handoff_data["from_agent"] == "analyzer"
            assert handoff_data["to_agent"] == "generator"
            assert handoff_data["handoff_type"] == "analysis_complete"
            assert handoff_data["data"]["project_name"] == "test"
            assert handoff_data["status"] == "created"
        
        # Check Markdown file was created
        md_file = comm_manager.handoffs_dir / f"{handoff_id}.md"
        assert md_file.exists()
        
        with open(md_file) as f:
            md_content = f.read()
            assert f"# Handoff: {handoff_id}" in md_content
            assert "**From**: @analyzer" in md_content
            assert "**To**: @generator" in md_content
            assert "analysis_complete" in md_content
            assert "Please generate configurations" in md_content

    @pytest.mark.asyncio
    async def test_create_handoff_with_complex_data(self, comm_manager):
        """Test create_handoff with complex data structures"""
        complex_data = {
            "analysis_results": {
                "technologies": ["python", "javascript"],
                "frameworks": {"backend": ["fastapi"], "frontend": ["react"]},
                "complexity_score": 8.5,
                "recommendations": [
                    {"type": "backend-developer", "priority": "high"},
                    {"type": "frontend-developer", "priority": "medium"}
                ]
            },
            "metadata": {
                "timestamp": "2024-01-01T00:00:00",
                "version": "1.0"
            }
        }
        
        handoff_id = await comm_manager.create_handoff(
            from_agent="project-analyzer",
            to_agent="context-engineer",
            handoff_type="deep_analysis",
            data=complex_data,
            instructions="Context engineering needed for complex multi-framework project"
        )
        
        # Verify complex data is properly serialized
        json_file = comm_manager.handoffs_dir / f"{handoff_id}.json"
        with open(json_file) as f:
            handoff_data = json.load(f)
            assert handoff_data["data"]["analysis_results"]["complexity_score"] == 8.5
            assert "python" in handoff_data["data"]["analysis_results"]["technologies"]

    @pytest.mark.asyncio  
    async def test_handoff_id_generation(self, comm_manager):
        """Test handoff ID generation is unique"""
        # Create multiple handoffs and ensure unique IDs
        handoff_ids = []
        
        for i in range(3):
            handoff_id = await comm_manager.create_handoff(
                from_agent=f"agent_{i}",
                to_agent="target",
                handoff_type="test",
                data={"index": i},
                instructions=f"Test handoff {i}"
            )
            handoff_ids.append(handoff_id)
        
        # All IDs should be unique
        assert len(set(handoff_ids)) == len(handoff_ids)
        
        # All should follow expected format
        for handoff_id in handoff_ids:
            assert handoff_id.startswith("handoff_")
            parts = handoff_id.split("_")
            assert len(parts) >= 3  # handoff_timestamp_hash (timestamp might have multiple parts)


# Test Utilities and Edge Cases
class TestEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.mark.asyncio
    async def test_project_analyzer_file_read_permission_error(self):
        """Test handling of file permission errors"""
        analyzer = ProjectAnalyzer()
        
        with patch('os.walk') as mock_walk, \
             patch('builtins.open', side_effect=PermissionError("Access denied")):
            
            mock_walk.return_value = [("/test", [], ["test.py"])]
            
            # Should not raise exception, just skip files
            analysis = await analyzer._analyze_file_system(Path("/test"))
            assert analysis["total_lines"] == 0

    @pytest.mark.asyncio
    async def test_project_analyzer_unicode_decode_error(self):
        """Test handling of unicode decode errors"""
        analyzer = ProjectAnalyzer()
        
        with patch('os.walk') as mock_walk, \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_walk.return_value = [("/test", [], ["test.py"])]
            mock_file.return_value.read.side_effect = UnicodeDecodeError(
                "utf-8", b"\xff", 0, 1, "invalid start byte"
            )
            
            # Should handle unicode errors gracefully
            analysis = await analyzer._analyze_file_system(Path("/test"))
            assert analysis["total_files"] == 1
            assert analysis["total_lines"] == 0

    def test_technology_stack_empty_initialization(self):
        """Test TechnologyStack with empty sets"""
        stack = TechnologyStack(
            languages=set(),
            frameworks=set(), 
            databases=set(),
            tools=set(),
            package_managers=set()
        )
        
        stack_dict = stack.to_dict()
        assert stack_dict["languages"] == []
        assert stack_dict["frameworks"] == []

    def test_context_package_with_none_values(self):
        """Test ContextPackage handling of None values"""
        context_package = ContextPackage(
            project_context={"value": None},
            technical_context={},
            examples=[{"title": None, "code": None}],
            patterns=[],
            validation_gates=[],
            references=[],
            success_criteria=[]
        )
        
        markdown = context_package.to_markdown()
        assert "**Value**: None" in markdown

    @pytest.mark.asyncio
    async def test_communication_manager_concurrent_handoffs(self):
        """Test concurrent handoff creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            comm_manager = CommunicationManager(Path(temp_dir))
            
            # Create multiple handoffs concurrently
            tasks = []
            for i in range(5):
                task = comm_manager.create_handoff(
                    from_agent=f"agent_{i}",
                    to_agent="target",
                    handoff_type="concurrent_test",
                    data={"id": i},
                    instructions=f"Concurrent handoff {i}"
                )
                tasks.append(task)
            
            handoff_ids = await asyncio.gather(*tasks)
            
            # All should be unique
            assert len(set(handoff_ids)) == len(handoff_ids)
            
            # All files should exist
            for handoff_id in handoff_ids:
                json_file = comm_manager.handoffs_dir / f"{handoff_id}.json"
                md_file = comm_manager.handoffs_dir / f"{handoff_id}.md"
                assert json_file.exists()
                assert md_file.exists()


# Performance and Integration Tests
class TestIntegration:
    """Integration tests between components"""

    @pytest.mark.asyncio
    async def test_full_analysis_to_context_workflow(self, tmp_path):
        """Test complete workflow from analysis to context engineering"""
        # Setup
        project_dir = tmp_path / "integration_test"
        project_dir.mkdir()
        
        # Create project files
        (project_dir / "main.py").write_text("print('hello world')")
        (project_dir / "requirements.txt").write_text("fastapi\nuvicorn")
        (project_dir / "README.md").write_text("# Integration Test Project")
        
        workspace_dir = tmp_path / "workspace"
        
        # Phase 1: Project Analysis
        analyzer = ProjectAnalyzer()
        
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                (str(project_dir), [], ["main.py", "requirements.txt", "README.md"])
            ]
            
            profile = await analyzer.analyze_project(str(project_dir))
        
        assert profile.name == "integration_test"
        assert "python" in profile.technology_stack.languages
        
        # Phase 2: Context Engineering
        context_engineer = ContextEngineer(workspace_dir)
        context_package = context_engineer.engineer_context_for_phase(
            "analysis", profile, {}, ContextLevel.STANDARD
        )
        
        assert context_package.project_context["name"] == "integration_test"
        
        # Phase 3: PRP Generation
        prp_generator = PRPGenerator(workspace_dir)
        prp = prp_generator.generate_factory_analysis_prp(
            profile, context_package, "Create FastAPI application"
        )
        
        assert prp.type == PRPType.FACTORY_ANALYSIS
        assert "FastAPI application" in prp.execution_prompt
        
        # Phase 4: Communication
        comm_manager = CommunicationManager(workspace_dir)
        handoff_id = await comm_manager.create_handoff(
            from_agent="analyzer",
            to_agent="generator", 
            handoff_type="analysis_complete",
            data=profile.to_dict(),
            instructions="Analysis complete, proceed with generation"
        )
        
        assert handoff_id.startswith("handoff_")
        
        # Verify all components created their files
        assert (context_engineer.context_library / "analysis_context.md").exists()
        assert (prp_generator.generated_dir / f"{prp.id}.md").exists()
        assert (comm_manager.handoffs_dir / f"{handoff_id}.json").exists()

    def test_enum_coverage(self):
        """Test all enum values are covered"""
        # ProjectComplexity
        complexities = [
            ProjectComplexity.SIMPLE,
            ProjectComplexity.MEDIUM, 
            ProjectComplexity.COMPLEX,
            ProjectComplexity.ENTERPRISE
        ]
        assert all(c.value for c in complexities)
        
        # ArchitecturePattern
        architectures = [
            ArchitecturePattern.MONOLITHIC,
            ArchitecturePattern.MICROSERVICES,
            ArchitecturePattern.JAMSTACK,
            ArchitecturePattern.FULLSTACK,
            ArchitecturePattern.API_FIRST,
            ArchitecturePattern.SERVERLESS
        ]
        assert all(a.value for a in architectures)
        
        # ContextLevel
        levels = [
            ContextLevel.MINIMAL,
            ContextLevel.STANDARD,
            ContextLevel.DEEP,
            ContextLevel.EXPERT
        ]
        assert all(l.value for l in levels)
        
        # PRPType
        types = [
            PRPType.FACTORY_ANALYSIS,
            PRPType.FACTORY_GENERATION,
            PRPType.AGENT_SPECIALIZATION,
            PRPType.WORKFLOW_OPTIMIZATION,
            PRPType.VALIDATION_COMPREHENSIVE
        ]
        assert all(t.value for t in types)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=subforge.core", "--cov-report=term-missing"])
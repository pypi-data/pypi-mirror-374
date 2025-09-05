#!/usr/bin/env python3
"""
Comprehensive tests for ProjectAnalyzer
Tests project analysis functionality, technology detection, and edge cases
"""

import sys
from pathlib import Path

import pytest

# Add subforge to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subforge.core.project_analyzer import (
    ArchitecturePattern,
    ProjectAnalyzer,
    ProjectComplexity,
    ProjectProfile,
    TechnologyStack,
)


class TestTechnologyStack:
    """Test TechnologyStack dataclass functionality"""

    def test_technology_stack_creation(self):
        """Test creating a TechnologyStack instance"""
        stack = TechnologyStack(
            languages={"python", "javascript"},
            frameworks={"fastapi", "react"},
            databases={"postgresql", "redis"},
            tools={"docker", "kubernetes"},
            package_managers={"pip", "npm"},
        )

        assert "python" in stack.languages
        assert "javascript" in stack.languages
        assert "fastapi" in stack.frameworks
        assert "react" in stack.frameworks
        assert "postgresql" in stack.databases
        assert "docker" in stack.tools
        assert "pip" in stack.package_managers

    def test_technology_stack_to_dict(self):
        """Test TechnologyStack serialization to dict"""
        stack = TechnologyStack(
            languages={"python", "typescript"},
            frameworks={"nextjs", "fastapi"},
            databases={"mongodb"},
            tools={"git"},
            package_managers={"yarn"},
        )

        stack_dict = stack.to_dict()

        # Should convert sets to lists
        assert isinstance(stack_dict["languages"], list)
        assert isinstance(stack_dict["frameworks"], list)
        assert isinstance(stack_dict["databases"], list)
        assert isinstance(stack_dict["tools"], list)
        assert isinstance(stack_dict["package_managers"], list)

        # Should contain expected values
        assert "python" in stack_dict["languages"]
        assert "typescript" in stack_dict["languages"]
        assert "nextjs" in stack_dict["frameworks"]
        assert "fastapi" in stack_dict["frameworks"]


class TestProjectProfile:
    """Test ProjectProfile dataclass functionality"""

    def test_project_profile_creation(self, tmp_path):
        """Test creating a ProjectProfile instance"""
        stack = TechnologyStack(
            languages={"python"},
            frameworks={"django"},
            databases={"sqlite"},
            tools={"git"},
            package_managers={"pip"},
        )

        profile = ProjectProfile(
            name="test_project",
            path=str(tmp_path),
            technology_stack=stack,
            architecture_pattern=ArchitecturePattern.MONOLITHIC,
            complexity=ProjectComplexity.MEDIUM,
            team_size_estimate=3,
            file_count=25,
            lines_of_code=1000,
            has_tests=True,
            has_ci_cd=False,
            has_docker=True,
            has_docs=True,
            recommended_subagents=["backend-developer", "test-engineer"],
            integration_requirements=["database", "api"],
        )

        assert profile.name == "test_project"
        assert profile.path == str(tmp_path)
        assert profile.technology_stack == stack
        assert profile.architecture_pattern == ArchitecturePattern.MONOLITHIC
        assert profile.complexity == ProjectComplexity.MEDIUM
        assert profile.team_size_estimate == 3
        assert profile.file_count == 25
        assert profile.lines_of_code == 1000
        assert profile.has_tests is True
        assert profile.has_ci_cd is False
        assert profile.has_docker is True
        assert profile.has_docs is True
        assert "backend-developer" in profile.recommended_subagents
        assert "test-engineer" in profile.recommended_subagents
        assert "database" in profile.integration_requirements
        assert "api" in profile.integration_requirements

    def test_project_profile_to_dict(self, tmp_path):
        """Test ProjectProfile serialization to dict"""
        stack = TechnologyStack(
            languages={"go"},
            frameworks={"gin"},
            databases={"postgres"},
            tools={"make"},
            package_managers={"go_mod"},
        )

        profile = ProjectProfile(
            name="go_api",
            path=str(tmp_path),
            technology_stack=stack,
            architecture_pattern=ArchitecturePattern.API_FIRST,
            complexity=ProjectComplexity.SIMPLE,
            team_size_estimate=2,
            file_count=10,
            lines_of_code=500,
            has_tests=False,
            has_ci_cd=True,
            has_docker=False,
            has_docs=False,
            recommended_subagents=["backend-developer"],
            integration_requirements=["testing"],
        )

        profile_dict = profile.to_dict()

        assert profile_dict["name"] == "go_api"
        assert profile_dict["path"] == str(tmp_path)
        assert profile_dict["architecture_pattern"] == "api_first"
        assert profile_dict["complexity"] == "simple"
        assert profile_dict["team_size_estimate"] == 2
        assert isinstance(profile_dict["technology_stack"], dict)
        assert "go" in profile_dict["technology_stack"]["languages"]
        assert "gin" in profile_dict["technology_stack"]["frameworks"]


class TestProjectAnalyzer:
    """Test ProjectAnalyzer main functionality"""

    def test_analyzer_initialization(self):
        """Test ProjectAnalyzer initialization"""
        analyzer = ProjectAnalyzer()

        # Test default configuration
        assert analyzer.config is not None
        assert analyzer.file_analyzers is not None
        assert analyzer.pattern_detectors is not None

        # Test technology patterns are loaded
        assert len(analyzer.technology_patterns) > 0
        assert "python" in analyzer.technology_patterns
        assert "javascript" in analyzer.technology_patterns
        assert "java" in analyzer.technology_patterns

    def test_detect_languages_python(self, tmp_path):
        """Test Python language detection"""
        analyzer = ProjectAnalyzer()

        # Create Python files
        (tmp_path / "app.py").write_text("def main(): pass")
        (tmp_path / "utils.py").write_text("import os\nprint('hello')")
        (tmp_path / "requirements.txt").write_text("fastapi==0.68.0\npydantic")

        languages = analyzer._detect_languages(tmp_path)

        assert "python" in languages

    def test_detect_languages_javascript(self, tmp_path):
        """Test JavaScript/TypeScript language detection"""
        analyzer = ProjectAnalyzer()

        # Create JavaScript/TypeScript files
        (tmp_path / "app.js").write_text("console.log('hello');")
        (tmp_path / "utils.ts").write_text("interface User { name: string; }")
        (tmp_path / "package.json").write_text('{"name": "test", "dependencies": {}}')

        languages = analyzer._detect_languages(tmp_path)

        assert "javascript" in languages or "typescript" in languages

    def test_detect_languages_multiple(self, tmp_path):
        """Test detection of multiple languages"""
        analyzer = ProjectAnalyzer()

        # Create mixed language project
        (tmp_path / "backend.py").write_text("from fastapi import FastAPI")
        (tmp_path / "frontend.js").write_text("import React from 'react';")
        (tmp_path / "script.sh").write_text("#!/bin/bash\necho 'hello'")
        (tmp_path / "config.yaml").write_text("version: 1.0")

        languages = analyzer._detect_languages(tmp_path)

        # Should detect multiple languages
        assert len(languages) >= 2
        assert "python" in languages
        assert "javascript" in languages

    def test_detect_frameworks_fastapi(self, tmp_path):
        """Test FastAPI framework detection"""
        analyzer = ProjectAnalyzer()

        # Create FastAPI project structure
        (tmp_path / "main.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()"
        )
        (tmp_path / "requirements.txt").write_text("fastapi==0.68.0\nuvicorn")

        frameworks = analyzer._detect_frameworks(tmp_path, {"python"})

        assert "fastapi" in frameworks

    def test_detect_frameworks_react(self, tmp_path):
        """Test React framework detection"""
        analyzer = ProjectAnalyzer()

        # Create React project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "App.js").write_text("import React from 'react';")
        (tmp_path / "package.json").write_text('{"dependencies": {"react": "^17.0.0"}}')

        frameworks = analyzer._detect_frameworks(tmp_path, {"javascript"})

        assert "react" in frameworks

    def test_detect_frameworks_django(self, tmp_path):
        """Test Django framework detection"""
        analyzer = ProjectAnalyzer()

        # Create Django project structure
        (tmp_path / "manage.py").write_text(
            "#!/usr/bin/env python\nfrom django.core.management import execute_from_command_line"
        )
        (tmp_path / "settings.py").write_text(
            "INSTALLED_APPS = ['django.contrib.admin']"
        )

        frameworks = analyzer._detect_frameworks(tmp_path, {"python"})

        assert "django" in frameworks

    def test_detect_databases_postgresql(self, tmp_path):
        """Test PostgreSQL database detection"""
        analyzer = ProjectAnalyzer()

        # Create files indicating PostgreSQL usage
        (tmp_path / "requirements.txt").write_text("psycopg2-binary\nsqlalchemy")
        (tmp_path / "models.py").write_text(
            "from sqlalchemy import create_engine\nengine = create_engine('postgresql://...')"
        )

        databases = analyzer._detect_databases(tmp_path)

        assert "postgresql" in databases

    def test_detect_databases_mongodb(self, tmp_path):
        """Test MongoDB database detection"""
        analyzer = ProjectAnalyzer()

        # Create files indicating MongoDB usage
        (tmp_path / "package.json").write_text(
            '{"dependencies": {"mongoose": "^6.0.0"}}'
        )
        (tmp_path / "db.js").write_text("const mongoose = require('mongoose');")

        databases = analyzer._detect_databases(tmp_path)

        assert "mongodb" in databases

    def test_detect_tools_docker(self, tmp_path):
        """Test Docker tool detection"""
        analyzer = ProjectAnalyzer()

        # Create Docker files
        (tmp_path / "Dockerfile").write_text("FROM python:3.9\nWORKDIR /app")
        (tmp_path / "docker-compose.yml").write_text("version: '3.8'\nservices:")

        tools = analyzer._detect_tools(tmp_path)

        assert "docker" in tools

    def test_detect_tools_kubernetes(self, tmp_path):
        """Test Kubernetes tool detection"""
        analyzer = ProjectAnalyzer()

        # Create Kubernetes files
        k8s_dir = tmp_path / "k8s"
        k8s_dir.mkdir()
        (k8s_dir / "deployment.yaml").write_text(
            "apiVersion: apps/v1\nkind: Deployment"
        )
        (k8s_dir / "service.yaml").write_text("apiVersion: v1\nkind: Service")

        tools = analyzer._detect_tools(tmp_path)

        assert "kubernetes" in tools

    def test_detect_package_managers_pip(self, tmp_path):
        """Test pip package manager detection"""
        analyzer = ProjectAnalyzer()

        # Create pip files
        (tmp_path / "requirements.txt").write_text("fastapi\npydantic")
        (tmp_path / "setup.py").write_text("from setuptools import setup")

        package_managers = analyzer._detect_package_managers(tmp_path)

        assert "pip" in package_managers

    def test_detect_package_managers_npm(self, tmp_path):
        """Test npm/yarn package manager detection"""
        analyzer = ProjectAnalyzer()

        # Create npm files
        (tmp_path / "package.json").write_text('{"name": "test"}')
        (tmp_path / "package-lock.json").write_text('{"name": "test"}')

        package_managers = analyzer._detect_package_managers(tmp_path)

        assert "npm" in package_managers

    def test_determine_complexity_simple(self, tmp_path):
        """Test simple project complexity determination"""
        analyzer = ProjectAnalyzer()

        # Create simple project (few files, small size)
        (tmp_path / "app.py").write_text("print('hello')")  # Small file
        (tmp_path / "README.md").write_text("# Simple Project")

        complexity = analyzer._determine_complexity(
            file_count=2,
            lines_of_code=50,
            frameworks={"flask"},
            has_tests=False,
            has_ci_cd=False,
            has_docker=False,
        )

        assert complexity == ProjectComplexity.SIMPLE

    def test_determine_complexity_medium(self, tmp_path):
        """Test medium project complexity determination"""
        analyzer = ProjectAnalyzer()

        complexity = analyzer._determine_complexity(
            file_count=25,
            lines_of_code=2000,
            frameworks={"fastapi", "react"},
            has_tests=True,
            has_ci_cd=False,
            has_docker=True,
        )

        assert complexity == ProjectComplexity.MEDIUM

    def test_determine_complexity_complex(self, tmp_path):
        """Test complex project complexity determination"""
        analyzer = ProjectAnalyzer()

        complexity = analyzer._determine_complexity(
            file_count=150,
            lines_of_code=15000,
            frameworks={"django", "react", "redux", "celery"},
            has_tests=True,
            has_ci_cd=True,
            has_docker=True,
        )

        assert complexity == ProjectComplexity.COMPLEX

    def test_determine_complexity_enterprise(self, tmp_path):
        """Test enterprise project complexity determination"""
        analyzer = ProjectAnalyzer()

        complexity = analyzer._determine_complexity(
            file_count=500,
            lines_of_code=50000,
            frameworks={"spring", "react", "redux", "kafka", "elasticsearch"},
            has_tests=True,
            has_ci_cd=True,
            has_docker=True,
        )

        assert complexity == ProjectComplexity.ENTERPRISE

    def test_detect_architecture_monolithic(self, tmp_path):
        """Test monolithic architecture pattern detection"""
        analyzer = ProjectAnalyzer()

        # Create monolithic structure
        (tmp_path / "app.py").write_text("from flask import Flask")
        (tmp_path / "models.py").write_text("class User: pass")
        (tmp_path / "views.py").write_text("def index(): return 'Hello'")

        pattern = analyzer._detect_architecture_pattern(
            tmp_path, frameworks={"flask"}, has_docker=False
        )

        assert pattern == ArchitecturePattern.MONOLITHIC

    def test_detect_architecture_microservices(self, tmp_path):
        """Test microservices architecture pattern detection"""
        analyzer = ProjectAnalyzer()

        # Create microservices structure
        (tmp_path / "user-service").mkdir()
        (tmp_path / "order-service").mkdir()
        (tmp_path / "payment-service").mkdir()
        (tmp_path / "docker-compose.yml").write_text("version: '3.8'\nservices:")

        pattern = analyzer._detect_architecture_pattern(
            tmp_path, frameworks={"fastapi"}, has_docker=True
        )

        assert pattern == ArchitecturePattern.MICROSERVICES

    def test_detect_architecture_jamstack(self, tmp_path):
        """Test JAMstack architecture pattern detection"""
        analyzer = ProjectAnalyzer()

        # Create JAMstack structure
        (tmp_path / "src").mkdir()
        (tmp_path / "public").mkdir()
        (tmp_path / "package.json").write_text('{"dependencies": {"next": "^12.0.0"}}')
        (tmp_path / "next.config.js").write_text("module.exports = {}")

        pattern = analyzer._detect_architecture_pattern(
            tmp_path, frameworks={"nextjs"}, has_docker=False
        )

        assert pattern == ArchitecturePattern.JAMSTACK

    def test_detect_architecture_serverless(self, tmp_path):
        """Test serverless architecture pattern detection"""
        analyzer = ProjectAnalyzer()

        # Create serverless structure
        (tmp_path / "serverless.yml").write_text("service: my-service")
        (tmp_path / "handler.py").write_text("def lambda_handler(event, context): pass")

        pattern = analyzer._detect_architecture_pattern(
            tmp_path, frameworks={"aws_lambda"}, has_docker=False
        )

        assert pattern == ArchitecturePattern.SERVERLESS

    def test_recommend_subagents_fullstack(self):
        """Test subagent recommendations for fullstack project"""
        analyzer = ProjectAnalyzer()

        recommendations = analyzer._recommend_subagents(
            technology_stack=TechnologyStack(
                languages={"python", "javascript"},
                frameworks={"fastapi", "react"},
                databases={"postgresql"},
                tools={"docker"},
                package_managers={"pip", "npm"},
            ),
            complexity=ProjectComplexity.MEDIUM,
            architecture_pattern=ArchitecturePattern.FULLSTACK,
            has_tests=False,
            has_ci_cd=False,
            has_docker=True,
        )

        assert "backend-developer" in recommendations
        assert "frontend-developer" in recommendations
        assert "test-engineer" in recommendations  # Due to has_tests=False
        assert "devops-engineer" in recommendations  # Due to Docker

    def test_recommend_subagents_api_only(self):
        """Test subagent recommendations for API-only project"""
        analyzer = ProjectAnalyzer()

        recommendations = analyzer._recommend_subagents(
            technology_stack=TechnologyStack(
                languages={"python"},
                frameworks={"fastapi"},
                databases={"postgresql"},
                tools=set(),
                package_managers={"pip"},
            ),
            complexity=ProjectComplexity.SIMPLE,
            architecture_pattern=ArchitecturePattern.API_FIRST,
            has_tests=True,
            has_ci_cd=False,
            has_docker=False,
        )

        assert "backend-developer" in recommendations
        assert "api-developer" in recommendations
        # Should not include frontend-developer for API-only
        assert "frontend-developer" not in recommendations

    @pytest.mark.asyncio
    async def test_analyze_project_full_workflow(self, tmp_path):
        """Test complete project analysis workflow"""
        analyzer = ProjectAnalyzer()

        # Create comprehensive project structure
        project_dir = tmp_path / "fullstack_app"
        project_dir.mkdir()

        # Backend
        backend_dir = project_dir / "backend"
        backend_dir.mkdir()
        (backend_dir / "main.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()"
        )
        (backend_dir / "models.py").write_text(
            "from sqlalchemy import Column, Integer, String"
        )
        (backend_dir / "requirements.txt").write_text(
            "fastapi\nsqlalchemy\npsycopg2-binary"
        )

        # Frontend
        frontend_dir = project_dir / "frontend"
        frontend_dir.mkdir()
        (frontend_dir / "package.json").write_text(
            '{"dependencies": {"react": "^17.0.0", "typescript": "^4.0.0"}}'
        )
        (frontend_dir / "src").mkdir()
        (frontend_dir / "src" / "App.tsx").write_text("import React from 'react';")

        # Tests
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_app(): assert True")

        # Docker
        (project_dir / "Dockerfile").write_text("FROM python:3.9")
        (project_dir / "docker-compose.yml").write_text("version: '3.8'")

        # CI/CD
        github_dir = project_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True)
        (github_dir / "ci.yml").write_text("name: CI\non: [push]")

        # Documentation
        (project_dir / "README.md").write_text(
            "# Fullstack App\nComprehensive documentation"
        )

        # Analyze the project
        profile = await analyzer.analyze_project(str(project_dir))

        # Verify analysis results
        assert profile.name == "fullstack_app"
        assert profile.path == str(project_dir)

        # Technology stack
        assert "python" in profile.technology_stack.languages
        assert "typescript" in profile.technology_stack.languages
        assert "fastapi" in profile.technology_stack.frameworks
        assert "react" in profile.technology_stack.frameworks
        assert "postgresql" in profile.technology_stack.databases
        assert "docker" in profile.technology_stack.tools
        assert "pip" in profile.technology_stack.package_managers
        assert "npm" in profile.technology_stack.package_managers

        # Project characteristics
        assert profile.complexity in [
            ProjectComplexity.MEDIUM,
            ProjectComplexity.COMPLEX,
        ]
        assert profile.architecture_pattern in [
            ArchitecturePattern.FULLSTACK,
            ArchitecturePattern.MICROSERVICES,
        ]
        assert profile.has_tests is True
        assert profile.has_ci_cd is True
        assert profile.has_docker is True
        assert profile.has_docs is True

        # Subagent recommendations
        assert "backend-developer" in profile.recommended_subagents
        assert "frontend-developer" in profile.recommended_subagents
        assert "devops-engineer" in profile.recommended_subagents

        # Integration requirements
        assert len(profile.integration_requirements) > 0


class TestProjectAnalyzer_EdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_analyze_empty_directory(self, tmp_path):
        """Test analyzing an empty directory"""
        analyzer = ProjectAnalyzer()

        empty_dir = tmp_path / "empty_project"
        empty_dir.mkdir()

        profile = await analyzer.analyze_project(str(empty_dir))

        assert profile.name == "empty_project"
        assert profile.file_count == 0
        assert profile.lines_of_code == 0
        assert profile.complexity == ProjectComplexity.SIMPLE
        assert len(profile.technology_stack.languages) == 0
        assert (
            len(profile.recommended_subagents) > 0
        )  # Should still recommend basic agents

    @pytest.mark.asyncio
    async def test_analyze_nonexistent_directory(self):
        """Test analyzing a non-existent directory"""
        analyzer = ProjectAnalyzer()

        with pytest.raises(FileNotFoundError):
            await analyzer.analyze_project("/nonexistent/path")

    @pytest.mark.asyncio
    async def test_analyze_file_instead_of_directory(self, tmp_path):
        """Test analyzing a file instead of directory"""
        analyzer = ProjectAnalyzer()

        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with pytest.raises(NotADirectoryError):
            await analyzer.analyze_project(str(test_file))

    def test_count_lines_of_code_with_binary_files(self, tmp_path):
        """Test line counting with binary files that should be skipped"""
        analyzer = ProjectAnalyzer()

        # Create text files
        (tmp_path / "code.py").write_text(
            "def hello():\n    print('world')\n    return True"
        )
        (tmp_path / "readme.md").write_text("# Project\n\nDescription here")

        # Create binary-like file
        (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

        lines = analyzer._count_lines_of_code(tmp_path)

        # Should count lines from text files only
        assert lines >= 5  # At least 5 lines from the text files

    def test_detect_languages_with_unusual_extensions(self, tmp_path):
        """Test language detection with unusual file extensions"""
        analyzer = ProjectAnalyzer()

        # Create files with various extensions
        (tmp_path / "script.py3").write_text("#!/usr/bin/env python3\nprint('hello')")
        (tmp_path / "config.yml").write_text("version: 1.0")
        (tmp_path / "data.json").write_text('{"name": "test"}')
        (tmp_path / "style.scss").write_text("$primary-color: blue;")

        languages = analyzer._detect_languages(tmp_path)

        # Should detect python from .py3 file
        assert "python" in languages

    def test_detect_frameworks_with_subtle_indicators(self, tmp_path):
        """Test framework detection with subtle file indicators"""
        analyzer = ProjectAnalyzer()

        # Create subtle FastAPI indicators
        (tmp_path / "api").mkdir()
        (tmp_path / "api" / "__init__.py").write_text("")
        (tmp_path / "api" / "routes.py").write_text(
            "from fastapi import APIRouter\nrouter = APIRouter()"
        )

        frameworks = analyzer._detect_frameworks(tmp_path, {"python"})

        assert "fastapi" in frameworks

    def test_estimate_team_size_various_complexities(self):
        """Test team size estimation for various project complexities"""
        analyzer = ProjectAnalyzer()

        # Simple project
        simple_size = analyzer._estimate_team_size(
            complexity=ProjectComplexity.SIMPLE,
            frameworks={"flask"},
            architecture_pattern=ArchitecturePattern.MONOLITHIC,
        )
        assert simple_size <= 3

        # Medium project
        medium_size = analyzer._estimate_team_size(
            complexity=ProjectComplexity.MEDIUM,
            frameworks={"fastapi", "react"},
            architecture_pattern=ArchitecturePattern.FULLSTACK,
        )
        assert 2 <= medium_size <= 6

        # Complex project
        complex_size = analyzer._estimate_team_size(
            complexity=ProjectComplexity.COMPLEX,
            frameworks={"django", "react", "redux", "celery"},
            architecture_pattern=ArchitecturePattern.MICROSERVICES,
        )
        assert 4 <= complex_size <= 10

        # Enterprise project
        enterprise_size = analyzer._estimate_team_size(
            complexity=ProjectComplexity.ENTERPRISE,
            frameworks={"spring", "angular", "kafka", "elasticsearch"},
            architecture_pattern=ArchitecturePattern.MICROSERVICES,
        )
        assert enterprise_size >= 6


class TestProjectAnalyzer_Performance:
    """Test performance aspects of project analysis"""

    @pytest.mark.asyncio
    async def test_analyze_large_directory_structure(self, tmp_path):
        """Test analyzing project with many files"""
        analyzer = ProjectAnalyzer()

        # Create project with many files
        large_project = tmp_path / "large_project"
        large_project.mkdir()

        # Create multiple directories with files
        for i in range(10):
            dir_path = large_project / f"module_{i}"
            dir_path.mkdir()

            for j in range(5):
                file_path = dir_path / f"file_{j}.py"
                file_path.write_text(
                    f"# Module {i}, File {j}\ndef function_{j}(): pass\n"
                )

        # Add some configuration files
        (large_project / "requirements.txt").write_text("flask\nrequests\nnumpy")
        (large_project / "setup.py").write_text(
            "from setuptools import setup, find_packages"
        )

        # Analyze project (should complete reasonably fast)
        import time

        start_time = time.time()

        profile = await analyzer.analyze_project(str(large_project))

        end_time = time.time()
        analysis_time = end_time - start_time

        # Verify analysis completed
        assert profile.name == "large_project"
        assert profile.file_count >= 50
        assert "python" in profile.technology_stack.languages

        # Should complete within reasonable time (adjust threshold as needed)
        assert analysis_time < 5.0  # Should finish within 5 seconds

    def test_memory_usage_with_large_files(self, tmp_path):
        """Test memory usage when analyzing large files"""
        analyzer = ProjectAnalyzer()

        # Create a large Python file
        large_file = tmp_path / "large_module.py"
        content = "# Large Python module\n" + "def function_{}(): pass\n" * 1000
        large_file.write_text(content)

        # This should not cause memory issues
        lines = analyzer._count_lines_of_code(tmp_path)
        assert lines >= 1000

        languages = analyzer._detect_languages(tmp_path)
        assert "python" in languages


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--color=yes"])
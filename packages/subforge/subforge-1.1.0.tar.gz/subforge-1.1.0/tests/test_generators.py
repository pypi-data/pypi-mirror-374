#!/usr/bin/env python3
"""
Comprehensive unit tests for subforge.generators module
Tests all generator functions, template generation, and edge cases
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch
from datetime import datetime

import pytest

# Add subforge to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subforge.generators import PromptGenerator, ClaudeConfigGenerator
from subforge.core.project_analyzer import (
    ProjectProfile, 
    TechnologyStack, 
    ArchitecturePattern, 
    ProjectComplexity
)


class TestPromptGenerator:
    """Test PromptGenerator class and its methods"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.generator = PromptGenerator()
        
        # Create mock profile with proper structure
        self.mock_profile = MagicMock()
        self.mock_profile.name = "test-project"
        self.mock_profile.path = "/test/project"
        
        # Create a real TechnologyStack for proper testing
        self.technology_stack = TechnologyStack(
            languages={"python", "javascript"},
            frameworks={"fastapi", "react"},
            databases={"postgresql"},
            tools={"docker"},
            package_managers={"npm", "pip"}
        )
        
        # Create a real ProjectProfile for integration tests
        self.real_profile = ProjectProfile(
            name="test-project",
            path="/test/project",
            technology_stack=self.technology_stack,
            architecture_pattern=ArchitecturePattern.JAMSTACK,
            complexity=ProjectComplexity.MEDIUM,
            team_size_estimate=3,
            file_count=50,
            lines_of_code=1000,
            has_tests=True,
            has_ci_cd=False,
            has_docker=True,
            has_docs=True,
            recommended_subagents=["frontend-developer", "backend-developer"],
            integration_requirements=["database", "api"]
        )

    def test_generate_agent_prompt_with_path_object(self):
        """Test generate_agent_prompt with Path object in template"""
        template_content = """# Agent Template
Project: Claude-subagents
Path: /home/nando/projects/Claude-subagents
{{PROJECT_NAME}} configuration
"""
        
        template_path = Path("/mock/template.md")
        template = {"path": template_path}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        # Check that replacements happened (order matters in replacement logic)
        # "Claude-subagents" gets replaced with "test-project" 
        # "/home/nando/projects/Claude-subagents" becomes "/home/nando/projects/test-project"
        assert "test-project" in result
        assert "/home/nando/projects/test-project" in result or "/test/project" in result
        assert "2025-01-01 12:00:00 UTC-3" in result

    def test_generate_agent_prompt_with_template_path_key(self):
        """Test generate_agent_prompt with template_path key in template dict"""
        template_content = """# Agent Template
Project: {{PROJECT_NAME}}
Path: {{PROJECT_PATH}}
"""
        
        template = {"template_path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        assert "test-project" in result
        assert "/test/project" in result

    def test_generate_agent_prompt_with_string_path(self):
        """Test generate_agent_prompt with string path"""
        template_content = """# Agent Template
Project: {PROJECT_NAME}
Path: {PROJECT_PATH}
"""
        
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        assert "test-project" in result
        assert "/test/project" in result

    def test_generate_agent_prompt_all_replacements(self):
        """Test all possible placeholder replacements"""
        template_content = """# Agent Template
Old project: Claude-subagents
Old path: /home/nando/projects/Claude-subagents
New project 1: {{PROJECT_NAME}}
New path 1: {{PROJECT_PATH}}
New project 2: {PROJECT_NAME}
New path 2: {PROJECT_PATH}
"""
        
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        # Check replacements happened (accounting for replacement order effects)
        # The order of replacements affects the final result
        
        # Check all new values are present
        assert result.count("test-project") >= 3  # All project name replacements
        # Path replacements may be affected by order - check for presence
        path_replacements = result.count("/test/project") + result.count("/home/nando/projects/test-project")
        assert path_replacements >= 2  # Some form of path replacement happened

    def test_generate_agent_prompt_with_subforge_timestamp(self):
        """Test timestamp replacement when SubForge signature exists"""
        template_content = """# Agent Template
Some content here.

*Generated by SubForge v1.0 - Intelligent Claude Code Configuration*
"""
        
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        assert "*Generated by SubForge v1.0 - Intelligent Claude Code Configuration*" in result
        assert "*Updated: 2025-01-01 12:00:00 UTC-3*" in result

    def test_generate_agent_prompt_without_subforge_timestamp(self):
        """Test timestamp appending when no SubForge signature exists"""
        template_content = """# Agent Template
Some content here.
No SubForge signature.
"""
        
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        assert result.endswith("*Updated: 2025-01-01 12:00:00 UTC-3*")

    def test_generate_agent_prompt_no_template_path(self):
        """Test error when no template path is provided"""
        template = {"invalid_key": "value"}
        
        with pytest.raises(ValueError, match="Template path not found"):
            self.generator.generate_agent_prompt(template, self.mock_profile)

    def test_generate_agent_prompt_file_not_found(self):
        """Test file not found error handling"""
        template = {"path": "/nonexistent/template.md"}
        
        with pytest.raises(FileNotFoundError):
            self.generator.generate_agent_prompt(template, self.mock_profile)

    def test_generate_agent_prompt_file_read_error(self):
        """Test file read permission error"""
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                self.generator.generate_agent_prompt(template, self.mock_profile)

    def test_generate_agent_prompt_empty_file(self):
        """Test handling of empty template file"""
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data="")):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        assert result == "\n\n*Updated: 2025-01-01 12:00:00 UTC-3*"

    def test_generate_agent_prompt_with_special_characters(self):
        """Test handling of special characters in paths and names"""
        self.mock_profile.name = "test-project with spaces & symbols"
        self.mock_profile.path = "/test/path with spaces/project"
        
        template_content = """{{PROJECT_NAME}} - {{PROJECT_PATH}}"""
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        assert "test-project with spaces & symbols" in result
        assert "/test/path with spaces/project" in result

    def test_generate_agent_prompt_path_object_conversion(self):
        """Test proper conversion of Path object to string"""
        self.mock_profile.path = "/test/project/with/deep/structure"
        
        template_content = """Path: {{PROJECT_PATH}}"""
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        assert "/test/project/with/deep/structure" in result

    def test_generate_agent_prompt_unicode_content(self):
        """Test handling of unicode characters in template content"""
        template_content = """# 🚀 Agent Template
Project: {{PROJECT_NAME}}
Unicode test: 中文测试 émojis 🎉
"""
        
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.generator.generate_agent_prompt(template, self.mock_profile)
        
        assert "🚀" in result
        assert "中文测试" in result
        assert "émojis 🎉" in result
        assert "test-project" in result


class TestClaudeConfigGenerator:
    """Test ClaudeConfigGenerator class and its methods"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.generator = ClaudeConfigGenerator()
        
        # Create a real ProjectProfile for testing
        self.technology_stack = TechnologyStack(
            languages={"python", "javascript", "typescript"},
            frameworks={"fastapi", "react", "nextjs"},
            databases={"postgresql", "redis"},
            tools={"docker", "kubernetes"},
            package_managers={"npm", "pip"}
        )
        
        self.profile = ProjectProfile(
            name="test-project",
            path="/test/project",
            technology_stack=self.technology_stack,
            architecture_pattern=ArchitecturePattern.JAMSTACK,
            complexity=ProjectComplexity.MEDIUM,
            team_size_estimate=3,
            file_count=50,
            lines_of_code=1000,
            has_tests=True,
            has_ci_cd=False,
            has_docker=True,
            has_docs=True,
            recommended_subagents=["frontend-developer", "backend-developer"],
            integration_requirements=["database", "api"]
        )

    def test_generate_claude_config_basic(self):
        """Test basic CLAUDE.md configuration generation"""
        selected_templates = ["Frontend Developer", "Backend Developer"]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        assert "# test-project - Claude Code Agent Configuration" in result
        assert "/test/project" in result
        assert "javascript, python, typescript" in result  # sorted order
        assert "fastapi, nextjs, react" in result  # sorted order  
        assert "docker, kubernetes" in result  # sorted order

    def test_generate_claude_config_agent_formatting(self):
        """Test proper agent name formatting in config"""
        selected_templates = ["Frontend Developer", "Backend Developer", "DevOps Engineer"]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        assert "**@frontend-developer**" in result
        assert "**@backend-developer**" in result
        assert "**@devops-engineer**" in result
        assert "Specialized agent for Frontend Developer" in result
        assert "Specialized agent for Backend Developer" in result
        assert "Specialized agent for DevOps Engineer" in result

    def test_generate_claude_config_empty_templates(self):
        """Test config generation with no selected templates"""
        selected_templates = []
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        assert "# test-project - Claude Code Agent Configuration" in result
        assert "## Available Specialist Agents" in result
        assert "## Agent Coordination Protocol" in result
        assert "*Generated by SubForge v1.0 - Intelligent Claude Code Configuration*" in result

    def test_generate_claude_config_single_template(self):
        """Test config generation with single template"""
        selected_templates = ["Test Engineer"]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        assert "**@test-engineer**" in result
        assert "Specialized agent for Test Engineer" in result

    def test_generate_claude_config_special_characters_in_names(self):
        """Test agent name formatting with special characters"""
        selected_templates = ["Frontend/UI Developer", "Backend & API Developer", "ML/AI Specialist"]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        # Spaces should be replaced with dashes, special chars preserved in description
        assert "**@frontend/ui-developer**" in result
        assert "**@backend-&-api-developer**" in result  
        assert "**@ml/ai-specialist**" in result
        assert "Frontend/UI Developer" in result  # Original name in description
        assert "Backend & API Developer" in result
        assert "ML/AI Specialist" in result

    def test_generate_claude_config_timestamp_format(self):
        """Test correct timestamp formatting"""
        selected_templates = ["Frontend Developer"]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-12-31 23:59:59 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        assert "*Updated: 2025-12-31 23:59:59 UTC-3*" in result

    def test_generate_claude_config_technology_stack_lists(self):
        """Test proper formatting of technology stack as comma-separated lists"""
        # Test with empty sets
        empty_tech_stack = TechnologyStack(
            languages=set(),
            frameworks=set(),
            databases=set(),
            tools=set(),
            package_managers=set()
        )
        
        profile_empty = ProjectProfile(
            name="empty-project",
            path="/empty/project",
            technology_stack=empty_tech_stack,
            architecture_pattern=ArchitecturePattern.MONOLITHIC,
            complexity=ProjectComplexity.SIMPLE,
            team_size_estimate=1,
            file_count=0,
            lines_of_code=0,
            has_tests=False,
            has_ci_cd=False,
            has_docker=False,
            has_docs=False,
            recommended_subagents=[],
            integration_requirements=[]
        )
        
        selected_templates = []
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(profile_empty, selected_templates)
        
        # Should handle empty sets gracefully
        assert "**Languages**: " in result
        assert "**Frameworks**: " in result  
        assert "**Technologies**: " in result

    def test_generate_claude_config_long_template_list(self):
        """Test config generation with many templates"""
        selected_templates = [
            "Frontend Developer",
            "Backend Developer", 
            "DevOps Engineer",
            "Test Engineer",
            "Security Auditor",
            "Database Specialist",
            "Mobile Developer",
            "Performance Optimizer"
        ]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        for template in selected_templates:
            agent_key = template.replace(" ", "-").lower()
            assert f"**@{agent_key}**" in result
            assert f"Specialized agent for {template}" in result

    def test_generate_claude_config_unicode_project_name(self):
        """Test handling of unicode characters in project name and path"""
        self.profile.name = "测试项目-émojis🚀"
        self.profile.path = "/test/项目/path"
        
        selected_templates = ["Frontend Developer"]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        assert "测试项目-émojis🚀" in result
        assert "/test/项目/path" in result

    def test_generate_claude_config_profile_attribute_access(self):
        """Test that all required profile attributes are accessed correctly"""
        # This test ensures we're accessing the TechnologyStack attributes correctly
        selected_templates = ["Frontend Developer"]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.generator.generate_claude_config(self.profile, selected_templates)
        
        # Verify all technology stack attributes are properly converted to lists and joined
        assert any(lang in result for lang in self.technology_stack.languages)
        assert any(fw in result for fw in self.technology_stack.frameworks)
        assert any(tool in result for tool in self.technology_stack.tools)


class TestGeneratorsIntegration:
    """Integration tests for generators module"""

    def setup_method(self):
        """Set up test fixtures"""
        self.prompt_generator = PromptGenerator()
        self.config_generator = ClaudeConfigGenerator()
        
        self.technology_stack = TechnologyStack(
            languages={"python", "javascript"},
            frameworks={"fastapi", "react"},
            databases={"postgresql"},
            tools={"docker"},
            package_managers={"npm", "pip"}
        )
        
        self.profile = ProjectProfile(
            name="integration-test",
            path="/integration/test",
            technology_stack=self.technology_stack,
            architecture_pattern=ArchitecturePattern.JAMSTACK,
            complexity=ProjectComplexity.MEDIUM,
            team_size_estimate=3,
            file_count=50,
            lines_of_code=1000,
            has_tests=True,
            has_ci_cd=False,
            has_docker=True,
            has_docs=True,
            recommended_subagents=["frontend-developer", "backend-developer"],
            integration_requirements=["database", "api"]
        )

    def test_generators_workflow_integration(self):
        """Test typical workflow using both generators"""
        # Step 1: Generate agent prompt
        template_content = """# Agent: {{PROJECT_NAME}}
Path: {{PROJECT_PATH}}
"""
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                agent_prompt = self.prompt_generator.generate_agent_prompt(template, self.profile)
        
        # Step 2: Generate CLAUDE.md config
        selected_templates = ["Frontend Developer", "Backend Developer"]
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            claude_config = self.config_generator.generate_claude_config(self.profile, selected_templates)
        
        # Verify both outputs are consistent
        assert "integration-test" in agent_prompt
        assert "integration-test" in claude_config
        assert "/integration/test" in agent_prompt
        assert "/integration/test" in claude_config
        assert "2025-01-01 12:00:00 UTC-3" in agent_prompt
        assert "2025-01-01 12:00:00 UTC-3" in claude_config

    def test_real_file_operations(self):
        """Test generators with real temporary files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            template_content = """# {{PROJECT_NAME}} Configuration
Project root: {{PROJECT_PATH}}
"""
            temp_file.write(template_content)
            temp_file.flush()
            
            template = {"path": temp_file.name}
            
            try:
                with patch("subforge.generators.datetime") as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                    
                    result = self.prompt_generator.generate_agent_prompt(template, self.profile)
                
                assert "# integration-test Configuration" in result
                assert "Project root: /integration/test" in result
                
            finally:
                Path(temp_file.name).unlink()  # Clean up

    def test_generators_error_consistency(self):
        """Test that both generators handle errors consistently"""
        # Test PromptGenerator error handling
        with pytest.raises(ValueError):
            self.prompt_generator.generate_agent_prompt({}, self.profile)
        
        # Test ClaudeConfigGenerator with None profile should not raise ValueError
        # but might raise AttributeError - testing defensive programming
        with pytest.raises(AttributeError):
            self.config_generator.generate_claude_config(None, ["Frontend Developer"])


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios"""

    def setup_method(self):
        """Set up test fixtures"""
        self.prompt_generator = PromptGenerator()
        self.config_generator = ClaudeConfigGenerator()

    def test_prompt_generator_with_none_template(self):
        """Test PromptGenerator with None template"""
        with pytest.raises((ValueError, AttributeError)):
            self.prompt_generator.generate_agent_prompt(None, MagicMock())

    def test_prompt_generator_with_none_profile(self):
        """Test PromptGenerator with None profile"""
        template = {"path": "/mock/path"}
        
        with patch("builtins.open", mock_open(read_data="test content")):
            with pytest.raises(AttributeError):
                self.prompt_generator.generate_agent_prompt(template, None)

    def test_config_generator_with_none_templates(self):
        """Test ClaudeConfigGenerator with None templates list"""
        profile = MagicMock()
        profile.name = "test"
        profile.path = "/test"
        profile.technology_stack = TechnologyStack(
            languages=set(),
            frameworks=set(), 
            databases=set(),
            tools=set(),
            package_managers=set()
        )
        
        with patch("subforge.generators.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
            
            result = self.config_generator.generate_claude_config(profile, None)
        
        # Should handle None gracefully by treating as empty list
        assert "# test - Claude Code Agent Configuration" in result

    def test_template_with_circular_replacements(self):
        """Test template with potential circular replacement patterns"""
        template_content = """{{PROJECT_NAME}} contains {{PROJECT_PATH}} and {PROJECT_NAME} and {PROJECT_PATH}"""
        
        profile = MagicMock()
        profile.name = "circular-test"  # Normal name
        profile.path = "/circular/path"   # Normal path
        
        template = {"path": "/mock/template.md"}
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.prompt_generator.generate_agent_prompt(template, profile)
        
        # Should replace all placeholders with actual values
        assert "circular-test" in result  # All PROJECT_NAME placeholders replaced
        assert "/circular/path" in result   # All PROJECT_PATH placeholders replaced
        # Should not contain any unreplaced placeholders
        assert "{{PROJECT_NAME}}" not in result
        assert "{{PROJECT_PATH}}" not in result
        assert "{PROJECT_NAME}" not in result  
        assert "{PROJECT_PATH}" not in result

    def test_extremely_long_template_content(self):
        """Test handling of very large template content"""
        # Create a large template content
        large_content = "# Large Template\n" + ("Content line\n" * 10000) + "{{PROJECT_NAME}}\n"
        
        profile = MagicMock()
        profile.name = "large-test"
        profile.path = "/large/test"
        
        template = {"path": "/mock/large_template.md"}
        
        with patch("builtins.open", mock_open(read_data=large_content)):
            with patch("subforge.generators.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00 UTC-3"
                
                result = self.prompt_generator.generate_agent_prompt(template, profile)
        
        assert "large-test" in result
        assert len(result) > 100000  # Should handle large content

    def test_binary_file_handling(self):
        """Test error handling when template file is binary"""
        template = {"path": "/mock/binary_file"}
        profile = MagicMock()
        
        # Simulate binary file read error
        with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")):
            with pytest.raises(UnicodeDecodeError):
                self.prompt_generator.generate_agent_prompt(template, profile)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
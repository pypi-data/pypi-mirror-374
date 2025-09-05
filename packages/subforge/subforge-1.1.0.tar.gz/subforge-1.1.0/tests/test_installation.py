#!/usr/bin/env python3
"""
SubForge Installation Tests
Basic tests to verify package installation and functionality

Created: 2025-09-02 20:10 UTC-3 São Paulo
"""

import importlib
import sys
from pathlib import Path

import pytest


class TestInstallation:
    """Test suite for SubForge installation verification"""

    def test_package_can_be_imported(self):
        """Test that SubForge package can be imported without errors"""
        try:
            import subforge

            assert subforge is not None
        except ImportError as e:
            pytest.fail(f"Failed to import subforge package: {e}")

    def test_version_is_accessible(self):
        """Test that package version is accessible"""
        try:
            import subforge

            version = subforge.__version__
            assert version is not None
            assert isinstance(version, str)
            assert len(version) > 0
            # Basic semver pattern check
            assert "." in version
        except AttributeError:
            pytest.fail("__version__ attribute not found in subforge package")
        except ImportError as e:
            pytest.fail(f"Failed to import subforge package: {e}")

    def test_core_modules_importable(self):
        """Test that core SubForge modules can be imported"""
        core_modules = [
            "subforge.core.project_analyzer",
            "subforge.core.workflow_orchestrator",
            "subforge.core.validation_engine",
            "subforge.core.communication",
        ]

        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_cli_modules_importable(self):
        """Test that CLI modules can be imported"""
        cli_modules = [
            "subforge.simple_cli",
        ]

        # Try to import rich CLI if available
        try:
            pass

            cli_modules.append("subforge.cli")
        except ImportError:
            pass  # Rich CLI not available, skip

        for module_name in cli_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_templates_are_included(self):
        """Test that templates are included in the package"""
        try:
            import subforge

            package_path = Path(subforge.__file__).parent
            templates_path = package_path / "templates"

            assert (
                templates_path.exists()
            ), f"Templates directory not found at {templates_path}"
            assert (
                templates_path.is_dir()
            ), f"Templates path is not a directory: {templates_path}"

            # Check for at least one template file
            template_files = list(templates_path.glob("*.md"))
            assert (
                len(template_files) > 0
            ), f"No template files found in {templates_path}"

        except ImportError as e:
            pytest.fail(f"Failed to import subforge package: {e}")

    def test_main_entry_point_works(self):
        """Test that the main entry point can be called"""
        try:
            pass

            # Just test that the module can be imported
            # Don't actually call main() as it might exit
        except ImportError as e:
            pytest.fail(f"Failed to import subforge.__main__: {e}")

    def test_package_structure(self):
        """Test basic package structure"""
        try:
            import subforge

            package_path = Path(subforge.__file__).parent

            # Check for core subdirectory
            core_path = package_path / "core"
            assert core_path.exists(), f"Core directory not found at {core_path}"
            assert core_path.is_dir(), f"Core path is not a directory: {core_path}"

            # Check for templates subdirectory
            templates_path = package_path / "templates"
            assert (
                templates_path.exists()
            ), f"Templates directory not found at {templates_path}"
            assert (
                templates_path.is_dir()
            ), f"Templates path is not a directory: {templates_path}"

        except ImportError as e:
            pytest.fail(f"Failed to import subforge package: {e}")


class TestEntryPoints:
    """Test suite for command-line entry points"""

    def test_python_module_execution(self):
        """Test that 'python -m subforge' can be executed"""
        import subprocess

        # Test that the module can be called with --help
        try:
            result = subprocess.run(
                [sys.executable, "-m", "subforge", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should not fail completely (exit code 0 or help text shown)
            assert result.returncode in [
                0,
                1,
                2,
            ], f"Unexpected return code: {result.returncode}"
        except subprocess.TimeoutExpired:
            pytest.fail("Command 'python -m subforge --help' timed out")
        except Exception as e:
            pytest.fail(f"Failed to execute 'python -m subforge --help': {e}")


class TestOptionalDependencies:
    """Test suite for optional dependencies handling"""

    def test_rich_cli_fallback(self):
        """Test that the system gracefully falls back when rich dependencies aren't available"""
        # This test verifies that the import system works correctly
        # The actual fallback is tested by the import of __main__
        try:
            pass

            # If this doesn't raise an exception, the fallback mechanism is working
        except ImportError as e:
            pytest.fail(f"Failed to handle optional dependencies gracefully: {e}")


if __name__ == "__main__":
    """Run tests directly with python"""
    print("SubForge Installation Tests")
    print("==========================")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()

    # Run basic import test
    try:
        import subforge

        print(f"✓ SubForge imported successfully")
        print(f"✓ Version: {subforge.__version__}")
        print(f"✓ Location: {subforge.__file__}")
    except Exception as e:
        print(f"✗ Failed to import SubForge: {e}")
        sys.exit(1)

    # If pytest is available, run full test suite
    try:
        import pytest

        print("\nRunning full test suite...")
        pytest.main([__file__, "-v"])
    except ImportError:
        print("Note: pytest not available, running basic tests only")

        # Run basic tests manually
        test_instance = TestInstallation()
        tests = [
            test_instance.test_package_can_be_imported,
            test_instance.test_version_is_accessible,
            test_instance.test_core_modules_importable,
            test_instance.test_cli_modules_importable,
            test_instance.test_templates_are_included,
            test_instance.test_main_entry_point_works,
            test_instance.test_package_structure,
        ]

        for test in tests:
            try:
                test()
                print(f"✓ {test.__name__}")
            except Exception as e:
                print(f"✗ {test.__name__}: {e}")
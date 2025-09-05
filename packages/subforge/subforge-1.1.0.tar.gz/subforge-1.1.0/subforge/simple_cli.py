#!/usr/bin/env python3
"""
SubForge CLI - Simple Command Line Interface (No external dependencies)
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Import SubForge core modules
try:
    from .core.project_analyzer import ProjectAnalyzer
    from .core.workflow_orchestrator import WorkflowOrchestrator
    from .monitoring.metrics_collector import MetricsCollector
    from .orchestration.parallel_executor import ParallelExecutor
except ImportError:
    # Handle running from different directories
    sys.path.append(str(Path(__file__).parent))
    from core.project_analyzer import ProjectAnalyzer
    from core.workflow_orchestrator import WorkflowOrchestrator

    try:
        from monitoring.metrics_collector import MetricsCollector
        from orchestration.parallel_executor import ParallelExecutor
    except ImportError:
        ParallelExecutor = None
        MetricsCollector = None

# ASCII Art Banner
SUBFORGE_BANNER = r"""
 ____        _     _____
/ ___| _   _| |__ |  ___|__  _ __ __ _  ___
\___ \| | | | '_ \| |_ / _ \| '__/ _` |/ _ \
 ___) | |_| | |_) |  _| (_) | | | (_| |  __/
|____/ \__,_|_.__/|_|  \___/|_|  \__, |\___|
                                 |___/

🚀 Forge your perfect Claude Code development team
"""


def print_banner():
    """Print the SubForge banner"""
    print(SUBFORGE_BANNER)


def print_section(title: str, style: str = "="):
    """Print a section header"""
    print(f"\n{style * 60}")
    print(f" {title}")
    print(f"{style * 60}")


async def cmd_init(args):
    """Initialize SubForge for a project"""
    project_path = Path(args.project_path) if args.project_path else Path.cwd()

    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {project_path}")
        return 1

    print_banner()
    print(f"🚀 Initializing SubForge for: {project_path.name}")
    print(f"   Path: {project_path}")

    user_request = args.request or "Set up development environment with best practices"

    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")

        # Just run analysis
        print("\n🔍 Analyzing project...")
        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_path))

        display_analysis_results(profile)
        display_recommended_setup(profile)
        return 0

    # Run full workflow
    print(f"\n📝 Request: {user_request}")
    print("\n🔄 Executing SubForge workflow...")

    try:
        orchestrator = WorkflowOrchestrator()
        context = await orchestrator.execute_workflow(user_request, str(project_path))

        display_workflow_results(context)
        return 0

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


async def cmd_analyze(args):
    """Analyze project structure"""
    project_path = Path(args.project_path) if args.project_path else Path.cwd()

    print("🔍 Analyzing project...")

    try:
        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_path))

        if args.json:
            result = json.dumps(profile.to_dict(), indent=2)
            if args.output:
                Path(args.output).write_text(result)
                print(f"✅ Analysis saved to: {args.output}")
            else:
                print(result)
        else:
            display_analysis_results(profile)
            display_recommended_setup(profile)

            if args.output:
                await analyzer.save_analysis(profile, args.output)
                print(f"✅ Analysis saved to: {args.output}")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_status(args):
    """Show SubForge status"""
    project_path = Path(args.project_path) if args.project_path else Path.cwd()

    print(f"📊 SubForge Status for: {project_path.name}")

    subforge_dir = project_path / ".subforge"
    claude_dir = project_path / ".claude"

    if not subforge_dir.exists():
        print("⚠️  No SubForge configuration found. Run 'subforge init' to get started.")
        return 0

    # Find latest workflow for ID only
    workflow_dirs = sorted(
        subforge_dir.glob("subforge_*"), key=lambda x: x.stat().st_mtime, reverse=True
    )

    if not workflow_dirs:
        print("⚠️  No workflow executions found.")
        return 0

    latest_workflow = workflow_dirs[0]
    workflow_id = latest_workflow.name

    print_section("Current Configuration", "-")
    print(f"Workflow ID: {workflow_id}")

    # Check Claude Code integration and show REAL agents
    if claude_dir.exists():
        agents_dir = claude_dir / "agents"
        if agents_dir.exists():
            agents = sorted(list(agents_dir.glob("*.md")))
            if agents:
                print(f"Active Subagents: {len(agents)}")
                for agent in agents:
                    print(f"  • {agent.stem}")
            else:
                print("Active Subagents: 0")
                print("  ⚠️  No agent files found")

        print("\n✅ Claude Code integration detected")

        # Show directory structure
        if agents_dir.exists():
            print(f"   📁 agents/ ({len(agents)} files)")
            for agent in agents[:10]:  # Show first 10
                print(f"     🤖 {agent.stem}")
            if len(agents) > 10:
                print(f"     ... and {len(agents) - 10} more")

        # Check for commands
        commands_dir = claude_dir / "commands"
        if commands_dir.exists():
            commands = list(commands_dir.glob("*.md"))
            if commands:
                print(f"   📁 commands/ ({len(commands)} files)")
                for cmd in commands[:5]:
                    print(f"     📝 {cmd.stem}")
                if len(commands) > 5:
                    print(f"     ... and {len(commands) - 5} more")
    else:
        print("\n⚠️  No Claude Code integration found")
        print("   Run 'subforge init' to set up Claude Code configuration")

    return 0


async def cmd_update(args):
    """Update/regenerate subagents for current project context"""
    import re
    from datetime import datetime

    project_path = Path(args.project_path) if args.project_path else Path.cwd()

    print(f"🔄 Updating SubForge agents for: {project_path.name}")
    print(f"📁 Project path: {project_path}")

    # Check if SubForge is already initialized
    subforge_dir = project_path / ".subforge"
    claude_dir = project_path / ".claude"

    if not subforge_dir.exists():
        print("⚠️  No SubForge configuration found. Run 'subforge init' first.")
        return 1

    try:
        # List agents that actually exist in the .claude/agents directory
        agents_dir = claude_dir / "agents"

        if not agents_dir.exists():
            print("❌ No agents directory found. Run 'subforge init' first.")
            return 1

        # Get all .md files in the agents directory
        agent_files = sorted(agents_dir.glob("*.md"))

        if not agent_files:
            print("⚠️  No agent files found in .claude/agents/")
            return 1

        # Extract template names from file names (without .md extension)
        selected_templates = [f.stem for f in agent_files]

        print(f"\n📋 Found {len(selected_templates)} agents to update:")
        for template in selected_templates:
            print(f"  • {template}")

        # Re-analyze the current project
        print("\n🔍 Analyzing current project context...")
        from subforge.core.project_analyzer import ProjectAnalyzer

        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_path))

        # Update agent files with current project context
        print("\n🔧 Regenerating agents with current context...")
        agents_dir = claude_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        updated_count = 0
        for template_name in selected_templates:
            template_key = template_name.replace(" ", "-").lower()
            agent_file = agents_dir / f"{template_key}.md"

            if agent_file.exists():
                # Read existing agent content
                content = agent_file.read_text()

                # Replace project context references
                replacements = [
                    (
                        "## PROJECT CONTEXT - Claude-subagents",
                        f"## PROJECT CONTEXT - {profile.name}",
                    ),
                    (
                        "**Project Root**: /home/nando/projects/Claude-subagents",
                        f"**Project Root**: {project_path}",
                    ),
                    ("Project: Claude-subagents", f"Project: {profile.name}"),
                    ("# Claude-subagents", f"# {profile.name}"),
                    ("Claude-subagents project", f"{profile.name} project"),
                ]

                for old, new in replacements:
                    content = content.replace(old, new)

                # Update languages, frameworks, technologies if present
                if "**Languages**:" in content:
                    languages = (
                        list(profile.technology_stack.languages)
                        if profile.technology_stack.languages
                        else []
                    )
                    content = re.sub(
                        r"\*\*Languages\*\*: .+",
                        f'**Languages**: {", ".join(languages)}',
                        content,
                    )
                if "**Frameworks**:" in content:
                    frameworks = (
                        list(profile.technology_stack.frameworks)
                        if profile.technology_stack.frameworks
                        else []
                    )
                    content = re.sub(
                        r"\*\*Frameworks\*\*: .+",
                        f'**Frameworks**: {", ".join(frameworks)}',
                        content,
                    )
                if "**Technologies**:" in content:
                    tools = (
                        list(profile.technology_stack.tools)
                        if profile.technology_stack.tools
                        else []
                    )
                    content = re.sub(
                        r"\*\*Technologies\*\*: .+",
                        f'**Technologies**: {", ".join(tools)}',
                        content,
                    )

                # Update timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC-3")
                if "*Updated:" in content:
                    content = re.sub(
                        r"\*Updated: .+\*", f"*Updated: {timestamp}*", content
                    )
                else:
                    content += f"\n\n*Updated: {timestamp}*"

                # Write updated content
                agent_file.write_text(content)
                print(f"  ✅ Updated: {template_key}.md")
                updated_count += 1
            else:
                print(f"  ⚠️  Agent file not found: {template_key}.md")
                continue

        # Update CLAUDE.md with current project info
        print("\n📝 Updating CLAUDE.md...")
        claude_md = claude_dir / "CLAUDE.md"
        if claude_md.exists():
            content = claude_md.read_text()

            # Update project name in the title
            import re

            content = re.sub(
                r"^# .+ - Claude Code Agent Configuration",
                f"# {profile.name} - Claude Code Agent Configuration",
                content,
                flags=re.MULTILINE,
            )

            # Update project path references
            content = re.sub(
                r"\*\*Project Root\*\*: .+",
                f"**Project Root**: {project_path}",
                content,
            )

            # Update timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC-3")
            content = re.sub(r"\*Updated: .+\*", f"*Updated: {timestamp}*", content)

            # Add update marker if not present
            if "*Updated:" not in content:
                content += f"\n\n*Updated: {timestamp}*"

            claude_md.write_text(content)
            print("  ✅ CLAUDE.md updated")

        print(f"\n✅ Successfully updated {updated_count} agents!")
        print("\n🚀 Your agents now have the correct project context.")

        if args.force:
            print("\n💡 Force mode: All agents were regenerated from scratch.")

        return 0

    except Exception as e:
        print(f"\n❌ Update failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def cmd_validate(args):
    """Validate SubForge configuration"""
    project_path = Path(args.project_path) if args.project_path else Path.cwd()

    print("✅ Validating SubForge configuration...")

    issues = []

    # Check SubForge directory
    subforge_dir = project_path / ".subforge"
    if not subforge_dir.exists():
        issues.append("❌ SubForge directory missing")
        print("❌ SubForge directory missing")
        return 1
    else:
        print("✅ SubForge directory found")

    # Check for workflows
    workflow_dirs = list(subforge_dir.glob("subforge_*"))
    if workflow_dirs:
        print(f"✅ {len(workflow_dirs)} workflow executions found")
    else:
        issues.append("❌ No workflow executions found")
        print("❌ No workflow executions found")

    # Check Claude Code integration
    claude_dir = project_path / ".claude"
    if claude_dir.exists():
        print("✅ Claude Code directory found")

        claude_md = claude_dir / "CLAUDE.md"
        if claude_md.exists():
            print("✅ CLAUDE.md configured")
        else:
            issues.append("❌ CLAUDE.md missing")
            print("❌ CLAUDE.md missing")

        agents_dir = claude_dir / "agents"
        if agents_dir.exists():
            agent_count = len(list(agents_dir.glob("*.md")))
            print(f"✅ {agent_count} subagent files found")
        else:
            issues.append("❌ No agents directory")
            print("❌ No agents directory")
    else:
        issues.append("❌ Claude Code directory missing")
        print("❌ Claude Code directory missing")

    # Summary
    if not issues:
        print("\n🎉 All checks passed!")
        return 0
    else:
        print(f"\n⚠️  {len(issues)} issues found:")
        for issue in issues:
            print(f"   {issue}")
        return 1


def cmd_deploy_commands(args):
    """Deploy SubForge commands to project"""
    import shutil

    project_path = Path(args.project_path) if args.project_path else Path.cwd()

    print(f"📝 Deploying SubForge commands to: {project_path.name}")

    # Check if .claude directory exists
    claude_dir = project_path / ".claude"
    if not claude_dir.exists():
        print("❌ No .claude directory found. Run 'subforge init' first.")
        return 1

    # Create commands directory if it doesn't exist
    commands_dir = claude_dir / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Find source commands (from SubForge installation)
    subforge_root = Path(__file__).parent.parent
    source_commands = subforge_root / ".claude" / "commands"

    if not source_commands.exists():
        print("❌ SubForge commands source not found.")
        return 1

    # Copy all command files
    command_files = list(source_commands.glob("*.md"))

    if not command_files:
        print("⚠️  No command files found in SubForge.")
        return 1

    copied_count = 0
    for cmd_file in command_files:
        dest_file = commands_dir / cmd_file.name
        try:
            shutil.copy2(cmd_file, dest_file)
            print(f"  ✅ Deployed: {cmd_file.name}")
            copied_count += 1
        except Exception as e:
            print(f"  ❌ Failed to deploy {cmd_file.name}: {e}")

    print(f"\n✅ Successfully deployed {copied_count} commands!")
    print("\n📋 Available commands:")
    for cmd_file in command_files:
        cmd_name = cmd_file.stem.replace("-", "_")
        print(f"  • /{cmd_name}")

    return 0


def cmd_templates(args):
    """List available templates"""
    templates_dir = Path(__file__).parent / "templates"

    print("🎨 Available Subagent Templates")

    if not templates_dir.exists():
        print("❌ Templates directory not found")
        return 1

    template_files = list(templates_dir.glob("*.md"))

    if not template_files:
        print("⚠️  No templates found")
        return 0

    print_section("Templates", "-")

    for template_file in sorted(template_files):
        name = template_file.stem
        description = extract_template_description(template_file)
        print(f"• {name:<20} - {description}")

    print(f"\nFound {len(template_files)} templates")
    return 0


def cmd_version(args):
    """Show version information"""
    from subforge import __author__, __description__, __version__

    print(f"SubForge v{__version__}")
    print(f"🚀 {__description__}")
    print(f"\nDeveloped with ❤️ by {__author__}")
    return 0


async def cmd_test_parallel(args):
    """Test parallel execution capabilities"""
    project_path = Path(args.project_path) if args.project_path else Path.cwd()

    print("🚀 Testing SubForge Parallel Execution")
    print("=" * 60)

    if not ParallelExecutor or not MetricsCollector:
        print("❌ Parallel execution modules not available")
        print("   Make sure orchestration and monitoring modules are installed")
        return 1

    try:
        # Initialize components
        executor = ParallelExecutor(str(project_path))
        metrics = MetricsCollector(str(project_path))

        # Test 1: Parallel Analysis
        print("\n🔍 Test 1: Parallel Analysis")
        print("   Running 5 agents simultaneously...")

        exec_id = metrics.start_execution(
            "parallel_analysis", "orchestrator", "analysis", parallel=True
        )

        analysis_results = await executor.execute_parallel_analysis(
            "Test SubForge parallel capabilities"
        )

        metrics.end_execution(exec_id, "completed")
        print(
            f"   ✅ Completed with {len(analysis_results.get('findings', {}))} agent reports"
        )

        # Test 2: Parallel Research
        print("\n🔬 Test 2: Parallel Research")
        print("   Running 9 parallel searches (3 topics × 3 sources)...")

        exec_id = metrics.start_execution(
            "parallel_research", "orchestrator", "research", parallel=True
        )

        research_topics = ["agent patterns", "parallel execution", "context management"]
        research_results = await executor.execute_parallel_research(research_topics)

        metrics.end_execution(exec_id, "completed")
        print(
            f"   ✅ Completed with {len(research_results.get('best_practices', []))} practices found"
        )

        # Show performance report
        print("\n" + metrics.get_performance_report())

        # Save metrics
        final_metrics = metrics.save_metrics()
        print(
            f"\n📁 Metrics saved to: .subforge/metrics/{metrics.current_session['session_id']}.json"
        )

        efficiency = final_metrics.get("efficiency_score", 0)
        if efficiency >= 80:
            print("\n🏆 Excellent parallel performance!")
        elif efficiency >= 60:
            print("\n👍 Good parallel performance")
        else:
            print("\n⚠️  Parallel performance needs optimization")

        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        if hasattr(args, "verbose") and args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def display_analysis_results(profile):
    """Display project analysis results"""
    print_section("📊 Project Analysis")

    print(f"Project Name:     {profile.name}")
    print(f"Architecture:     {profile.architecture_pattern.value.title()}")
    print(f"Complexity:       {profile.complexity.value.title()}")
    print(f"Languages:        {', '.join(profile.technology_stack.languages)}")
    print(
        f"Frameworks:       {', '.join(profile.technology_stack.frameworks) or 'None detected'}"
    )
    print(
        f"Databases:        {', '.join(profile.technology_stack.databases) or 'None detected'}"
    )
    print(f"Files:            {profile.file_count:,}")
    print(f"Lines of Code:    {profile.lines_of_code:,}")
    print(f"Team Size Est.:   {profile.team_size_estimate}")


def display_recommended_setup(profile):
    """Display recommended setup"""
    print_section("🎯 Recommended Setup")

    if profile.recommended_subagents:
        print("Recommended Subagents:")
        for template in profile.recommended_subagents:
            print(f"  • {template}")

    if profile.integration_requirements:
        print("\nIntegration Requirements:")
        for req in profile.integration_requirements:
            print(f"  • {req}")


def display_workflow_results(context):
    """Display workflow execution results"""
    print_section("🎉 SubForge Setup Complete!")

    print(f"Project:             {Path(context.project_path).name}")
    print(f"Workflow ID:         {context.project_id}")
    print(
        f"Generated Subagents: {len(context.template_selections.get('selected_templates', []))}"
    )
    print(f"Configuration:       {context.communication_dir}")

    if context.template_selections.get("selected_templates"):
        print("\n🤖 Generated Subagents:")
        for template in context.template_selections["selected_templates"]:
            print(f"  • {template}")

    print("\n🚀 Next Steps:")
    print("1. Run 'subforge validate' to test your configuration")
    print("2. Use '@<subagent-name>' in Claude Code to invoke subagents")
    print("3. Check 'subforge status' for team overview")
    print("4. Visit your project's '.claude/' directory for generated files")


def extract_template_description(template_file: Path) -> str:
    """Extract description from template file"""
    try:
        content = template_file.read_text()
        lines = content.split("\n")

        # Look for description section
        for i, line in enumerate(lines):
            if line.startswith("## Description"):
                if i + 1 < len(lines):
                    desc = lines[i + 1].strip()
                    # Truncate if too long
                    if len(desc) > 60:
                        desc = desc[:57] + "..."
                    return desc

        return "No description available"

    except Exception:
        return "Error reading template"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="subforge",
        description="🚀 SubForge - Forge your perfect Claude Code development team",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize SubForge for your project"
    )
    init_parser.add_argument(
        "project_path",
        nargs="?",
        help="Path to your project (default: current directory)",
    )
    init_parser.add_argument("--request", "-r", help="What you want to accomplish")
    init_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    init_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze your project structure"
    )
    analyze_parser.add_argument("project_path", nargs="?", help="Path to your project")
    analyze_parser.add_argument("--output", "-o", help="Save analysis to file")
    analyze_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    analyze_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show current SubForge status")
    status_parser.add_argument("project_path", nargs="?", help="Path to your project")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate your SubForge configuration"
    )
    validate_parser.add_argument("project_path", nargs="?", help="Path to your project")
    validate_parser.add_argument(
        "--fix", action="store_true", help="Automatically fix issues"
    )

    # Update command
    update_parser = subparsers.add_parser(
        "update", help="Update/regenerate subagents for current project context"
    )
    update_parser.add_argument(
        "project_path",
        nargs="?",
        help="Path to your project (default: current directory)",
    )
    update_parser.add_argument(
        "--force", action="store_true", help="Force regeneration of all agents"
    )
    update_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Deploy-commands command
    deploy_commands_parser = subparsers.add_parser(
        "deploy-commands", help="Deploy SubForge commands to project"
    )
    deploy_commands_parser.add_argument(
        "project_path",
        nargs="?",
        help="Path to your project (default: current directory)",
    )

    # Templates command
    subparsers.add_parser("templates", help="List available subagent templates")

    # Version command
    subparsers.add_parser("version", help="Show version information")

    # Test-parallel command
    test_parallel_parser = subparsers.add_parser(
        "test-parallel", help="Test parallel execution capabilities"
    )
    test_parallel_parser.add_argument(
        "project_path",
        nargs="?",
        help="Path to your project (default: current directory)",
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate command
    try:
        if args.command == "init":
            return asyncio.run(cmd_init(args))
        elif args.command == "analyze":
            return asyncio.run(cmd_analyze(args))
        elif args.command == "status":
            return cmd_status(args)
        elif args.command == "update":
            return asyncio.run(cmd_update(args))
        elif args.command == "validate":
            return cmd_validate(args)
        elif args.command == "deploy-commands":
            return cmd_deploy_commands(args)
        elif args.command == "templates":
            return cmd_templates(args)
        elif args.command == "version":
            return cmd_version(args)
        elif args.command == "test-parallel":
            return asyncio.run(cmd_test_parallel(args))
        else:
            print(f"Unknown command: {args.command}")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
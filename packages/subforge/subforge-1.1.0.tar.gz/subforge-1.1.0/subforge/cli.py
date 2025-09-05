#!/usr/bin/env python3
"""
SubForge CLI - Command Line Interface
Beautiful, powerful CLI for the SubForge subagent factory
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.tree import Tree

# Import SubForge core modules
try:
    from .core.project_analyzer import ProjectAnalyzer
    from .core.workflow_orchestrator import WorkflowOrchestrator
except ImportError:
    # Handle running from different directories
    sys.path.append(str(Path(__file__).parent))
    from core.project_analyzer import ProjectAnalyzer
    from core.workflow_orchestrator import WorkflowOrchestrator

# Initialize Typer app and Rich console
app = typer.Typer(
    name="subforge",
    help="🚀 SubForge - Forge your perfect Claude Code development team",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()

# ASCII Art Banner
SUBFORGE_BANNER = r"""
[bold blue]
 ____        _     _____
/ ___| _   _| |__ |  ___|__  _ __ __ _  ___
\___ \| | | | '_ \| |_ / _ \| '__/ _` |/ _ \
 ___) | |_| | |_) |  _| (_) | | | (_| |  __/
|____/ \__,_|_.__/|_|  \___/|_|  \__, |\___|
                                 |___/
[/bold blue]
[italic]Forge your perfect Claude Code development team[/italic]
"""


def print_banner():
    """Print the SubForge banner"""
    console.print(SUBFORGE_BANNER)


@app.command()
def init(
    project_path: Optional[Path] = typer.Argument(
        None, help="Path to your project (default: current directory)"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--non-interactive", "-i", help="Run in interactive mode"
    ),
    templates: Optional[List[str]] = typer.Option(
        None, "--template", "-t", help="Specific templates to use"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Initialize SubForge for your project

    Analyzes your project and sets up the perfect Claude Code subagent team.
    """
    if not project_path:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path).resolve()

    if not project_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Project path does not exist: {project_path}"
        )
        raise typer.Exit(1)

    print_banner()
    console.print(f"[bold]Initializing SubForge for:[/bold] {project_path.name}")
    console.print(f"[dim]Path: {project_path}[/dim]\n")

    # Interactive mode - gather requirements
    user_request = "Set up development environment with best practices"
    if interactive:
        user_request = Prompt.ask(
            "[bold]What would you like to accomplish with this project?[/bold]",
            default=user_request,
        )

        # Show analysis preview
        if not dry_run:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Analyzing project structure...", total=None)
                time.sleep(1)  # Visual pause

    # Run the workflow
    try:
        asyncio.run(
            _run_init_workflow(project_path, user_request, templates, dry_run, verbose)
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


async def _run_init_workflow(
    project_path: Path,
    user_request: str,
    templates: Optional[List[str]],
    dry_run: bool,
    verbose: bool,
):
    """Run the initialization workflow"""

    orchestrator = WorkflowOrchestrator()

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

        # Just run analysis
        analyzer = ProjectAnalyzer()
        profile = await analyzer.analyze_project(str(project_path))

        _display_analysis_results(profile)
        _display_recommended_setup(profile, templates)
        return

    # Run full workflow
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        workflow_task = progress.add_task("Executing SubForge workflow...", total=None)

        try:
            context = await orchestrator.execute_workflow(
                user_request, str(project_path)
            )

            progress.update(
                workflow_task,
                description="✅ Workflow completed!",
                total=1,
                completed=1,
            )

            # Display results
            _display_workflow_results(context)

        except Exception as e:
            progress.update(workflow_task, description=f"❌ Workflow failed: {e}")
            raise


def _display_analysis_results(profile):
    """Display project analysis results"""

    # Create analysis table
    table = Table(
        title="📊 Project Analysis", show_header=True, header_style="bold blue"
    )
    table.add_column("Attribute", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Project Name", profile.name)
    table.add_row("Architecture", profile.architecture_pattern.value.title())
    table.add_row("Complexity", profile.complexity.value.title())
    table.add_row("Languages", ", ".join(profile.technology_stack.languages))
    table.add_row(
        "Frameworks", ", ".join(profile.technology_stack.frameworks) or "None detected"
    )
    table.add_row(
        "Databases", ", ".join(profile.technology_stack.databases) or "None detected"
    )
    table.add_row("Files", f"{profile.file_count:,}")
    table.add_row("Lines of Code", f"{profile.lines_of_code:,}")
    table.add_row("Team Size Est.", str(profile.team_size_estimate))

    console.print(table)


def _display_recommended_setup(profile, explicit_templates):
    """Display recommended setup"""

    templates = explicit_templates or profile.recommended_subagents

    panel_content = ""
    if templates:
        panel_content += "[bold]Recommended Subagents:[/bold]\n"
        for template in templates:
            panel_content += f"• [cyan]{template}[/cyan]\n"

    if profile.integration_requirements:
        panel_content += "\n[bold]Integration Requirements:[/bold]\n"
        for req in profile.integration_requirements:
            panel_content += f"• [yellow]{req}[/yellow]\n"

    console.print(
        Panel(panel_content.strip(), title="🎯 Recommended Setup", border_style="green")
    )


def _display_workflow_results(context):
    """Display workflow execution results"""

    console.print("\n" + "=" * 60)
    console.print("[bold green]🎉 SubForge Setup Complete![/bold green]")
    console.print("=" * 60)

    # Summary panel
    summary = f"""[bold]Project:[/bold] {Path(context.project_path).name}
[bold]Workflow ID:[/bold] {context.project_id}
[bold]Generated Subagents:[/bold] {len(context.template_selections.get('selected_templates', []))}

[bold]Configuration Location:[/bold] {context.communication_dir}"""

    console.print(Panel(summary, title="📋 Summary", border_style="blue"))

    # Show generated subagents
    if context.template_selections.get("selected_templates"):
        console.print("\n[bold]🤖 Generated Subagents:[/bold]")
        for template in context.template_selections["selected_templates"]:
            console.print(f"  • [cyan]{template}[/cyan]")

    # Show next steps
    next_steps = """1. Run [cyan]`subforge validate`[/cyan] to test your configuration
2. Use [cyan]`@<subagent-name>`[/cyan] in Claude Code to invoke subagents
3. Check [cyan]`subforge status`[/cyan] for team overview
4. Visit your project's [cyan]`.claude/`[/cyan] directory for generated files"""

    console.print(Panel(next_steps, title="🚀 Next Steps", border_style="green"))


@app.command()
def analyze(
    project_path: Optional[Path] = typer.Argument(None, help="Path to your project"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save analysis to file"
    ),
    json_format: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """
    🔍 Analyze your project structure and technology stack

    Deep analysis of project characteristics to understand optimal subagent team.
    """
    if not project_path:
        project_path = Path.cwd()

    console.print("[bold]🔍 Analyzing project...[/bold]")

    try:
        analyzer = ProjectAnalyzer()
        profile = asyncio.run(analyzer.analyze_project(str(project_path)))

        if json_format:
            result = json.dumps(profile.to_dict(), indent=2)
            if output:
                output.write_text(result)
                console.print(f"[green]Analysis saved to:[/green] {output}")
            else:
                console.print(result)
        else:
            _display_analysis_results(profile)
            _display_recommended_setup(profile, None)

            if output:
                asyncio.run(analyzer.save_analysis(profile, str(output)))
                console.print(f"[green]Analysis saved to:[/green] {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def status(
    project_path: Optional[Path] = typer.Argument(None, help="Path to your project")
):
    """
    📊 Show current SubForge status for your project

    Displays information about configured subagents and recent activity.
    """
    if not project_path:
        project_path = Path.cwd()

    subforge_dir = project_path / ".subforge"
    claude_dir = project_path / ".claude"

    console.print(f"[bold]📊 SubForge Status for:[/bold] {project_path.name}\n")

    # Check for SubForge configuration
    if not subforge_dir.exists():
        console.print(
            "[yellow]No SubForge configuration found. Run `subforge init` to get started.[/yellow]"
        )
        return

    # Find latest workflow
    workflow_dirs = sorted(
        subforge_dir.glob("subforge_*"), key=lambda x: x.stat().st_mtime, reverse=True
    )

    if not workflow_dirs:
        console.print("[yellow]No workflow executions found.[/yellow]")
        return

    latest_workflow = workflow_dirs[0]

    # Load workflow context
    context_file = latest_workflow / "workflow_context.json"
    if context_file.exists():
        try:
            with open(context_file) as f:
                context_data = json.load(f)

            # Display status
            table = Table(
                title="Current Configuration",
                show_header=True,
                header_style="bold blue",
            )
            table.add_column("Attribute", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Workflow ID", context_data["project_id"])
            table.add_row(
                "Last Updated",
                context_data.get("phase_results", {})
                .get("deployment", {})
                .get("timestamp", "Unknown"),
            )

            if context_data.get("template_selections", {}).get("selected_templates"):
                templates = context_data["template_selections"]["selected_templates"]
                table.add_row("Active Subagents", f"{len(templates)} configured")

                for template in templates:
                    table.add_row("", f"• {template}")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error loading workflow context: {e}[/red]")

    # Check Claude Code integration
    if claude_dir.exists():
        console.print("\n[green]✅ Claude Code integration detected[/green]")

        # Show .claude directory structure
        tree = Tree("📁 .claude/")
        if (claude_dir / "agents").exists():
            agents_branch = tree.add("📁 agents/")
            for agent_file in (claude_dir / "agents").glob("*.md"):
                agents_branch.add(f"🤖 {agent_file.stem}")

        console.print(tree)
    else:
        console.print("\n[yellow]⚠️  No Claude Code integration found[/yellow]")
        console.print("   Run `subforge deploy` to set up Claude Code configuration")


@app.command()
def validate(
    project_path: Optional[Path] = typer.Argument(None, help="Path to your project"),
    fix: bool = typer.Option(
        False, "--fix", help="Automatically fix code issues where possible"
    ),
):
    """
    ✅ Validate your SubForge configuration

    Checks that all subagents and configurations are working correctly.
    
    When used with --fix, automatically applies common code improvements:
    • Sorts imports using isort (compatible with black)
    • Formats code with black (PEP 8 compliance)
    • Removes unused imports and variables with autoflake
    • Adds basic type hints for obvious cases (-> None)
    
    Example:
        subforge validate --fix
        
    Note: Requires black, isort, and autoflake to be installed for full functionality.
    Install with: pip install black isort autoflake
    """
    if not project_path:
        project_path = Path.cwd()

    console.print("[bold]✅ Validating SubForge configuration...[/bold]\n")

    validation_results = []

    # Check SubForge directory
    subforge_dir = project_path / ".subforge"
    if subforge_dir.exists():
        validation_results.append(("SubForge directory", "✅ Found", "green"))
    else:
        validation_results.append(("SubForge directory", "❌ Missing", "red"))
        return

    # Check for workflows
    workflow_dirs = list(subforge_dir.glob("subforge_*"))
    if workflow_dirs:
        validation_results.append(
            ("Workflow executions", f"✅ {len(workflow_dirs)} found", "green")
        )
    else:
        validation_results.append(("Workflow executions", "❌ None found", "red"))

    # Check Claude Code integration
    claude_dir = project_path / ".claude"
    if claude_dir.exists():
        validation_results.append(("Claude Code directory", "✅ Found", "green"))

        # Check for CLAUDE.md
        claude_md = claude_dir / "CLAUDE.md"
        if claude_md.exists():
            validation_results.append(("CLAUDE.md", "✅ Configured", "green"))
        else:
            validation_results.append(("CLAUDE.md", "❌ Missing", "red"))

        # Check for agents
        agents_dir = claude_dir / "agents"
        if agents_dir.exists():
            agent_count = len(list(agents_dir.glob("*.md")))
            validation_results.append(
                ("Subagent files", f"✅ {agent_count} found", "green")
            )
        else:
            validation_results.append(
                ("Subagent files", "❌ No agents directory", "red")
            )
    else:
        validation_results.append(("Claude Code directory", "❌ Missing", "red"))

    # Display results
    table = Table(
        title="Validation Results", show_header=True, header_style="bold blue"
    )
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")

    for component, status, color in validation_results:
        table.add_row(component, f"[{color}]{status}[/{color}]")

    console.print(table)

    # Summary
    passed = sum(1 for _, status, _ in validation_results if "✅" in status)
    total = len(validation_results)

    if passed == total:
        console.print(
            f"\n[bold green]🎉 All checks passed! ({passed}/{total})[/bold green]"
        )
    else:
        console.print(
            f"\n[bold yellow]⚠️  Some issues found ({passed}/{total} passed)[/bold yellow]"
        )

        if fix:
            console.print("\n[cyan]Running automatic fixes...[/cyan]")
            _run_automatic_fixes(project_path)


@app.command()
def templates():
    """
    🎨 List available subagent templates

    Shows all templates that can be used for subagent generation.
    """
    templates_dir = Path(__file__).parent / "templates"

    if not templates_dir.exists():
        console.print("[red]Templates directory not found[/red]")
        return

    console.print("[bold]🎨 Available Subagent Templates[/bold]\n")

    template_files = list(templates_dir.glob("*.md"))

    if not template_files:
        console.print("[yellow]No templates found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Template", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for template_file in sorted(template_files):
        name = template_file.stem
        description = _extract_template_description(template_file)
        table.add_row(name, description)

    console.print(table)

    console.print(
        f"\n[dim]Found {len(template_files)} templates in {templates_dir}[/dim]"
    )


def _extract_template_description(template_file: Path) -> str:
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
                    if len(desc) > 80:
                        desc = desc[:77] + "..."
                    return desc

        return "No description available"

    except Exception:
        return "Error reading template"


def _run_automatic_fixes(project_path: Path):
    """Run automatic fixes for common code issues"""

    # Find Python files in the project
    python_files = []
    for ext in ["*.py"]:
        python_files.extend(project_path.rglob(ext))

    # Filter out common directories to ignore
    ignored_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
    }
    python_files = [
        f for f in python_files if not any(part in ignored_dirs for part in f.parts)
    ]

    if not python_files:
        console.print("[yellow]No Python files found to fix[/yellow]")
        return

    console.print(f"[cyan]Found {len(python_files)} Python files to process...[/cyan]")

    fixes_applied = 0

    # Progress bar for fixes
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # 1. Fix import sorting with isort
        task = progress.add_task("Sorting imports...", total=None)
        if _run_isort_fix(python_files, project_path):
            fixes_applied += 1
            progress.update(task, description="✅ Imports sorted")
        else:
            progress.update(
                task, description="⚠️  Import sorting skipped (isort not available)"
            )

        # 2. Fix code formatting with black
        task = progress.add_task("Formatting code...", total=None)
        if _run_black_fix(python_files, project_path):
            fixes_applied += 1
            progress.update(task, description="✅ Code formatted")
        else:
            progress.update(
                task, description="⚠️  Code formatting skipped (black not available)"
            )

        # 3. Remove unused imports with autoflake
        task = progress.add_task("Removing unused imports...", total=None)
        if _run_autoflake_fix(python_files, project_path):
            fixes_applied += 1
            progress.update(task, description="✅ Unused imports removed")
        else:
            progress.update(
                task,
                description="⚠️  Unused import removal skipped (autoflake not available)",
            )

        # 4. Add basic type hints where missing
        task = progress.add_task("Adding type hints...", total=None)
        type_fixes = _add_basic_type_hints(python_files)
        if type_fixes > 0:
            fixes_applied += 1
            progress.update(task, description=f"✅ Added {type_fixes} basic type hints")
        else:
            progress.update(
                task, description="ℹ️  No obvious type hint additions needed"
            )

    # Summary
    if fixes_applied > 0:
        console.print(
            f"\n[bold green]✅ Applied {fixes_applied} categories of automatic fixes![/bold green]"
        )
        console.print(
            "[dim]Run your tests to ensure everything still works correctly.[/dim]"
        )
    else:
        console.print(
            "\n[yellow]No fixes could be applied. Consider installing: black, isort, autoflake[/yellow]"
        )
        console.print("[dim]pip install black isort autoflake[/dim]")


def _run_isort_fix(python_files: List[Path], project_path: Path) -> bool:
    """Fix import sorting with isort"""
    try:
        # Check if isort is available
        subprocess.run(["isort", "--version"], capture_output=True, check=True)

        # Run isort on all Python files
        cmd = ["isort", "--profile", "black", str(project_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _run_black_fix(python_files: List[Path], project_path: Path) -> bool:
    """Fix code formatting with black"""
    try:
        # Check if black is available
        subprocess.run(["black", "--version"], capture_output=True, check=True)

        # Run black on all Python files
        cmd = ["black", "--line-length", "88", str(project_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _run_autoflake_fix(python_files: List[Path], project_path: Path) -> bool:
    """Remove unused imports with autoflake"""
    try:
        # Check if autoflake is available
        subprocess.run(["autoflake", "--version"], capture_output=True, check=True)

        # Run autoflake on all Python files
        for file_path in python_files:
            cmd = [
                "autoflake",
                "--in-place",
                "--remove-unused-variables",
                "--remove-all-unused-imports",
                str(file_path),
            ]
            subprocess.run(cmd, capture_output=True)

        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _add_basic_type_hints(python_files: List[Path]) -> int:
    """Add basic type hints where obviously missing"""
    fixes_count = 0

    for file_path in python_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Add basic type hints for simple cases
            lines = content.splitlines()
            modified_lines = []

            for line in lines:
                stripped = line.strip()

                # Add return type hints for functions that return None
                if (
                    stripped.startswith("def ")
                    and "-> " not in line
                    and not stripped.endswith(":")
                    and ":" in line
                ):

                    # Check if it's a simple function without complex parameters
                    if (
                        "return None" in content
                        or "return" not in content.split(stripped)[1].split("def")[0]
                        if "def" in content.split(stripped)[1]
                        else False
                    ):

                        line = line.replace(":", " -> None:")
                        fixes_count += 1

                # Add typing import if type hints are used but import is missing
                elif stripped.startswith("from typing import") or stripped.startswith(
                    "import typing"
                ):
                    # Already has typing imports
                    pass

                modified_lines.append(line)

            new_content = "\n".join(modified_lines)

            # Only write if content changed
            if new_content != original_content:
                # Add typing import at the top if we added type hints and it's missing
                if (
                    "-> " in new_content
                    and "from typing import" not in new_content
                    and "import typing" not in new_content
                ):
                    # Find the right place to insert the import
                    import_lines = []
                    other_lines = []
                    in_imports = True

                    for line in modified_lines:
                        if in_imports and (
                            line.startswith("import ") or line.startswith("from ")
                        ):
                            import_lines.append(line)
                        elif line.strip() == "":
                            if in_imports:
                                import_lines.append(line)
                            else:
                                other_lines.append(line)
                        else:
                            in_imports = False
                            other_lines.append(line)

                    if import_lines:
                        import_lines.append(
                            "from typing import Optional, List, Dict, Any"
                        )
                        new_content = "\n".join(import_lines + other_lines)

                file_path.write_text(new_content, encoding="utf-8")

        except Exception:
            # Silently skip files that can't be processed
            continue

    return fixes_count


@app.command()
def version():
    """
    Show SubForge version information
    """
    console.print("[bold blue]SubForge v1.0.0-alpha[/bold blue]")
    console.print("🚀 Forge your perfect Claude Code development team")
    console.print("\nDeveloped with ❤️ for the Claude Code community")


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
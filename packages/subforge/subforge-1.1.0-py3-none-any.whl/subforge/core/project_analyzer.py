#!/usr/bin/env python3
"""
SubForge Project Analyzer - Core Engine
Intelligently analyzes projects to determine optimal subagent configurations
"""

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class ProjectComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class ArchitecturePattern(Enum):
    MONOLITHIC = "monolithic"
    MICROSERVICES = "microservices"
    JAMSTACK = "jamstack"
    FULLSTACK = "fullstack"
    API_FIRST = "api_first"
    SERVERLESS = "serverless"


@dataclass
class TechnologyStack:
    """Detected technology stack information"""

    languages: Set[str]
    frameworks: Set[str]
    databases: Set[str]
    tools: Set[str]
    package_managers: Set[str]

    def to_dict(self) -> Dict:
        return {
            "languages": list(self.languages),
            "frameworks": list(self.frameworks),
            "databases": list(self.databases),
            "tools": list(self.tools),
            "package_managers": list(self.package_managers),
        }


@dataclass
class ProjectProfile:
    """Complete project analysis profile"""

    name: str
    path: str
    technology_stack: TechnologyStack
    architecture_pattern: ArchitecturePattern
    complexity: ProjectComplexity
    team_size_estimate: int
    file_count: int
    lines_of_code: int
    has_tests: bool
    has_ci_cd: bool
    has_docker: bool
    has_docs: bool
    recommended_subagents: List[str]
    integration_requirements: List[str]

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "technology_stack": self.technology_stack.to_dict(),
            "architecture_pattern": self.architecture_pattern.value,
            "complexity": self.complexity.value,
            "recommended_subagents": self.recommended_subagents,
            "integration_requirements": self.integration_requirements,
        }


class ProjectAnalyzer:
    """
    Core project analysis engine that intelligently determines project characteristics
    and optimal subagent team configuration
    """

    def __init__(self):
        self.language_extensions = {
            "python": {".py", ".pyx", ".pyi"},
            "javascript": {".js", ".jsx", ".mjs"},
            "typescript": {".ts", ".tsx"},
            "java": {".java"},
            "csharp": {".cs"},
            "go": {".go"},
            "rust": {".rs"},
            "php": {".php"},
            "ruby": {".rb"},
            "cpp": {".cpp", ".cc", ".cxx", ".h", ".hpp"},
            "html": {".html", ".htm"},
            "css": {".css", ".scss", ".sass", ".less"},
            "sql": {".sql"},
            "shell": {".sh", ".bash", ".zsh"},
            "yaml": {".yaml", ".yml"},
            "json": {".json"},
            "markdown": {".md", ".mdx"},
        }

        self.framework_indicators = {
            # Frontend frameworks
            "react": [
                "package.json:react",
                "src/App.jsx",
                "src/App.tsx",
                "public/index.html",
            ],
            "vue": ["package.json:vue", "src/App.vue", "vue.config.js"],
            "angular": [
                "package.json:@angular",
                "angular.json",
                "src/app/app.module.ts",
            ],
            "svelte": ["package.json:svelte", "src/App.svelte"],
            "nextjs": ["package.json:next", "next.config.js", "pages/", "app/"],
            "nuxt": ["package.json:nuxt", "nuxt.config.js"],
            "gatsby": ["package.json:gatsby", "gatsby-config.js"],
            # Backend frameworks
            "express": ["package.json:express", "app.js", "server.js"],
            "fastapi": ["requirements.txt:fastapi", "main.py", "app/main.py"],
            "django": ["requirements.txt:django", "manage.py", "settings.py"],
            "flask": ["requirements.txt:flask", "app.py", "run.py"],
            "rails": ["Gemfile:rails", "config/application.rb"],
            "spring": ["pom.xml:spring", "src/main/java"],
            "dotnet": ["*.csproj", "Program.cs"],
            # Mobile
            "react-native": ["package.json:react-native", "App.js", "android/", "ios/"],
            "flutter": ["pubspec.yaml:flutter", "lib/main.dart"],
            # Database
            "mongodb": ["package.json:mongodb", "requirements.txt:pymongo"],
            "postgresql": ["package.json:pg", "requirements.txt:psycopg2"],
            "mysql": ["package.json:mysql", "requirements.txt:mysql"],
            "redis": ["package.json:redis", "requirements.txt:redis"],
            # Tools
            "docker": ["Dockerfile", "docker-compose.yml"],
            "kubernetes": ["*.yaml:kind:", "k8s/", "kustomization.yaml"],
            "terraform": ["*.tf", "terraform/"],
            "webpack": ["webpack.config.js", "package.json:webpack"],
            "vite": ["vite.config.js", "package.json:vite"],
            "rollup": ["rollup.config.js", "package.json:rollup"],
        }

        self.subagent_templates = {
            "frontend-developer": {
                "triggers": ["react", "vue", "angular", "svelte", "html", "css"],
                "description": "UI/UX specialist for client-side development",
            },
            "backend-developer": {
                "triggers": [
                    "express",
                    "fastapi",
                    "django",
                    "flask",
                    "spring",
                    "rails",
                ],
                "description": "Server-side logic and API development",
            },
            "devops-engineer": {
                "triggers": ["docker", "kubernetes", "terraform", "ci_cd"],
                "description": "Infrastructure, deployment, and monitoring",
            },
            "mobile-developer": {
                "triggers": ["react-native", "flutter"],
                "description": "Mobile application development",
            },
            "database-specialist": {
                "triggers": ["mongodb", "postgresql", "mysql", "redis"],
                "description": "Database design and optimization",
            },
            "security-auditor": {
                "triggers": ["authentication", "api_security", "data_protection"],
                "description": "Security assessment and compliance",
            },
            "code-reviewer": {
                "triggers": ["always"],  # Always recommended
                "description": "Code quality and best practices",
            },
            "test-engineer": {
                "triggers": ["has_tests", "testing_framework"],
                "description": "Testing strategy and automation",
            },
            "performance-optimizer": {
                "triggers": ["complex", "enterprise", "large_codebase"],
                "description": "Performance analysis and optimization",
            },
        }

    async def analyze_project(self, project_path: str) -> ProjectProfile:
        """
        Main analysis method that orchestrates all analysis phases
        """
        path = Path(project_path).resolve()

        if not path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")

        print(f"🔍 Analyzing project: {path.name}")

        # Phase 1: File system analysis
        file_analysis = await self._analyze_file_system(path)

        # Phase 2: Technology detection
        tech_stack = await self._detect_technology_stack(path, file_analysis)

        # Phase 3: Architecture pattern recognition
        architecture = await self._detect_architecture_pattern(
            path, tech_stack, file_analysis
        )

        # Phase 4: Complexity assessment
        complexity = await self._assess_complexity(file_analysis, tech_stack)

        # Phase 5: Integration requirements
        integrations = await self._detect_integrations(path, tech_stack)

        # Phase 6: Subagent recommendations
        recommended_agents = await self._recommend_subagents(
            tech_stack, architecture, complexity
        )

        profile = ProjectProfile(
            name=path.name,
            path=str(path),
            technology_stack=tech_stack,
            architecture_pattern=architecture,
            complexity=complexity,
            team_size_estimate=self._estimate_team_size(
                complexity, len(recommended_agents)
            ),
            file_count=file_analysis["total_files"],
            lines_of_code=file_analysis["total_lines"],
            has_tests=file_analysis["has_tests"],
            has_ci_cd=file_analysis["has_ci_cd"],
            has_docker=file_analysis["has_docker"],
            has_docs=file_analysis["has_docs"],
            recommended_subagents=recommended_agents,
            integration_requirements=integrations,
        )

        print(f"✅ Analysis complete: {len(recommended_agents)} subagents recommended")
        return profile

    async def _analyze_file_system(self, path: Path) -> Dict:
        """Analyze file system structure and gather basic metrics"""
        print("  📊 Analyzing file system structure...")

        analysis = {
            "total_files": 0,
            "total_lines": 0,
            "file_types": {},
            "directory_structure": [],
            "has_tests": False,
            "has_ci_cd": False,
            "has_docker": False,
            "has_docs": False,
            "markdown_files": 0,
            "test_files": 0,
            "config_files": 0,
            "package_files": [],
            "detected_patterns": [],
        }

        # Ignore common directories
        ignore_dirs = {
            ".git",
            ".svn",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".next",
            ".nuxt",
            "target",
            "bin",
            "obj",
        }

        for root, dirs, files in os.walk(path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            root_path = Path(root)
            relative_root = root_path.relative_to(path)

            if str(relative_root) != ".":
                analysis["directory_structure"].append(str(relative_root))

            for file in files:
                file_path = root_path / file
                analysis["total_files"] += 1

                # Get file extension
                ext = file_path.suffix.lower()
                analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1

                # Count specific file types
                if ext == ".md":
                    analysis["markdown_files"] += 1

                # Check for package files
                if file.lower() in [
                    "package.json",
                    "requirements.txt",
                    "gemfile",
                    "go.mod",
                    "cargo.toml",
                    "composer.json",
                ]:
                    analysis["package_files"].append(str(file_path.relative_to(path)))

                # Check for Docker
                if file.lower() in [
                    "dockerfile",
                    "docker-compose.yml",
                    ".dockerignore",
                ]:
                    analysis["has_docker"] = True
                    analysis["detected_patterns"].append("containerization")

                # Check for tests (more comprehensive)
                if (
                    "test" in file.lower()
                    or "spec" in file.lower()
                    or file.lower().startswith("test_")
                    or file.lower().endswith("_test.py")
                    or file.lower().endswith(".test.js")
                    or file.lower().endswith(".spec.js")
                ):
                    analysis["has_tests"] = True
                    analysis["test_files"] += 1
                    analysis["detected_patterns"].append("testing")

                # Check for CI/CD
                if file.lower() in [
                    ".gitlab-ci.yml",
                    "jenkinsfile",
                    ".travis.yml",
                    "azure-pipelines.yml",
                ]:
                    analysis["has_ci_cd"] = True
                    analysis["detected_patterns"].append("ci_cd")

                # Check for GitHub Actions
                if root_path.name == ".github" and file.endswith(".yml"):
                    analysis["has_ci_cd"] = True
                    analysis["detected_patterns"].append("github_actions")

                # Check for configuration files
                if file.lower() in [
                    "config.py",
                    "settings.py",
                    ".env",
                    "app.config",
                    "web.config",
                ]:
                    analysis["config_files"] += 1

                # Check for docs directory
                if (
                    "docs" in str(relative_root).lower()
                    or "documentation" in str(relative_root).lower()
                ):
                    analysis["has_docs"] = True
                    analysis["detected_patterns"].append("documentation")

                if file.lower() in ["readme.md", "docs", "documentation"]:
                    analysis["has_docs"] = True

                # Count lines for text files
                if ext in {
                    ".py",
                    ".js",
                    ".ts",
                    ".jsx",
                    ".tsx",
                    ".java",
                    ".cs",
                    ".go",
                    ".rs",
                    ".php",
                    ".rb",
                }:
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            analysis["total_lines"] += sum(1 for _ in f)
                    except Exception:
                        pass

        return analysis

    async def _detect_technology_stack(
        self, path: Path, file_analysis: Dict
    ) -> TechnologyStack:
        """Detect languages, frameworks, and tools used in the project"""
        print("  🔧 Detecting technology stack...")

        languages = set()
        frameworks = set()
        databases = set()
        tools = set()
        package_managers = set()

        # Detect languages from file extensions
        for ext, count in file_analysis["file_types"].items():
            for lang, exts in self.language_extensions.items():
                if ext in exts and count > 0:
                    languages.add(lang)

        # Detect frameworks and tools
        for package_file in file_analysis["package_files"]:
            package_path = path / package_file

            if package_file.endswith("package.json"):
                package_managers.add("npm")
                frameworks.update(await self._analyze_package_json(package_path))

            elif package_file.endswith("requirements.txt"):
                package_managers.add("pip")
                frameworks.update(await self._analyze_requirements_txt(package_path))

            elif package_file.endswith("Gemfile"):
                package_managers.add("bundler")
                frameworks.update(await self._analyze_gemfile(package_path))

            elif package_file.endswith("go.mod"):
                package_managers.add("go-modules")
                frameworks.update(await self._analyze_go_mod(package_path))

            elif package_file.endswith("Cargo.toml"):
                package_managers.add("cargo")
                frameworks.update(await self._analyze_cargo_toml(package_path))

        # Detect additional tools from directory structure
        if file_analysis["has_docker"]:
            tools.add("docker")

        if file_analysis["has_ci_cd"]:
            tools.add("ci_cd")

        # Check for specific framework indicators
        for framework, indicators in self.framework_indicators.items():
            if await self._check_framework_indicators(path, indicators):
                if framework in ["mongodb", "postgresql", "mysql", "redis"]:
                    databases.add(framework)
                elif framework in [
                    "docker",
                    "kubernetes",
                    "terraform",
                    "webpack",
                    "vite",
                    "rollup",
                ]:
                    tools.add(framework)
                else:
                    frameworks.add(framework)

        return TechnologyStack(
            languages=languages,
            frameworks=frameworks,
            databases=databases,
            tools=tools,
            package_managers=package_managers,
        )

    async def _analyze_package_json(self, package_path: Path) -> Set[str]:
        """Analyze package.json for JavaScript/Node.js frameworks"""
        frameworks = set()

        try:
            with open(package_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)

            dependencies = {
                **package_data.get("dependencies", {}),
                **package_data.get("devDependencies", {}),
            }

            for dep in dependencies:
                if dep in ["react", "@types/react"]:
                    frameworks.add("react")
                elif dep in ["vue", "@vue/cli"]:
                    frameworks.add("vue")
                elif dep.startswith("@angular"):
                    frameworks.add("angular")
                elif dep == "svelte":
                    frameworks.add("svelte")
                elif dep == "next":
                    frameworks.add("nextjs")
                elif dep == "nuxt":
                    frameworks.add("nuxt")
                elif dep == "gatsby":
                    frameworks.add("gatsby")
                elif dep == "express":
                    frameworks.add("express")
                elif dep == "react-native":
                    frameworks.add("react-native")

        except Exception as e:
            print(f"    ⚠️  Could not parse package.json: {e}")

        return frameworks

    async def _analyze_requirements_txt(self, req_path: Path) -> Set[str]:
        """Analyze requirements.txt for Python frameworks"""
        frameworks = set()

        try:
            with open(req_path, "r", encoding="utf-8") as f:
                requirements = f.read().lower()

            if "fastapi" in requirements:
                frameworks.add("fastapi")
            if "django" in requirements:
                frameworks.add("django")
            if "flask" in requirements:
                frameworks.add("flask")
            if "pymongo" in requirements:
                frameworks.add("mongodb")
            if "psycopg2" in requirements or "asyncpg" in requirements:
                frameworks.add("postgresql")
            if "mysql" in requirements or "pymysql" in requirements:
                frameworks.add("mysql")
            if "redis" in requirements:
                frameworks.add("redis")

        except Exception as e:
            print(f"    ⚠️  Could not parse requirements.txt: {e}")

        return frameworks

    async def _analyze_gemfile(self, gemfile_path: Path) -> Set[str]:
        """Analyze Gemfile for Ruby frameworks"""
        frameworks = set()

        try:
            with open(gemfile_path, "r", encoding="utf-8") as f:
                gemfile = f.read().lower()

            if "rails" in gemfile:
                frameworks.add("rails")

        except Exception as e:
            print(f"    ⚠️  Could not parse Gemfile: {e}")

        return frameworks

    async def _analyze_go_mod(self, go_mod_path: Path) -> Set[str]:
        """Analyze go.mod for Go frameworks"""
        frameworks = set()
        # Add Go-specific framework detection logic here
        return frameworks

    async def _analyze_cargo_toml(self, cargo_path: Path) -> Set[str]:
        """Analyze Cargo.toml for Rust frameworks"""
        frameworks = set()
        # Add Rust-specific framework detection logic here
        return frameworks

    async def _check_framework_indicators(
        self, path: Path, indicators: List[str]
    ) -> bool:
        """Check if framework indicators exist in the project"""
        for indicator in indicators:
            if ":" in indicator:
                # Package file check (e.g., "package.json:react")
                parts = indicator.split(":", 1)  # Split only on first colon
                if len(parts) == 2:
                    file_name, dependency = parts
                    file_path = path / file_name
                    if file_path.exists():
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                if dependency in content:
                                    return True
                        except Exception:
                            continue
            else:
                # File or directory check
                check_path = path / indicator
                if check_path.exists():
                    return True

        return False

    async def _detect_architecture_pattern(
        self, path: Path, tech_stack: TechnologyStack, file_analysis: Dict
    ) -> ArchitecturePattern:
        """Detect the overall architecture pattern of the project"""
        print("  🏗️  Detecting architecture pattern...")

        # JAMStack indicators
        if "gatsby" in tech_stack.frameworks or "nextjs" in tech_stack.frameworks:
            return ArchitecturePattern.JAMSTACK

        # Microservices indicators
        microservice_indicators = [
            "docker-compose.yml",
            "kubernetes",
            "terraform",
            len(file_analysis["directory_structure"]) > 10,  # Complex structure
            "api" in str(path).lower() and "service" in str(path).lower(),
        ]

        if sum(1 for indicator in microservice_indicators if indicator) >= 2:
            return ArchitecturePattern.MICROSERVICES

        # API-first indicators
        api_indicators = ["fastapi", "express", "spring", "rails"]
        if any(framework in tech_stack.frameworks for framework in api_indicators):
            if not any(
                frontend in tech_stack.frameworks
                for frontend in ["react", "vue", "angular"]
            ):
                return ArchitecturePattern.API_FIRST

        # Serverless indicators
        serverless_indicators = ["vercel", "netlify", "lambda", "cloudflare-workers"]
        if any(tool in tech_stack.tools for tool in serverless_indicators):
            return ArchitecturePattern.SERVERLESS

        # Full-stack indicators
        has_frontend = any(
            framework in tech_stack.frameworks
            for framework in ["react", "vue", "angular", "svelte"]
        )
        has_backend = any(
            framework in tech_stack.frameworks
            for framework in [
                "express",
                "fastapi",
                "django",
                "flask",
                "rails",
                "spring",
            ]
        )

        if has_frontend and has_backend:
            return ArchitecturePattern.FULLSTACK

        # Default to monolithic
        return ArchitecturePattern.MONOLITHIC

    async def _assess_complexity(
        self, file_analysis: Dict, tech_stack: TechnologyStack
    ) -> ProjectComplexity:
        """Assess the overall complexity of the project"""
        print("  📈 Assessing project complexity...")

        complexity_score = 0

        # File count scoring
        if file_analysis["total_files"] > 1000:
            complexity_score += 3
        elif file_analysis["total_files"] > 500:
            complexity_score += 2
        elif file_analysis["total_files"] > 100:
            complexity_score += 1

        # Lines of code scoring
        if file_analysis["total_lines"] > 100000:
            complexity_score += 3
        elif file_analysis["total_lines"] > 50000:
            complexity_score += 2
        elif file_analysis["total_lines"] > 10000:
            complexity_score += 1

        # Technology diversity scoring
        total_tech = (
            len(tech_stack.languages)
            + len(tech_stack.frameworks)
            + len(tech_stack.databases)
            + len(tech_stack.tools)
        )
        if total_tech > 15:
            complexity_score += 3
        elif total_tech > 10:
            complexity_score += 2
        elif total_tech > 5:
            complexity_score += 1

        # Infrastructure complexity
        if "kubernetes" in tech_stack.tools:
            complexity_score += 2
        if "docker" in tech_stack.tools:
            complexity_score += 1
        if file_analysis["has_ci_cd"]:
            complexity_score += 1

        # Determine complexity level
        if complexity_score >= 8:
            return ProjectComplexity.ENTERPRISE
        elif complexity_score >= 5:
            return ProjectComplexity.COMPLEX
        elif complexity_score >= 2:
            return ProjectComplexity.MEDIUM
        else:
            return ProjectComplexity.SIMPLE

    async def _detect_integrations(
        self, path: Path, tech_stack: TechnologyStack
    ) -> List[str]:
        """Detect external integrations and services"""
        print("  🔌 Detecting integration requirements...")

        integrations = []

        # Database integrations
        if tech_stack.databases:
            integrations.append("database_management")

        # Authentication
        auth_indicators = ["auth", "passport", "oauth", "jwt", "session"]
        if any(
            indicator in " ".join(tech_stack.frameworks)
            for indicator in auth_indicators
        ):
            integrations.append("authentication")

        # API integrations
        if "fastapi" in tech_stack.frameworks or "express" in tech_stack.frameworks:
            integrations.append("api_development")

        # Deployment
        if tech_stack.tools & {"docker", "kubernetes", "terraform"}:
            integrations.append("containerization")

        # Monitoring
        monitoring_indicators = ["prometheus", "grafana", "datadog", "newrelic"]
        if any(tool in " ".join(tech_stack.tools) for tool in monitoring_indicators):
            integrations.append("monitoring")

        # Testing
        testing_indicators = ["jest", "pytest", "junit", "mocha", "cypress"]
        if any(tool in " ".join(tech_stack.frameworks) for tool in testing_indicators):
            integrations.append("testing_automation")

        return integrations

    async def _recommend_subagents(
        self,
        tech_stack: TechnologyStack,
        architecture: ArchitecturePattern,
        complexity: ProjectComplexity,
    ) -> List[str]:
        """Recommend optimal subagent team based on comprehensive analysis"""
        print("  🤖 Recommending subagent team...")

        recommended = set()

        # Always include code reviewer
        recommended.add("code-reviewer")

        # === LANGUAGE-BASED RECOMMENDATIONS ===

        # Python projects - always add backend developer and test engineer
        if "python" in tech_stack.languages:
            recommended.add("backend-developer")
            recommended.add("test-engineer")

        # JavaScript/TypeScript projects
        if {"javascript", "typescript"} & set(tech_stack.languages):
            # Check if it's frontend (has HTML/CSS) or backend (Node.js)
            if {"html", "css"} & set(tech_stack.languages):
                recommended.add("frontend-developer")
            else:
                recommended.add("backend-developer")  # Node.js backend

        # Java projects
        if "java" in tech_stack.languages:
            recommended.add("backend-developer")

        # === FRAMEWORK-BASED RECOMMENDATIONS ===

        # Frontend frameworks
        frontend_frameworks = {
            "react",
            "vue",
            "angular",
            "svelte",
            "nextjs",
            "nuxt",
            "gatsby",
        }
        if tech_stack.frameworks & frontend_frameworks:
            recommended.add("frontend-developer")

        # Backend frameworks
        backend_frameworks = {
            "express",
            "fastapi",
            "django",
            "flask",
            "rails",
            "spring",
            "fastify",
        }
        if tech_stack.frameworks & backend_frameworks:
            recommended.add("backend-developer")

        # Mobile frameworks
        mobile_frameworks = {"react-native", "flutter", "ionic"}
        if tech_stack.frameworks & mobile_frameworks:
            recommended.add("mobile-developer")

        # Testing frameworks
        testing_frameworks = {"pytest", "jest", "junit", "mocha", "cypress", "selenium"}
        if tech_stack.frameworks & testing_frameworks:
            recommended.add("test-engineer")

        # === DATABASE & DATA RECOMMENDATIONS ===

        if tech_stack.databases:
            recommended.add("database-specialist")

        # Data science indicators
        data_tools = {"pandas", "numpy", "tensorflow", "pytorch", "scikit-learn"}
        if tech_stack.tools & data_tools:
            recommended.add("data-scientist")

        # === INFRASTRUCTURE & DEVOPS ===

        # DevOps engineer
        devops_tools = {"docker", "kubernetes", "terraform", "ansible", "jenkins"}
        if (
            tech_stack.tools & devops_tools
            or architecture == ArchitecturePattern.MICROSERVICES
        ):
            recommended.add("devops-engineer")

        # === DOCUMENTATION & CONTENT ===

        # Documentation specialist for markdown-heavy projects
        if "markdown" in tech_stack.languages:
            recommended.add("documentation-specialist")

        # === SECURITY & PERFORMANCE ===

        # Security auditor for complex projects
        if complexity in [ProjectComplexity.COMPLEX, ProjectComplexity.ENTERPRISE]:
            recommended.add("security-auditor")

        # Performance optimizer for complex/enterprise projects
        if complexity in [
            ProjectComplexity.COMPLEX,
            ProjectComplexity.ENTERPRISE,
        ] or architecture in [
            ArchitecturePattern.MICROSERVICES,
            ArchitecturePattern.SERVERLESS,
        ]:
            recommended.add("performance-optimizer")

        # API specialist for API-heavy projects
        if (
            architecture == ArchitecturePattern.API_FIRST
            or {"fastapi", "express", "django-rest"} & tech_stack.frameworks
        ):
            recommended.add("api-developer")

        return list(recommended)

    def _estimate_team_size(
        self, complexity: ProjectComplexity, agent_count: int
    ) -> int:
        """Estimate recommended team size based on complexity and agent count"""
        base_size = {
            ProjectComplexity.SIMPLE: 1,
            ProjectComplexity.MEDIUM: 2,
            ProjectComplexity.COMPLEX: 4,
            ProjectComplexity.ENTERPRISE: 8,
        }

        # Adjust based on number of recommended agents
        return max(base_size[complexity], min(agent_count, 12))

    async def save_analysis(
        self, profile: ProjectProfile, output_path: Optional[str] = None
    ) -> str:
        """Save analysis results to JSON file"""
        if output_path is None:
            output_path = Path(profile.path) / "subforge_analysis.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"💾 Analysis saved to: {output_path}")
        return str(output_path)


# CLI interface for testing
async def main():
    """Main CLI interface for testing the project analyzer"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python project_analyzer.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]

    analyzer = ProjectAnalyzer()

    try:
        profile = await analyzer.analyze_project(project_path)

        print("\n" + "=" * 60)
        print("📋 PROJECT ANALYSIS REPORT")
        print("=" * 60)
        print(f"Project: {profile.name}")
        print(f"Path: {profile.path}")
        print(f"Architecture: {profile.architecture_pattern.value}")
        print(f"Complexity: {profile.complexity.value}")
        print(f"Team Size Estimate: {profile.team_size_estimate}")
        print("\n🔧 Technology Stack:")
        print(f"  Languages: {', '.join(profile.technology_stack.languages)}")
        print(f"  Frameworks: {', '.join(profile.technology_stack.frameworks)}")
        print(f"  Databases: {', '.join(profile.technology_stack.databases)}")
        print(f"  Tools: {', '.join(profile.technology_stack.tools)}")
        print("\n🤖 Recommended Subagents:")
        for agent in profile.recommended_subagents:
            print(f"  • {agent}")
        print("\n🔌 Integration Requirements:")
        for integration in profile.integration_requirements:
            print(f"  • {integration}")
        print("\n📊 Project Metrics:")
        print(f"  Files: {profile.file_count:,}")
        print(f"  Lines of Code: {profile.lines_of_code:,}")
        print(f"  Has Tests: {'Yes' if profile.has_tests else 'No'}")
        print(f"  Has CI/CD: {'Yes' if profile.has_ci_cd else 'No'}")
        print(f"  Has Docker: {'Yes' if profile.has_docker else 'No'}")
        print(f"  Has Documentation: {'Yes' if profile.has_docs else 'No'}")

        # Save analysis
        await analyzer.save_analysis(profile)

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
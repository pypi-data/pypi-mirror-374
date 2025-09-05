"""
Intelligent Template System for SubForge
Dynamic agent template generation based on project analysis
"""

from typing import Any, Dict, List


class IntelligentTemplateGenerator:
    """Generates agent templates based on project characteristics"""

    def __init__(self):
        self.base_tools = ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep", "Glob"]

    def generate_from_analysis(
        self, project_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate agent templates based on project analysis
        """
        templates = []

        # Always include orchestrator
        templates.append(self._create_orchestrator_template(project_profile))

        # Technology-specific agents
        for language in project_profile.get("technology_stack", {}).get(
            "languages", []
        ):
            templates.append(self._create_language_agent(language, project_profile))

        # Framework-specific agents
        for framework in project_profile.get("technology_stack", {}).get(
            "frameworks", []
        ):
            templates.append(self._create_framework_agent(framework, project_profile))

        # Architecture-specific agents
        architecture = project_profile.get("architecture_pattern", "monolithic")
        if architecture == "microservices":
            templates.extend(self._create_microservices_agents(project_profile))
        elif architecture == "serverless":
            templates.extend(self._create_serverless_agents(project_profile))

        # Domain-specific agents based on detected patterns
        if self._has_authentication(project_profile):
            templates.append(self._create_auth_specialist())

        if self._has_data_processing(project_profile):
            templates.append(self._create_data_specialist())

        if self._has_api_layer(project_profile):
            templates.append(self._create_api_specialist())

        # Quality assurance agents
        templates.extend(self._create_qa_agents(project_profile))

        return templates

    def _create_orchestrator_template(self, profile: Dict) -> Dict:
        """Create orchestrator agent template"""
        complexity = profile.get("complexity", "medium")

        return {
            "name": "orchestrator",
            "model": "opus-4.1" if complexity == "high" else "sonnet",
            "description": f"Master orchestrator for {profile.get('name')} project",
            "tools": self.base_tools
            + [
                "Task",
                "TodoWrite",
                "WebSearch",
                "WebFetch",
                "mcp__perplexity__perplexity_ask",
                "mcp__github__search_code",
                "mcp__Ref__ref_search_documentation",
            ],
            "context": self._generate_orchestrator_context(profile),
        }

    def _create_language_agent(self, language: str, profile: Dict) -> Dict:
        """Create language-specific agent"""
        language_configs = {
            "python": {
                "name": "python-developer",
                "specialization": "Python development, async programming, type hints",
                "extra_tools": ["mcp__ide__executeCode"],
            },
            "typescript": {
                "name": "typescript-developer",
                "specialization": "TypeScript, type safety, modern JavaScript",
                "extra_tools": ["mcp__ide__getDiagnostics"],
            },
            "javascript": {
                "name": "javascript-developer",
                "specialization": "JavaScript, ES6+, async patterns",
                "extra_tools": ["mcp__playwright__browser_navigate"],
            },
        }

        config = language_configs.get(
            language,
            {
                "name": f"{language}-developer",
                "specialization": f"{language} development",
                "extra_tools": [],
            },
        )

        return {
            "name": config["name"],
            "model": "sonnet",
            "description": f"Specialist in {config['specialization']}",
            "tools": self.base_tools + config["extra_tools"],
            "context": f"Expert in {language} with focus on {profile.get('name')} patterns",
        }

    def _create_framework_agent(self, framework: str, profile: Dict) -> Dict:
        """Create framework-specific agent"""
        framework_configs = {
            "react": {
                "name": "react-specialist",
                "focus": "React components, hooks, state management",
                "tools": ["mcp__playwright__browser_snapshot"],
            },
            "nextjs": {
                "name": "nextjs-specialist",
                "focus": "Next.js 14, App Router, SSR/SSG",
                "tools": ["mcp__playwright__browser_navigate"],
            },
            "fastapi": {
                "name": "fastapi-specialist",
                "focus": "FastAPI, async endpoints, OpenAPI",
                "tools": [],
            },
        }

        config = framework_configs.get(
            framework,
            {
                "name": f"{framework}-specialist",
                "focus": f"{framework} framework",
                "tools": [],
            },
        )

        return {
            "name": config["name"],
            "model": "sonnet",
            "description": f"Expert in {config['focus']}",
            "tools": self.base_tools + config["tools"],
            "context": self._generate_framework_context(framework, profile),
        }

    def _create_microservices_agents(self, profile: Dict) -> List[Dict]:
        """Create agents for microservices architecture"""
        return [
            {
                "name": "service-orchestrator",
                "model": "sonnet",
                "description": "Microservices coordination and communication",
                "tools": self.base_tools + ["mcp__github__create_repository"],
                "context": "Service mesh, API gateway, service discovery",
            },
            {
                "name": "container-specialist",
                "model": "haiku",
                "description": "Docker, Kubernetes, container orchestration",
                "tools": self.base_tools,
                "context": "Containerization, scaling, deployment",
            },
        ]

    def _create_serverless_agents(self, profile: Dict) -> List[Dict]:
        """Create agents for serverless architecture"""
        return [
            {
                "name": "serverless-specialist",
                "model": "sonnet",
                "description": "Serverless functions, event-driven architecture",
                "tools": self.base_tools,
                "context": "Lambda, Edge functions, event triggers",
            }
        ]

    def _create_auth_specialist(self) -> Dict:
        """Create authentication specialist"""
        return {
            "name": "auth-specialist",
            "model": "sonnet",
            "description": "Authentication, authorization, security",
            "tools": self.base_tools + ["mcp__perplexity__perplexity_ask"],
            "context": "OAuth, JWT, session management, security best practices",
        }

    def _create_data_specialist(self) -> Dict:
        """Create data processing specialist"""
        return {
            "name": "data-specialist",
            "model": "sonnet",
            "description": "Data processing, ML pipelines, analytics",
            "tools": self.base_tools + ["mcp__ide__executeCode"],
            "context": "Data pipelines, ML models, analytics, visualization",
        }

    def _create_api_specialist(self) -> Dict:
        """Create API specialist"""
        return {
            "name": "api-specialist",
            "model": "sonnet",
            "description": "API design, REST/GraphQL, OpenAPI",
            "tools": self.base_tools,
            "context": "RESTful design, GraphQL schemas, API documentation",
        }

    def _create_qa_agents(self, profile: Dict) -> List[Dict]:
        """Create quality assurance agents"""
        agents = [
            {
                "name": "code-reviewer",
                "model": "sonnet",
                "description": "Code quality, standards, best practices",
                "tools": self.base_tools,
                "context": "Code review, patterns, anti-patterns, refactoring",
            }
        ]

        if profile.get("has_tests"):
            agents.append(
                {
                    "name": "test-engineer",
                    "model": "sonnet",
                    "description": "Testing strategies, test automation",
                    "tools": self.base_tools + ["mcp__playwright__browser_click"],
                    "context": "Unit tests, integration tests, E2E tests",
                }
            )

        return agents

    def _has_authentication(self, profile: Dict) -> bool:
        """Check if project has authentication"""
        # Logic to detect auth patterns
        return any(
            keyword in str(profile).lower()
            for keyword in ["auth", "login", "user", "session"]
        )

    def _has_data_processing(self, profile: Dict) -> bool:
        """Check if project has data processing"""
        return any(
            keyword in str(profile).lower()
            for keyword in ["data", "ml", "analytics", "pandas", "numpy"]
        )

    def _has_api_layer(self, profile: Dict) -> bool:
        """Check if project has API layer"""
        return any(
            keyword in str(profile).lower()
            for keyword in ["api", "rest", "graphql", "endpoint"]
        )

    def _generate_orchestrator_context(self, profile: Dict) -> str:
        """Generate context for orchestrator"""
        return f"""
You are the master orchestrator for {profile.get('name')}.
Project complexity: {profile.get('complexity')}
Architecture: {profile.get('architecture_pattern')}
Team size: {profile.get('team_size_estimate')}

Your role is to coordinate {len(profile.get('recommended_subagents', []))} specialized agents
for optimal development workflow.

Use parallel execution for:
- Analysis phases (all agents simultaneously)
- Research tasks (multiple sources)
- Independent implementation tasks

Use sequential execution for:
- Dependent tasks
- Database migrations
- Critical path operations
"""

    def _generate_framework_context(self, framework: str, profile: Dict) -> str:
        """Generate context for framework specialist"""
        return f"""
You are a {framework} specialist for {profile.get('name')}.
Focus on {framework}-specific patterns and best practices.
Ensure compatibility with project architecture: {profile.get('architecture_pattern')}.
"""
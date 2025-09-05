"""
Intelligent Test Generation System with Context Engineering Integration
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestFramework(Enum):
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"
    JUNIT = "junit"


@dataclass
class TestCase:
    name: str
    description: str
    test_type: TestType
    framework: TestFramework
    file_path: str
    code: str
    dependencies: List[str]
    assertions: List[str]


@dataclass
class TestSuite:
    name: str
    description: str
    test_cases: List[TestCase]
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    fixtures: Optional[Dict[str, str]] = None


class TestGenerator:
    """
    Intelligent test generator that creates comprehensive test suites
    based on project analysis and Context Engineering principles
    """

    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)
        self.test_templates = self._load_test_templates()

    def _load_test_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load test templates for different frameworks and patterns"""
        templates = {}

        # Python/pytest templates
        templates["python"] = {
            "unit_test": '''
import pytest
from unittest.mock import Mock, patch
from {module_path} import {class_name}

class Test{class_name}:
    """Test suite for {class_name}"""
    
    @pytest.fixture
    def {fixture_name}(self):
        """Create test fixture"""
        return {class_name}({fixture_args})
    
    def test_{method_name}_success(self, {fixture_name}):
        """Test {method_name} success scenario"""
        # Arrange
        {arrange_code}
        
        # Act
        result = {fixture_name}.{method_name}({method_args})
        
        # Assert
        {assert_code}
        
    def test_{method_name}_error_handling(self, {fixture_name}):
        """Test {method_name} error handling"""
        # Arrange
        {error_arrange_code}
        
        # Act & Assert
        with pytest.raises({expected_exception}):
            {fixture_name}.{method_name}({error_args})
''',
            "integration_test": '''
import pytest
import asyncio
from {module_path} import {service_class}

@pytest.mark.asyncio
class Test{service_class}Integration:
    """Integration tests for {service_class}"""
    
    @pytest.fixture
    async def {service_fixture}(self):
        """Create service fixture with dependencies"""
        service = {service_class}()
        await service.initialize()
        yield service
        await service.cleanup()
    
    async def test_{operation}_integration(self, {service_fixture}):
        """Test {operation} integration flow"""
        # Arrange
        {integration_arrange}
        
        # Act
        result = await {service_fixture}.{operation}({operation_args})
        
        # Assert
        {integration_assert}
''',
            "api_test": '''
import pytest
import httpx
from fastapi.testclient import TestClient
from {app_module} import app

class Test{api_name}API:
    """API tests for {api_name}"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_{endpoint}_get_success(self, client):
        """Test GET {endpoint} success"""
        response = client.get("{endpoint_path}")
        assert response.status_code == 200
        data = response.json()
        {response_assertions}
    
    def test_{endpoint}_post_success(self, client):
        """Test POST {endpoint} success"""
        payload = {test_payload}
        response = client.post("{endpoint_path}", json=payload)
        assert response.status_code == 201
        {post_assertions}
    
    def test_{endpoint}_validation_error(self, client):
        """Test {endpoint} validation error"""
        invalid_payload = {invalid_payload}
        response = client.post("{endpoint_path}", json=invalid_payload)
        assert response.status_code == 422
''',
        }

        # JavaScript/Jest templates
        templates["javascript"] = {
            "unit_test": """
const {{ {class_name} }} = require('{module_path}');

describe('{class_name}', () => {{
    let {instance_name};
    
    beforeEach(() => {{
        {instance_name} = new {class_name}({constructor_args});
    }});
    
    afterEach(() => {{
        {cleanup_code}
    }});
    
    describe('{method_name}', () => {{
        test('should {expected_behavior}', async () => {{
            // Arrange
            {arrange_code}
            
            // Act
            const result = await {instance_name}.{method_name}({method_args});
            
            // Assert
            {assertions}
        }});
        
        test('should handle errors correctly', async () => {{
            // Arrange
            {error_arrange}
            
            // Act & Assert
            await expect({instance_name}.{method_name}({error_args}))
                .rejects.toThrow({expected_error});
        }});
    }});
}});
""",
            "api_test": """
const request = require('supertest');
const app = require('{app_path}');

describe('{api_name} API', () => {{
    describe('GET {endpoint_path}', () => {{
        test('should return {expected_response}', async () => {{
            const response = await request(app)
                .get('{endpoint_path}')
                .expect(200);
                
            {response_assertions}
        }});
    }});
    
    describe('POST {endpoint_path}', () => {{
        test('should create {resource_name}', async () => {{
            const payload = {test_payload};
            
            const response = await request(app)
                .post('{endpoint_path}')
                .send(payload)
                .expect(201);
                
            {post_assertions}
        }});
        
        test('should validate required fields', async () => {{
            const invalidPayload = {invalid_payload};
            
            await request(app)
                .post('{endpoint_path}')
                .send(invalidPayload)
                .expect(400);
        }});
    }});
}});
""",
        }

        return templates

    def generate_test_suite_for_project(
        self, project_profile: Dict[str, Any], use_case: str = None
    ) -> TestSuite:
        """
        Generate comprehensive test suite based on project analysis
        """
        primary_language = self._detect_primary_language(project_profile)
        framework = self._select_test_framework(primary_language)

        test_cases = []

        # Generate unit tests
        test_cases.extend(self._generate_unit_tests(project_profile, framework))

        # Generate integration tests
        test_cases.extend(self._generate_integration_tests(project_profile, framework))

        # Generate API tests if applicable
        if self._has_api_components(project_profile):
            test_cases.extend(self._generate_api_tests(project_profile, framework))

        # Generate performance tests
        if project_profile.get("complexity") != "simple":
            test_cases.extend(
                self._generate_performance_tests(project_profile, framework)
            )

        # Generate security tests
        test_cases.extend(self._generate_security_tests(project_profile, framework))

        suite_name = f"{project_profile['name']}_comprehensive_tests"

        return TestSuite(
            name=suite_name,
            description=f"Comprehensive test suite for {project_profile['name']}",
            test_cases=test_cases,
            setup_code=self._generate_setup_code(project_profile, framework),
            teardown_code=self._generate_teardown_code(project_profile, framework),
            fixtures=self._generate_fixtures(project_profile, framework),
        )

    def _detect_primary_language(self, project_profile: Dict[str, Any]) -> str:
        """Detect primary programming language"""
        languages = project_profile.get("technology_stack", {}).get("languages", [])

        # Priority order for test generation
        priority_languages = ["python", "javascript", "typescript", "java", "go"]

        for lang in priority_languages:
            if lang in languages:
                return lang

        return languages[0] if languages else "python"

    def _select_test_framework(self, language: str) -> TestFramework:
        """Select appropriate test framework for language"""
        framework_map = {
            "python": TestFramework.PYTEST,
            "javascript": TestFramework.JEST,
            "typescript": TestFramework.JEST,
            "java": TestFramework.JUNIT,
            "go": TestFramework.PYTEST,  # Go has its own but we'll use pytest pattern
        }

        return framework_map.get(language, TestFramework.PYTEST)

    def _generate_unit_tests(
        self, project_profile: Dict[str, Any], framework: TestFramework
    ) -> List[TestCase]:
        """Generate unit tests based on project structure"""
        test_cases = []

        # Analyze project files to identify testable units
        testable_modules = self._identify_testable_modules(project_profile)

        for module in testable_modules:
            test_case = TestCase(
                name=f"test_{module['name']}_unit",
                description=f"Unit tests for {module['name']} module",
                test_type=TestType.UNIT,
                framework=framework,
                file_path=f"tests/unit/test_{module['name']}.py",
                code=self._generate_unit_test_code(module, framework),
                dependencies=module.get("dependencies", []),
                assertions=self._generate_unit_assertions(module),
            )
            test_cases.append(test_case)

        return test_cases

    def _generate_integration_tests(
        self, project_profile: Dict[str, Any], framework: TestFramework
    ) -> List[TestCase]:
        """Generate integration tests for system components"""
        test_cases = []

        if project_profile.get("architecture_pattern") == "microservices":
            # Generate service integration tests
            services = self._identify_services(project_profile)

            for service in services:
                test_case = TestCase(
                    name=f"test_{service['name']}_integration",
                    description=f"Integration tests for {service['name']} service",
                    test_type=TestType.INTEGRATION,
                    framework=framework,
                    file_path=f"tests/integration/test_{service['name']}_integration.py",
                    code=self._generate_integration_test_code(service, framework),
                    dependencies=service.get("dependencies", []),
                    assertions=self._generate_integration_assertions(service),
                )
                test_cases.append(test_case)

        return test_cases

    def _generate_api_tests(
        self, project_profile: Dict[str, Any], framework: TestFramework
    ) -> List[TestCase]:
        """Generate API tests for REST/GraphQL endpoints"""
        test_cases = []

        api_endpoints = self._identify_api_endpoints(project_profile)

        for endpoint in api_endpoints:
            test_case = TestCase(
                name=f"test_{endpoint['name']}_api",
                description=f"API tests for {endpoint['path']} endpoint",
                test_type=TestType.INTEGRATION,
                framework=framework,
                file_path=f"tests/api/test_{endpoint['name']}_api.py",
                code=self._generate_api_test_code(endpoint, framework),
                dependencies=["httpx", "fastapi[testing]"],
                assertions=self._generate_api_assertions(endpoint),
            )
            test_cases.append(test_case)

        return test_cases

    def _generate_performance_tests(
        self, project_profile: Dict[str, Any], framework: TestFramework
    ) -> List[TestCase]:
        """Generate performance and load tests"""
        test_cases = []

        # Generate load tests for critical paths
        critical_components = self._identify_critical_components(project_profile)

        for component in critical_components:
            test_case = TestCase(
                name=f"test_{component['name']}_performance",
                description=f"Performance tests for {component['name']}",
                test_type=TestType.PERFORMANCE,
                framework=framework,
                file_path=f"tests/performance/test_{component['name']}_performance.py",
                code=self._generate_performance_test_code(component, framework),
                dependencies=["pytest-benchmark", "locust"],
                assertions=self._generate_performance_assertions(component),
            )
            test_cases.append(test_case)

        return test_cases

    def _generate_security_tests(
        self, project_profile: Dict[str, Any], framework: TestFramework
    ) -> List[TestCase]:
        """Generate security and vulnerability tests"""
        test_cases = []

        security_concerns = self._identify_security_concerns(project_profile)

        for concern in security_concerns:
            test_case = TestCase(
                name=f"test_{concern['name']}_security",
                description=f"Security tests for {concern['description']}",
                test_type=TestType.SECURITY,
                framework=framework,
                file_path=f"tests/security/test_{concern['name']}_security.py",
                code=self._generate_security_test_code(concern, framework),
                dependencies=["pytest-security", "bandit"],
                assertions=self._generate_security_assertions(concern),
            )
            test_cases.append(test_case)

        return test_cases

    # Helper methods for analysis and code generation
    def _identify_testable_modules(
        self, project_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify modules that need unit testing"""
        # This would analyze the actual project structure
        # For now, return example modules based on common patterns
        return [
            {"name": "core", "type": "module", "dependencies": []},
            {"name": "utils", "type": "module", "dependencies": []},
            {"name": "services", "type": "module", "dependencies": ["core"]},
        ]

    def _identify_services(
        self, project_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify services in microservices architecture"""
        return [
            {"name": "user_service", "type": "service", "dependencies": ["database"]},
            {"name": "auth_service", "type": "service", "dependencies": ["cache"]},
        ]

    def _identify_api_endpoints(
        self, project_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify API endpoints for testing"""
        return [
            {"name": "users", "path": "/api/users", "methods": ["GET", "POST"]},
            {"name": "auth", "path": "/api/auth", "methods": ["POST"]},
        ]

    def _identify_critical_components(
        self, project_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify performance-critical components"""
        return [
            {"name": "data_processor", "type": "service", "sla": "100ms"},
            {"name": "api_gateway", "type": "gateway", "sla": "50ms"},
        ]

    def _identify_security_concerns(
        self, project_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify security testing areas"""
        return [
            {"name": "auth", "description": "Authentication and authorization"},
            {
                "name": "input_validation",
                "description": "Input validation and sanitization",
            },
        ]

    def _has_api_components(self, project_profile: Dict[str, Any]) -> bool:
        """Check if project has API components"""
        frameworks = project_profile.get("technology_stack", {}).get("frameworks", [])
        api_frameworks = ["fastapi", "flask", "django", "express", "spring"]
        return any(fw in frameworks for fw in api_frameworks)

    def _generate_unit_test_code(
        self, module: Dict[str, Any], framework: TestFramework
    ) -> str:
        """Generate unit test code for a module"""
        template = self.test_templates.get("python", {}).get("unit_test", "")
        return template.format(
            module_path=f"src.{module['name']}",
            class_name=module["name"].title(),
            fixture_name=f"{module['name']}_instance",
            fixture_args="",
            method_name="process",
            method_args="test_data",
            arrange_code="test_data = {'key': 'value'}",
            assert_code="assert result is not None\nassert result['status'] == 'success'",
            error_arrange_code="invalid_data = None",
            expected_exception="ValueError",
            error_args="invalid_data",
        )

    def _generate_integration_test_code(
        self, service: Dict[str, Any], framework: TestFramework
    ) -> str:
        """Generate integration test code for a service"""
        template = self.test_templates.get("python", {}).get("integration_test", "")
        return template.format(
            module_path=f"src.services.{service['name']}",
            service_class=service["name"].title().replace("_", ""),
            service_fixture=f"{service['name']}_service",
            operation="execute",
            operation_args="test_payload",
            integration_arrange="test_payload = {'action': 'test'}",
            integration_assert="assert result['success'] is True",
        )

    def _generate_api_test_code(
        self, endpoint: Dict[str, Any], framework: TestFramework
    ) -> str:
        """Generate API test code for an endpoint"""
        template = self.test_templates.get("python", {}).get("api_test", "")
        return template.format(
            app_module="src.main",
            api_name=endpoint["name"].title(),
            endpoint=endpoint["name"],
            endpoint_path=endpoint["path"],
            response_assertions="assert 'data' in data\nassert isinstance(data['data'], list)",
            test_payload="{'name': 'Test User', 'email': 'test@example.com'}",
            post_assertions="assert response.json()['id'] is not None",
            invalid_payload="{}",
        )

    def _generate_performance_test_code(
        self, component: Dict[str, Any], framework: TestFramework
    ) -> str:
        """Generate performance test code"""
        return f'''
import pytest
import time
from src.{component['name']} import {component['name'].title()}

class Test{component['name'].title()}Performance:
    @pytest.fixture
    def {component['name']}(self):
        return {component['name'].title()}()
    
    def test_{component['name']}_performance(self, benchmark, {component['name']}):
        """Test {component['name']} meets performance SLA"""
        result = benchmark({component['name']}.execute, test_data={{}})
        
        # SLA: {component.get('sla', '100ms')}
        assert benchmark.stats['mean'] < 0.1  # 100ms
        assert result is not None
    
    def test_{component['name']}_load_test(self, {component['name']}):
        """Test {component['name']} under load"""
        start_time = time.time()
        
        # Simulate load
        for i in range(100):
            result = {component['name']}.execute({{'iteration': i}})
            assert result is not None
        
        total_time = time.time() - start_time
        avg_time = total_time / 100
        
        assert avg_time < 0.1  # Average under 100ms
'''

    def _generate_security_test_code(
        self, concern: Dict[str, Any], framework: TestFramework
    ) -> str:
        """Generate security test code"""
        return f'''
import pytest
from src.security.{concern['name']} import {concern['name'].title()}Handler

class Test{concern['name'].title()}Security:
    def test_{concern['name']}_secure_input(self):
        """Test secure input handling"""
        handler = {concern['name'].title()}Handler()
        
        # Test SQL injection prevention
        malicious_input = "'; DROP TABLE users; --"
        result = handler.process(malicious_input)
        
        assert result['safe'] is True
        assert 'error' not in result
    
    def test_{concern['name']}_xss_prevention(self):
        """Test XSS prevention"""
        handler = {concern['name'].title()}Handler()
        
        xss_input = "<script>alert('xss')</script>"
        result = handler.sanitize(xss_input)
        
        assert '<script>' not in result
        assert 'alert' not in result
    
    def test_{concern['name']}_access_control(self):
        """Test access control"""
        handler = {concern['name'].title()}Handler()
        
        # Test unauthorized access
        unauthorized_request = {{'user': None, 'action': 'admin_action'}}
        result = handler.authorize(unauthorized_request)
        
        assert result['authorized'] is False
        assert result['status_code'] == 403
'''

    def _generate_setup_code(
        self, project_profile: Dict[str, Any], framework: TestFramework
    ) -> str:
        """Generate test setup code"""
        return '''
# Test setup and configuration
import os
import pytest
from pathlib import Path

# Set test environment
os.environ['ENVIRONMENT'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

@pytest.fixture(scope='session')
def test_config():
    """Test configuration fixture"""
    return {
        'database_url': 'sqlite:///test.db',
        'debug': True,
        'testing': True
    }

@pytest.fixture(scope='session')
def test_db():
    """Test database fixture"""
    # Database setup logic here
    yield
    # Database cleanup logic here
'''

    def _generate_teardown_code(
        self, project_profile: Dict[str, Any], framework: TestFramework
    ) -> str:
        """Generate test teardown code"""
        return '''
# Test cleanup and teardown
import shutil
import tempfile

def cleanup_test_files():
    """Clean up test files"""
    test_files = Path('./test_temp')
    if test_files.exists():
        shutil.rmtree(test_files)

def cleanup_test_database():
    """Clean up test database"""
    test_db = Path('./test.db')
    if test_db.exists():
        test_db.unlink()
'''

    def _generate_fixtures(
        self, project_profile: Dict[str, Any], framework: TestFramework
    ) -> Dict[str, str]:
        """Generate test fixtures"""
        return {
            "sample_user": """
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2023-01-01T00:00:00Z"
}
""",
            "sample_api_response": """
{
    "status": "success",
    "data": [],
    "message": "Operation completed successfully"
}
""",
        }

    # Generate assertion helpers
    def _generate_unit_assertions(self, module: Dict[str, Any]) -> List[str]:
        """Generate unit test assertions"""
        return [
            "assert result is not None",
            "assert isinstance(result, dict)",
            "assert result['status'] == 'success'",
        ]

    def _generate_integration_assertions(self, service: Dict[str, Any]) -> List[str]:
        """Generate integration test assertions"""
        return [
            "assert response.status_code == 200",
            "assert result['success'] is True",
            "assert 'data' in result",
        ]

    def _generate_api_assertions(self, endpoint: Dict[str, Any]) -> List[str]:
        """Generate API test assertions"""
        return [
            "assert response.status_code in [200, 201]",
            "assert response.headers['content-type'] == 'application/json'",
            "assert 'data' in response.json()",
        ]

    def _generate_performance_assertions(self, component: Dict[str, Any]) -> List[str]:
        """Generate performance test assertions"""
        sla = component.get("sla", "100ms")
        return [
            f"assert response_time < {sla}",
            "assert cpu_usage < 80",
            "assert memory_usage < 500  # MB",
        ]

    def _generate_security_assertions(self, concern: Dict[str, Any]) -> List[str]:
        """Generate security test assertions"""
        return [
            "assert result['secure'] is True",
            "assert 'vulnerability' not in result",
            "assert result['status_code'] != 500",
        ]
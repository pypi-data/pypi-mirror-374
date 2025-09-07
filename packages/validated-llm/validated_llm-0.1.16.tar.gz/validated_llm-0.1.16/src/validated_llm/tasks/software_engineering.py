"""
Software engineering tasks for project analysis, requirements generation, and user stories.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..base_validator import BaseValidator
from ..validators.composite import CompositeValidator
from ..validators.json_schema import JSONSchemaValidator
from ..validators.markdown import MarkdownValidator
from ..validators.range import RangeValidator
from .base_task import BaseTask


class AnalysisType(Enum):
    """Types of codebase analysis to perform."""

    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    QUALITY = "quality"
    DEPENDENCIES = "dependencies"
    TESTING = "testing"
    DOCUMENTATION = "documentation"


class RequirementType(Enum):
    """Types of requirements to generate."""

    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    USER = "user"
    SYSTEM = "system"


class CodebaseAnalysisTask(BaseTask):
    """
    Analyze codebases for patterns, issues, and improvements.

    Performs comprehensive analysis of software projects including:
    - Architecture analysis and recommendations
    - Security vulnerability assessment
    - Performance bottleneck identification
    - Code quality and maintainability metrics
    - Dependency analysis and risk assessment
    - Test coverage and strategy evaluation
    - Documentation completeness review
    """

    def __init__(
        self,
        analysis_types: Optional[List[AnalysisType]] = None,
        project_language: str = "python",
        project_type: str = "web_application",
        include_dependencies: bool = True,
        include_metrics: bool = True,
        include_recommendations: bool = True,
        severity_levels: Optional[List[str]] = None,
        output_format: str = "detailed_report",
        max_issues_per_category: int = 10,
        **validator_kwargs: Any,
    ):
        """
        Initialize codebase analysis task.

        Args:
            analysis_types: Types of analysis to perform
            project_language: Primary programming language
            project_type: Type of project (web_app, library, service, etc.)
            include_dependencies: Include dependency analysis
            include_metrics: Include code metrics
            include_recommendations: Include improvement recommendations
            severity_levels: Issue severity levels to include
            output_format: Format for analysis output
            max_issues_per_category: Maximum issues per category
            **validator_kwargs: Additional validator configuration
        """
        self.analysis_types = analysis_types or [AnalysisType.ARCHITECTURE, AnalysisType.SECURITY, AnalysisType.MAINTAINABILITY, AnalysisType.QUALITY]
        self.project_language = project_language
        self.project_type = project_type
        self.include_dependencies = include_dependencies
        self.include_metrics = include_metrics
        self.include_recommendations = include_recommendations
        self.severity_levels = severity_levels or ["critical", "high", "medium"]
        self.output_format = output_format
        self.max_issues_per_category = max_issues_per_category

        # Create analysis report schema for validation
        analysis_schema = self._build_analysis_schema()

        # Create composite validator
        validators = [JSONSchemaValidator(schema=analysis_schema, strict_mode=True), RangeValidator(min_value=500, max_value=5000)]

        self._validator = CompositeValidator(validators=validators, operator="AND", **validator_kwargs)

        # Build prompt template
        self._prompt_template = self._build_prompt_template()

    def _build_analysis_schema(self) -> Dict[str, Any]:
        """Build JSON schema for analysis report validation."""
        return {
            "type": "object",
            "properties": {
                "project_overview": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "language": {"type": "string"},
                        "type": {"type": "string"},
                        "size": {"type": "string"},
                        "complexity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "description": {"type": "string"},
                    },
                    "required": ["name", "language", "type", "description"],
                },
                "analysis_results": {
                    "type": "object",
                    "properties": {
                        "architecture": {
                            "type": "object",
                            "properties": {
                                "patterns": {"type": "array", "items": {"type": "string"}},
                                "issues": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                                            "category": {"type": "string"},
                                            "description": {"type": "string"},
                                            "location": {"type": "string"},
                                            "recommendation": {"type": "string"},
                                        },
                                        "required": ["severity", "category", "description"],
                                    },
                                },
                                "score": {"type": "number", "minimum": 0, "maximum": 10},
                            },
                        },
                        "security": {
                            "type": "object",
                            "properties": {
                                "vulnerabilities": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string"},
                                            "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                                            "description": {"type": "string"},
                                            "file": {"type": "string"},
                                            "line": {"type": ["integer", "null"]},
                                            "mitigation": {"type": "string"},
                                        },
                                        "required": ["type", "severity", "description", "mitigation"],
                                    },
                                },
                                "security_score": {"type": "number", "minimum": 0, "maximum": 10},
                            },
                        },
                        "quality": {
                            "type": "object",
                            "properties": {
                                "metrics": {
                                    "type": "object",
                                    "properties": {"maintainability_index": {"type": "number"}, "cyclomatic_complexity": {"type": "number"}, "code_duplication": {"type": "number"}, "test_coverage": {"type": "number"}},
                                },
                                "issues": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {"type": {"type": "string"}, "description": {"type": "string"}, "file": {"type": "string"}, "suggestion": {"type": "string"}},
                                        "required": ["type", "description", "suggestion"],
                                    },
                                },
                                "quality_score": {"type": "number", "minimum": 0, "maximum": 10},
                            },
                        },
                    },
                },
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "impact": {"type": "string"},
                            "effort": {"type": "string", "enum": ["low", "medium", "high"]},
                            "timeline": {"type": "string"},
                        },
                        "required": ["category", "priority", "title", "description", "impact"],
                    },
                },
                "summary": {
                    "type": "object",
                    "properties": {
                        "overall_score": {"type": "number", "minimum": 0, "maximum": 10},
                        "key_strengths": {"type": "array", "items": {"type": "string"}},
                        "critical_issues": {"type": "array", "items": {"type": "string"}},
                        "next_steps": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["overall_score", "key_strengths", "critical_issues", "next_steps"],
                },
            },
            "required": ["project_overview", "analysis_results", "summary"],
        }

    def _build_prompt_template(self) -> str:
        """Build the prompt template for codebase analysis."""
        analysis_types_text = ", ".join([t.value for t in self.analysis_types])

        prompt = f"""
You are a senior software architect and code quality expert. Analyze the provided codebase and generate a comprehensive analysis report.

## Project Information
- Language: {self.project_language}
- Project Type: {self.project_type}
- Analysis Types: {analysis_types_text}

## Codebase to Analyze
{{codebase_content}}

## Analysis Instructions

Perform a thorough analysis covering the requested analysis types. For each type, provide:

### 1. Architecture Analysis (if requested)
- Identify architectural patterns and design principles
- Assess overall system design and structure
- Find architectural issues and anti-patterns
- Evaluate modularity, coupling, and cohesion
- Score: Rate architecture quality (0-10)

### 2. Security Analysis (if requested)
- Identify potential security vulnerabilities
- Check for common security anti-patterns
- Assess input validation and sanitization
- Review authentication and authorization
- Score: Rate security posture (0-10)

### 3. Performance Analysis (if requested)
- Identify performance bottlenecks
- Assess algorithmic complexity
- Review resource usage patterns
- Find inefficient operations
- Score: Rate performance characteristics (0-10)

### 4. Quality Analysis (if requested)
- Assess code maintainability and readability
- Calculate complexity metrics
- Identify code duplication
- Review naming conventions and structure
- Score: Rate overall code quality (0-10)

### 5. Maintainability Analysis (if requested)
- Evaluate ease of modification and extension
- Assess technical debt
- Review documentation completeness
- Check test coverage and quality
- Score: Rate maintainability (0-10)

### 6. Dependency Analysis (if requested)
- Review external dependencies
- Identify outdated or vulnerable packages
- Assess dependency management
- Check for circular dependencies
- Score: Rate dependency health (0-10)

## Output Requirements

Return your analysis as a JSON object with the following structure:

```json
{{
    "project_overview": {{
        "name": "Project name from codebase",
        "language": "{self.project_language}",
        "type": "{self.project_type}",
        "size": "small/medium/large",
        "complexity": "low/medium/high",
        "description": "Brief project description"
    }},
    "analysis_results": {{
        "architecture": {{
            "patterns": ["pattern1", "pattern2"],
            "issues": [
                {{
                    "severity": "high/medium/low",
                    "category": "coupling/cohesion/design",
                    "description": "Detailed issue description",
                    "location": "file or module",
                    "recommendation": "How to fix"
                }}
            ],
            "score": 7.5
        }},
        "security": {{
            "vulnerabilities": [
                {{
                    "type": "SQL Injection/XSS/etc",
                    "severity": "critical/high/medium/low",
                    "description": "Vulnerability description",
                    "file": "filename.py",
                    "line": 123,
                    "mitigation": "How to fix"
                }}
            ],
            "security_score": 8.0
        }},
        "quality": {{
            "metrics": {{
                "maintainability_index": 75.5,
                "cyclomatic_complexity": 12.3,
                "code_duplication": 5.2,
                "test_coverage": 85.0
            }},
            "issues": [
                {{
                    "type": "complexity/duplication/naming",
                    "description": "Issue description",
                    "file": "filename.py",
                    "suggestion": "Improvement suggestion"
                }}
            ],
            "quality_score": 7.8
        }}
    }},
    "recommendations": [
        {{
            "category": "Architecture/Security/Performance/Quality",
            "priority": "high/medium/low",
            "title": "Recommendation title",
            "description": "Detailed recommendation",
            "impact": "Expected impact description",
            "effort": "low/medium/high",
            "timeline": "Estimated timeline"
        }}
    ],
    "summary": {{
        "overall_score": 7.6,
        "key_strengths": ["strength1", "strength2"],
        "critical_issues": ["critical issue 1", "critical issue 2"],
        "next_steps": ["immediate action 1", "immediate action 2"]
    }}
}}
```

## Analysis Guidelines

1. **Be Thorough**: Examine code structure, patterns, potential issues
2. **Be Specific**: Provide exact locations and detailed descriptions
3. **Be Constructive**: Focus on actionable improvements
4. **Be Realistic**: Consider project context and constraints
5. **Prioritize Issues**: Focus on high-impact, critical issues first
6. **Provide Context**: Explain why issues matter and their consequences

Generate the analysis now:
"""
        return prompt

    @property
    def name(self) -> str:
        return "CodebaseAnalysisTask"

    @property
    def description(self) -> str:
        return "Comprehensive codebase analysis for architecture, security, performance, and quality assessment"

    @property
    def prompt_template(self) -> str:
        return self._prompt_template

    @property
    def validator_class(self) -> type:
        return type(self._validator)

    def create_validator(self, **kwargs: Any) -> BaseValidator:
        return self._validator


class RequirementsTask(BaseTask):
    """
    Generate and validate software requirements documents.

    Creates comprehensive requirements documentation including:
    - Functional requirements with acceptance criteria
    - Non-functional requirements (performance, security, usability)
    - Technical requirements and constraints
    - Business requirements and objectives
    - User requirements and personas
    - System requirements and architecture needs
    """

    def __init__(
        self,
        requirement_types: Optional[List[RequirementType]] = None,
        project_type: str = "web_application",
        stakeholders: Optional[List[str]] = None,
        compliance_standards: Optional[List[str]] = None,
        include_acceptance_criteria: bool = True,
        include_priorities: bool = True,
        include_traceability: bool = True,
        output_format: str = "structured_document",
        min_requirements_per_type: int = 3,
        **validator_kwargs: Any,
    ):
        """
        Initialize requirements generation task.

        Args:
            requirement_types: Types of requirements to generate
            project_type: Type of project
            stakeholders: List of stakeholders
            compliance_standards: Compliance standards to consider
            include_acceptance_criteria: Include acceptance criteria
            include_priorities: Include requirement priorities
            include_traceability: Include traceability matrix
            output_format: Output format for requirements
            min_requirements_per_type: Minimum requirements per type
            **validator_kwargs: Additional validator configuration
        """
        self.requirement_types = requirement_types or [RequirementType.FUNCTIONAL, RequirementType.NON_FUNCTIONAL, RequirementType.TECHNICAL]
        self.project_type = project_type
        self.stakeholders = stakeholders or ["end_users", "developers", "product_owner"]
        self.compliance_standards = compliance_standards or []
        self.include_acceptance_criteria = include_acceptance_criteria
        self.include_priorities = include_priorities
        self.include_traceability = include_traceability
        self.output_format = output_format
        self.min_requirements_per_type = min_requirements_per_type

        # Create requirements schema for validation
        requirements_schema = self._build_requirements_schema()

        # Create composite validator
        validators = [JSONSchemaValidator(schema=requirements_schema, strict_mode=True), RangeValidator(min_value=1000, max_value=8000)]

        self._validator = CompositeValidator(validators=validators, operator="AND", **validator_kwargs)

        # Build prompt template
        self._prompt_template = self._build_prompt_template()

    def _build_requirements_schema(self) -> Dict[str, Any]:
        """Build JSON schema for requirements document validation."""
        return {
            "type": "object",
            "properties": {
                "document_info": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "version": {"type": "string"},
                        "date": {"type": "string"},
                        "authors": {"type": "array", "items": {"type": "string"}},
                        "stakeholders": {"type": "array", "items": {"type": "string"}},
                        "project_overview": {"type": "string"},
                    },
                    "required": ["title", "version", "project_overview"],
                },
                "functional_requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                            "complexity": {"type": "string", "enum": ["low", "medium", "high"]},
                            "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                            "dependencies": {"type": "array", "items": {"type": "string"}},
                            "stakeholder": {"type": "string"},
                        },
                        "required": ["id", "title", "description", "priority"],
                    },
                    "minItems": 1,
                },
                "non_functional_requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "category": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "metric": {"type": "string"},
                            "target_value": {"type": "string"},
                            "measurement_method": {"type": "string"},
                            "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                        },
                        "required": ["id", "category", "title", "description", "metric"],
                    },
                },
                "technical_requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "category": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "technology": {"type": "string"},
                            "justification": {"type": "string"},
                            "constraints": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["id", "category", "title", "description"],
                    },
                },
                "traceability_matrix": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "requirement_id": {"type": "string"},
                            "business_objective": {"type": "string"},
                            "user_story": {"type": "string"},
                            "test_case": {"type": "string"},
                            "implementation": {"type": "string"},
                        },
                        "required": ["requirement_id", "business_objective"],
                    },
                },
            },
            "required": ["document_info", "functional_requirements"],
        }

    def _build_prompt_template(self) -> str:
        """Build the prompt template for requirements generation."""
        requirement_types_text = ", ".join([t.value for t in self.requirement_types])
        stakeholders_text = ", ".join(self.stakeholders)
        compliance_text = ", ".join(self.compliance_standards) if self.compliance_standards else "None specified"

        # Build conditional sections
        acceptance_criteria_instruction = ""
        if self.include_acceptance_criteria:
            acceptance_criteria_instruction = "- Acceptance criteria (specific, measurable conditions)"

        traceability_section = ""
        if self.include_traceability:
            traceability_section = """
### Traceability Matrix
Map each requirement to business objectives, user stories, test cases, and implementation components."""

        # Build example sections
        acceptance_criteria_example = ""
        if self.include_acceptance_criteria:
            acceptance_criteria_example = '"acceptance_criteria": ["User can log in with valid credentials", "Invalid credentials show error message"],'

        traceability_example = ""
        if self.include_traceability:
            traceability_example = """,
    "traceability_matrix": [
        {
            "requirement_id": "FR-001",
            "business_objective": "Enable secure user access",
            "user_story": "As a user, I want to log in securely",
            "test_case": "TC-001: User Login Test",
            "implementation": "Authentication module"
        }
    ]"""

        prompt = f"""
You are a senior business analyst and requirements engineer. Generate a comprehensive software requirements document based on the provided project information.

## Project Information
- Project Type: {self.project_type}
- Requirement Types: {requirement_types_text}
- Stakeholders: {stakeholders_text}
- Compliance Standards: {compliance_text}

## Project Description
{{project_description}}

## Requirements Generation Instructions

Generate comprehensive requirements covering the requested types. Structure your output as a JSON document with the following sections:

### Document Information
- Title, version, date, authors
- Project overview and scope
- Stakeholder list and roles

### Functional Requirements
For each functional requirement, provide:
- Unique ID (FR-001, FR-002, etc.)
- Clear title and description
- Priority level (critical/high/medium/low)
- Complexity estimate (low/medium/high)
{acceptance_criteria_instruction}
- Dependencies on other requirements
- Primary stakeholder

### Non-Functional Requirements
For each non-functional requirement, provide:
- Unique ID (NFR-001, NFR-002, etc.)
- Category (performance, security, usability, reliability, etc.)
- Clear title and description
- Measurable metric and target value
- Measurement method
- Priority level

### Technical Requirements
For each technical requirement, provide:
- Unique ID (TR-001, TR-002, etc.)
- Category (infrastructure, integration, platform, etc.)
- Clear title and description
- Technology or approach specification
- Justification for choice
- Technical constraints
{traceability_section}

## Output Requirements

Return your requirements as a JSON object with this structure:

```json
{{
    "document_info": {{
        "title": "Software Requirements Specification",
        "version": "1.0",
        "date": "YYYY-MM-DD",
        "authors": ["Requirements Engineer"],
        "stakeholders": ["{stakeholders_text}"],
        "project_overview": "Comprehensive project description"
    }},
    "functional_requirements": [
        {{
            "id": "FR-001",
            "title": "User Authentication",
            "description": "System must allow users to authenticate using email and password",
            "priority": "critical",
            "complexity": "medium",
            {acceptance_criteria_example}
            "dependencies": ["TR-001"],
            "stakeholder": "end_users"
        }}
    ],
    "non_functional_requirements": [
        {{
            "id": "NFR-001",
            "category": "performance",
            "title": "Response Time",
            "description": "System must respond to user requests within acceptable time limits",
            "metric": "Average response time",
            "target_value": "< 200ms for 95% of requests",
            "measurement_method": "Load testing with realistic user scenarios",
            "priority": "high"
        }}
    ],
    "technical_requirements": [
        {{
            "id": "TR-001",
            "category": "security",
            "title": "Password Encryption",
            "description": "User passwords must be encrypted using industry-standard algorithms",
            "technology": "bcrypt or Argon2",
            "justification": "Provides strong protection against rainbow table attacks",
            "constraints": ["Must comply with OWASP guidelines", "Minimum 12 character passwords"]
        }}
    ]{traceability_example}
}}
```

## Requirements Quality Guidelines

1. **Clarity**: Each requirement must be clear and unambiguous
2. **Completeness**: Cover all aspects of the requested functionality
3. **Consistency**: Ensure requirements don't contradict each other
4. **Testability**: Requirements must be verifiable and testable
5. **Traceability**: Link requirements to business objectives
6. **Feasibility**: Ensure requirements are technically achievable
7. **Prioritization**: Assign realistic priorities based on business value

Generate the requirements document now:
"""
        return prompt

    @property
    def name(self) -> str:
        return "RequirementsTask"

    @property
    def description(self) -> str:
        return "Generate comprehensive software requirements documentation with validation"

    @property
    def prompt_template(self) -> str:
        return self._prompt_template

    @property
    def validator_class(self) -> type:
        return type(self._validator)

    def create_validator(self, **kwargs: Any) -> BaseValidator:
        return self._validator


class UserStoryTask(BaseTask):
    """
    Generate user stories with acceptance criteria and validation.

    Creates well-structured user stories following best practices:
    - Standard user story format (As a... I want... So that...)
    - Detailed acceptance criteria using Given-When-Then format
    - Story sizing and complexity estimation
    - Dependency mapping between stories
    - Epic and theme organization
    - Priority and business value assessment
    """

    def __init__(
        self,
        story_format: str = "standard",
        include_acceptance_criteria: bool = True,
        include_story_points: bool = True,
        include_dependencies: bool = True,
        include_business_value: bool = True,
        persona_types: Optional[List[str]] = None,
        epic_organization: bool = True,
        output_format: str = "agile_backlog",
        min_stories: int = 5,
        max_stories: int = 20,
        **validator_kwargs: Any,
    ):
        """
        Initialize user story generation task.

        Args:
            story_format: Format for user stories (standard, job_story, etc.)
            include_acceptance_criteria: Include acceptance criteria
            include_story_points: Include story point estimation
            include_dependencies: Include story dependencies
            include_business_value: Include business value assessment
            persona_types: Types of user personas to consider
            epic_organization: Organize stories into epics
            output_format: Output format for stories
            min_stories: Minimum number of stories to generate
            max_stories: Maximum number of stories to generate
            **validator_kwargs: Additional validator configuration
        """
        self.story_format = story_format
        self.include_acceptance_criteria = include_acceptance_criteria
        self.include_story_points = include_story_points
        self.include_dependencies = include_dependencies
        self.include_business_value = include_business_value
        self.persona_types = persona_types or ["end_user", "administrator", "manager", "developer", "support_staff"]
        self.epic_organization = epic_organization
        self.output_format = output_format
        self.min_stories = min_stories
        self.max_stories = max_stories

        # Create user story schema for validation
        story_schema = self._build_story_schema()

        # Create composite validator
        validators = [JSONSchemaValidator(schema=story_schema, strict_mode=True), RangeValidator(min_value=min_stories, max_value=max_stories)]

        self._validator = CompositeValidator(validators=validators, operator="AND", **validator_kwargs)

        # Build prompt template
        self._prompt_template = self._build_prompt_template()

    def _build_story_schema(self) -> Dict[str, Any]:
        """Build JSON schema for user story validation."""
        return {
            "type": "object",
            "properties": {
                "backlog_info": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string"},
                        "version": {"type": "string"},
                        "created_date": {"type": "string"},
                        "product_owner": {"type": "string"},
                        "development_team": {"type": "string"},
                        "sprint_capacity": {"type": "number"},
                    },
                    "required": ["product_name", "version"],
                },
                "personas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "description": {"type": "string"},
                            "goals": {"type": "array", "items": {"type": "string"}},
                            "pain_points": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["name", "role", "description"],
                    },
                },
                "epics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "business_value": {"type": "string"},
                            "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                            "estimated_effort": {"type": "string"},
                        },
                        "required": ["id", "title", "description"],
                    },
                },
                "user_stories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "epic_id": {"type": "string"},
                            "title": {"type": "string"},
                            "story": {"type": "string"},
                            "persona": {"type": "string"},
                            "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                            "story_points": {"type": "integer", "minimum": 1, "maximum": 21},
                            "business_value": {"type": "string"},
                            "acceptance_criteria": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"scenario": {"type": "string"}, "given": {"type": "string"}, "when": {"type": "string"}, "then": {"type": "string"}},
                                    "required": ["scenario", "given", "when", "then"],
                                },
                            },
                            "dependencies": {"type": "array", "items": {"type": "string"}},
                            "notes": {"type": "string"},
                        },
                        "required": ["id", "title", "story", "persona", "priority"],
                    },
                    "minItems": 1,
                },
            },
            "required": ["backlog_info", "user_stories"],
        }

    def _build_prompt_template(self) -> str:
        """Build the prompt template for user story generation."""
        personas_text = ", ".join(self.persona_types)

        # Build conditional sections
        personas_section = ""
        if self.persona_types:
            personas_section = """
    "personas": [
        {
            "name": "Primary User",
            "role": "end_user",
            "description": "Primary system user",
            "goals": ["Goal 1", "Goal 2"],
            "pain_points": ["Pain point 1", "Pain point 2"]
        }
    ],"""

        epics_section = ""
        if self.epic_organization:
            epics_section = """
    "epics": [
        {
            "id": "EPIC-001",
            "title": "User Management",
            "description": "Complete user lifecycle management",
            "business_value": "Enable user onboarding and retention",
            "priority": "high",
            "estimated_effort": "3-4 sprints"
        }
    ],"""

        story_fields = []
        story_fields.append('"id": "US-001",')
        if self.epic_organization:
            story_fields.append('"epic_id": "EPIC-001",')
        story_fields.extend(['"title": "User Registration",', '"story": "As a new user, I want to create an account so that I can access the system features",', '"persona": "end_user",', '"priority": "high",'])
        if self.include_story_points:
            story_fields.append('"story_points": 5,')
        if self.include_business_value:
            story_fields.append('"business_value": "High - enables user onboarding",')
        if self.include_acceptance_criteria:
            story_fields.append(
                """
            "acceptance_criteria": [
                {
                    "scenario": "Successful registration",
                    "given": "I am on the registration page",
                    "when": "I enter valid registration details and submit",
                    "then": "I should receive a confirmation email and be redirected to the welcome page"
                }
            ],"""
            )
        if self.include_dependencies:
            story_fields.append('"dependencies": [],')
        story_fields.append('"notes": "Consider social login options in future iterations"')

        story_example = "            " + "\n            ".join(story_fields)

        prompt = f"""
You are a senior product owner and agile coach. Generate a comprehensive set of user stories based on the provided product requirements.

## Product Information
- Story Format: {self.story_format}
- User Personas: {personas_text}
- Include Acceptance Criteria: {self.include_acceptance_criteria}
- Include Story Points: {self.include_story_points}
- Epic Organization: {self.epic_organization}

## Product Requirements
{{product_requirements}}

## User Story Generation Instructions

Generate a well-structured product backlog with user stories following agile best practices:

### Story Format Guidelines
Use the standard format: "As a [persona], I want [functionality] so that [benefit/value]"

### Story Quality Criteria
1. **Independent**: Stories should be self-contained
2. **Negotiable**: Details can be discussed and refined
3. **Valuable**: Each story delivers user value
4. **Estimable**: Story complexity can be estimated
5. **Small**: Stories fit within a sprint
6. **Testable**: Clear acceptance criteria

### Acceptance Criteria Format
Use Given-When-Then format:
- **Given**: Initial context/preconditions
- **When**: Action or event trigger
- **Then**: Expected outcome

## Output Requirements

Return your user stories as a JSON object with this structure:

```json
{{
    "backlog_info": {{
        "product_name": "Product Name",
        "version": "1.0",
        "created_date": "YYYY-MM-DD",
        "product_owner": "Product Owner Name",
        "development_team": "Team Name",
        "sprint_capacity": 30
    }},{personas_section}{epics_section}
    "user_stories": [
        {{
{story_example}
        }}
    ]
}}
```

## Story Writing Guidelines

1. **User-Centric**: Focus on user needs and value
2. **Conversational**: Write in plain language
3. **Complete**: Include all necessary details
4. **Prioritized**: Order by business value and dependencies
5. **Sized Appropriately**: Fit within sprint capacity
6. **Testable**: Clear definition of done
7. **Valuable**: Each story delivers working software

Generate {self.min_stories}-{self.max_stories} user stories covering the core functionality described in the requirements.

Generate the user stories now:
"""
        return prompt

    @property
    def name(self) -> str:
        return "UserStoryTask"

    @property
    def description(self) -> str:
        return "Generate user stories with acceptance criteria and agile backlog organization"

    @property
    def prompt_template(self) -> str:
        return self._prompt_template

    @property
    def validator_class(self) -> type:
        return type(self._validator)

    def create_validator(self, **kwargs: Any) -> BaseValidator:
        return self._validator

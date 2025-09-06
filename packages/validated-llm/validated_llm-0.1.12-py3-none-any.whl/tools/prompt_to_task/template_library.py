"""
Template library for prompt-to-task conversion.

This module provides a library of reusable templates for common prompt patterns,
making it easier to convert prompts to validated tasks by leveraging existing patterns.
"""

import difflib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class PromptTemplate:
    """A reusable template for prompt-to-task conversion."""

    name: str
    category: str  # json, csv, email, api_docs, analysis_report, etc.
    description: str
    prompt_template: str
    validator_type: str  # Type of validator to use
    validator_config: Dict[str, Any] = field(default_factory=dict)
    json_schema: Optional[Dict[str, Any]] = None
    example_output: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create template from dictionary."""
        return cls(**data)


class TemplateLibrary:
    """Manages a library of prompt templates."""

    def __init__(self, library_path: Optional[Path] = None):
        """
        Initialize the template library.

        Args:
            library_path: Path to store template library. Defaults to built-in templates.
        """
        self.library_path = library_path or Path(__file__).parent / "templates"
        self.library_path.mkdir(parents=True, exist_ok=True)
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_templates()
        self._load_builtin_templates()

    def _load_templates(self) -> None:
        """Load templates from library path."""
        template_files = self.library_path.glob("*.json")
        for template_file in template_files:
            try:
                with open(template_file, "r") as f:
                    data = json.load(f)
                    template = PromptTemplate.from_dict(data)
                    self._templates[template.name] = template
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")

    def _load_builtin_templates(self) -> None:
        """Load built-in templates."""
        builtin_templates = [
            # JSON Templates
            PromptTemplate(
                name="user_profile_json",
                category="json",
                description="Generate user profile information in JSON format",
                prompt_template="Generate a user profile for {name} who is {age} years old and works as {occupation}. Include contact information and interests.",
                validator_type="json",
                validator_config={
                    "required_fields": ["name", "age", "email", "occupation", "interests"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer", "minimum": 0, "maximum": 150},
                            "email": {"type": "string", "format": "email"},
                            "occupation": {"type": "string"},
                            "interests": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["name", "age", "email", "occupation", "interests"],
                    },
                },
                json_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer", "minimum": 0, "maximum": 150},
                        "email": {"type": "string", "format": "email"},
                        "occupation": {"type": "string"},
                        "interests": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name", "age", "email", "occupation", "interests"],
                },
                example_output='{"name": "John Doe", "age": 30, "email": "john@example.com", "occupation": "Software Engineer", "interests": ["coding", "hiking", "photography"]}',
                tags=["user", "profile", "personal", "json"],
            ),
            PromptTemplate(
                name="product_catalog_json",
                category="json",
                description="Generate product catalog entries in JSON format",
                prompt_template="Create a product catalog entry for {product_name} in the {category} category. Include pricing, description, and specifications.",
                validator_type="json",
                validator_config={
                    "required_fields": ["id", "name", "category", "price", "description"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "price": {"type": "number", "minimum": 0},
                            "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
                            "description": {"type": "string"},
                            "specifications": {"type": "object"},
                        },
                        "required": ["id", "name", "category", "price", "description"],
                    },
                },
                json_schema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "category": {"type": "string"},
                        "price": {"type": "number", "minimum": 0},
                        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
                        "description": {"type": "string"},
                        "specifications": {"type": "object"},
                    },
                    "required": ["id", "name", "category", "price", "description"],
                },
                example_output='{"id": "PROD-001", "name": "Wireless Mouse", "category": "Electronics", "price": 29.99, "currency": "USD", "description": "Ergonomic wireless mouse with precision tracking", "specifications": {"dpi": 1600, "battery": "AA x2", "connectivity": "USB receiver"}}',
                tags=["product", "catalog", "ecommerce", "json"],
            ),
            # CSV Templates
            PromptTemplate(
                name="sales_report_csv",
                category="csv",
                description="Generate sales report data in CSV format",
                prompt_template="Generate a sales report for {period} showing daily sales data including date, product, quantity, and revenue.",
                validator_type="csv",
                validator_config={"required_columns": ["date", "product", "quantity", "revenue"], "min_rows": 5},
                example_output="date,product,quantity,revenue\n2024-01-01,Widget A,10,299.90\n2024-01-02,Widget B,5,149.95",
                tags=["sales", "report", "csv", "business"],
            ),
            # Email Templates
            PromptTemplate(
                name="business_email",
                category="email",
                description="Generate professional business emails",
                prompt_template="Write a professional email to {recipient} regarding {subject}. The tone should be {tone} and include {key_points}.",
                validator_type="email",
                validator_config={"require_subject": True, "min_body_length": 50, "require_greeting": True, "require_closing": True},
                example_output="Subject: Project Update\n\nDear Mr. Johnson,\n\nI hope this email finds you well...\n\nBest regards,\nJohn Doe",
                tags=["email", "business", "communication"],
            ),
            # API Documentation Templates
            PromptTemplate(
                name="rest_api_endpoint",
                category="api_docs",
                description="Generate REST API endpoint documentation",
                prompt_template="Document the {http_method} endpoint at {endpoint_path} that {endpoint_description}. Include request/response examples.",
                validator_type="markdown",
                validator_config={"required_sections": ["description", "request", "response", "example"], "require_code_blocks": True},
                example_output='## GET /api/users/{id}\n\nRetrieves user information by ID.\n\n### Request\n```http\nGET /api/users/123\n```\n\n### Response\n```json\n{\n  "id": 123,\n  "name": "John Doe"\n}\n```',
                tags=["api", "documentation", "rest", "markdown"],
            ),
            # Analysis Report Templates
            PromptTemplate(
                name="data_analysis_report",
                category="analysis_report",
                description="Generate data analysis reports with insights",
                prompt_template="Analyze the {dataset_name} dataset and provide insights on {analysis_focus}. Include summary statistics and recommendations.",
                validator_type="markdown",
                validator_config={"required_sections": ["summary", "methodology", "findings", "recommendations"], "require_statistics": True, "min_length": 500},
                tags=["analysis", "report", "data", "insights"],
            ),
            # SQL Query Templates
            PromptTemplate(
                name="sql_data_query",
                category="sql",
                description="Generate SQL queries for data retrieval",
                prompt_template="Write a SQL query to {query_objective} from the {table_name} table with conditions: {conditions}.",
                validator_type="sql",
                validator_config={"allowed_statements": ["SELECT"], "require_where_clause": True, "check_syntax": True},
                example_output="SELECT id, name, email FROM users WHERE age > 18 AND status = 'active';",
                tags=["sql", "query", "database"],
            ),
            # Story/Content Templates
            PromptTemplate(
                name="story_with_scenes",
                category="story",
                description="Generate stories with structured scenes",
                prompt_template="Write a {genre} story about {main_character} who {character_goal}. Include {num_scenes} scenes with clear progression.",
                validator_type="story_scenes",
                validator_config={"min_scenes": 3, "require_scene_titles": True, "require_scene_descriptions": True},
                tags=["story", "creative", "narrative", "scenes"],
            ),
            # Extended API Documentation Templates
            PromptTemplate(
                name="openapi_specification",
                category="api_docs",
                description="Generate OpenAPI/Swagger specification for REST APIs",
                prompt_template="Create an OpenAPI 3.0 specification for the {api_name} API that {api_purpose}. Include endpoints for {resource_types} with full CRUD operations.",
                validator_type="json",
                validator_config={
                    "required_fields": ["openapi", "info", "paths", "components"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "openapi": {"type": "string", "pattern": "^3\\.0\\.[0-9]+$"},
                            "info": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "version": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["title", "version"],
                            },
                            "paths": {"type": "object"},
                            "components": {"type": "object"},
                        },
                        "required": ["openapi", "info", "paths"],
                    },
                },
                example_output='{"openapi": "3.0.0", "info": {"title": "User API", "version": "1.0.0", "description": "API for user management"}, "paths": {"/users": {"get": {"summary": "List users"}}}}',
                tags=["api", "openapi", "swagger", "documentation", "rest"],
            ),
            PromptTemplate(
                name="graphql_schema_docs",
                category="api_docs",
                description="Generate GraphQL schema documentation with types and resolvers",
                prompt_template="Document a GraphQL schema for {domain} that includes types for {entity_types} with queries and mutations for {operations}.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["types", "queries", "mutations", "examples"],
                    "require_code_blocks": True,
                    "code_block_languages": ["graphql"],
                },
                example_output="# User Management GraphQL Schema\n\n## Types\n\n```graphql\ntype User {\n  id: ID!\n  name: String!\n  email: String!\n}\n```\n\n## Queries\n\n```graphql\ntype Query {\n  user(id: ID!): User\n  users: [User!]!\n}\n```",
                tags=["api", "graphql", "schema", "documentation"],
            ),
            PromptTemplate(
                name="api_integration_guide",
                category="api_docs",
                description="Create comprehensive API integration guides with code examples",
                prompt_template="Create an integration guide for the {api_name} API showing how to {use_case}. Include authentication setup and code examples in {programming_languages}.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["prerequisites", "authentication", "examples", "error-handling", "best-practices"],
                    "require_code_blocks": True,
                    "min_length": 1000,
                },
                tags=["api", "integration", "guide", "documentation", "tutorial"],
            ),
            # Data Analysis and Reporting Templates
            PromptTemplate(
                name="statistical_analysis_report",
                category="analysis_report",
                description="Generate detailed statistical analysis reports with visualizations",
                prompt_template="Perform statistical analysis on {dataset_description} focusing on {analysis_objectives}. Include descriptive statistics, {statistical_tests}, and interpretation of results.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["executive-summary", "data-description", "methodology", "results", "statistical-tests", "conclusions", "recommendations"],
                    "require_tables": True,
                    "require_statistics": True,
                    "min_length": 1500,
                },
                tags=["analysis", "statistics", "report", "data-science", "research"],
            ),
            PromptTemplate(
                name="business_intelligence_dashboard",
                category="analysis_report",
                description="Design business intelligence dashboard specifications",
                prompt_template="Design a BI dashboard for {business_area} that tracks {key_metrics}. Include KPIs, visualizations, and data refresh requirements for {target_audience}.",
                validator_type="json",
                validator_config={
                    "required_fields": ["dashboard_name", "metrics", "visualizations", "data_sources", "refresh_schedule"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "dashboard_name": {"type": "string"},
                            "description": {"type": "string"},
                            "metrics": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "calculation": {"type": "string"},
                                        "unit": {"type": "string"},
                                        "target": {"type": "number"},
                                    },
                                    "required": ["name", "calculation"],
                                },
                            },
                            "visualizations": {"type": "array", "items": {"type": "object"}},
                            "data_sources": {"type": "array", "items": {"type": "string"}},
                            "refresh_schedule": {"type": "string"},
                        },
                        "required": ["dashboard_name", "metrics", "visualizations"],
                    },
                },
                tags=["business-intelligence", "dashboard", "analytics", "kpi", "visualization"],
            ),
            PromptTemplate(
                name="market_research_report",
                category="analysis_report",
                description="Generate comprehensive market research reports",
                prompt_template="Create a market research report for {industry} focusing on {research_objectives}. Analyze market size, trends, competitors, and opportunities in {geographic_region}.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["executive-summary", "market-overview", "market-size", "trends", "competitive-analysis", "opportunities", "threats", "recommendations"],
                    "require_data_citations": True,
                    "min_length": 2000,
                },
                tags=["market-research", "analysis", "business", "strategy", "report"],
            ),
            # Content Generation Templates
            PromptTemplate(
                name="blog_post_seo",
                category="content",
                description="Generate SEO-optimized blog posts with metadata",
                prompt_template="Write a {word_count}-word blog post about {topic} targeting the keyword '{target_keyword}'. Include an engaging introduction, {num_sections} main sections, and a conclusion. Optimize for {target_audience}.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["title", "meta-description", "introduction", "conclusion"],
                    "require_headings": True,
                    "min_word_count": 500,
                    "require_keyword_density": {"min": 1, "max": 3},
                },
                example_output="# 10 Best Practices for Remote Work Success\n\n**Meta Description:** Discover proven strategies for remote work success...\n\n## Introduction\n\nRemote work has transformed...",
                tags=["blog", "content", "seo", "marketing", "writing"],
            ),
            PromptTemplate(
                name="marketing_campaign_copy",
                category="content",
                description="Create multi-channel marketing campaign copy",
                prompt_template="Create marketing copy for a {campaign_type} campaign promoting {product_service}. Include variations for {channels} targeting {audience_segments}. Campaign goal: {campaign_goal}.",
                validator_type="json",
                validator_config={
                    "required_fields": ["campaign_name", "channels", "messages", "call_to_action"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "campaign_name": {"type": "string"},
                            "campaign_goal": {"type": "string"},
                            "channels": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "object"},
                                    "social_media": {"type": "object"},
                                    "web": {"type": "object"},
                                },
                            },
                            "messages": {"type": "array", "items": {"type": "object"}},
                            "call_to_action": {"type": "string"},
                        },
                        "required": ["campaign_name", "channels", "messages", "call_to_action"],
                    },
                },
                tags=["marketing", "campaign", "copywriting", "advertising", "content"],
            ),
            PromptTemplate(
                name="social_media_content_calendar",
                category="content",
                description="Generate social media content calendar with posts",
                prompt_template="Create a {duration} social media content calendar for {brand_name} on {platforms}. Focus on {content_themes} with {posts_per_week} posts per week.",
                validator_type="csv",
                validator_config={
                    "required_columns": ["date", "platform", "post_type", "content", "hashtags", "media_type"],
                    "min_rows": 20,
                    "date_column": "date",
                },
                tags=["social-media", "content", "calendar", "marketing", "planning"],
            ),
            PromptTemplate(
                name="email_newsletter",
                category="content",
                description="Design email newsletters with sections and CTAs",
                prompt_template="Create an email newsletter for {company_name} with theme '{newsletter_theme}'. Include {num_sections} content sections, personalization for {audience_segment}, and clear CTAs.",
                validator_type="email",
                validator_config={
                    "require_subject": True,
                    "require_preview_text": True,
                    "require_sections": ["header", "main-content", "cta", "footer"],
                    "require_unsubscribe": True,
                    "max_line_length": 600,
                },
                tags=["email", "newsletter", "marketing", "content", "communication"],
            ),
            # Code Documentation Templates
            PromptTemplate(
                name="code_api_reference",
                category="code_docs",
                description="Generate API reference documentation from code",
                prompt_template="Document the {language} API for {module_name} that {module_purpose}. Include all public methods, parameters, return types, and usage examples.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["overview", "installation", "api-reference", "examples", "error-codes"],
                    "require_code_blocks": True,
                    "require_parameter_tables": True,
                },
                tags=["code", "api", "reference", "documentation", "technical"],
            ),
            PromptTemplate(
                name="code_architecture_doc",
                category="code_docs",
                description="Create software architecture documentation",
                prompt_template="Document the architecture of {system_name} that {system_purpose}. Include system overview, components, data flow, technology stack, and deployment architecture.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["overview", "architecture-diagram", "components", "data-flow", "technology-stack", "deployment", "security-considerations"],
                    "require_diagrams": True,
                    "min_length": 1500,
                },
                tags=["architecture", "documentation", "software", "design", "technical"],
            ),
            PromptTemplate(
                name="code_tutorial",
                category="code_docs",
                description="Write step-by-step coding tutorials",
                prompt_template="Create a tutorial on {tutorial_topic} using {programming_language}. Target audience: {skill_level}. Include {num_exercises} hands-on exercises.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["objectives", "prerequisites", "setup", "steps", "exercises", "conclusion"],
                    "require_code_blocks": True,
                    "require_numbered_steps": True,
                    "min_code_blocks": 5,
                },
                tags=["tutorial", "education", "code", "documentation", "learning"],
            ),
            # Technical Specifications Templates
            PromptTemplate(
                name="technical_requirements_doc",
                category="tech_specs",
                description="Generate technical requirements documentation",
                prompt_template="Create technical requirements for {project_name} that will {project_goal}. Include functional requirements, non-functional requirements, constraints, and acceptance criteria.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["introduction", "functional-requirements", "non-functional-requirements", "constraints", "acceptance-criteria", "appendices"],
                    "require_numbered_requirements": True,
                    "require_priorities": True,
                },
                tags=["requirements", "specification", "technical", "documentation", "project"],
            ),
            PromptTemplate(
                name="database_schema_design",
                category="tech_specs",
                description="Design database schemas with relationships",
                prompt_template="Design a database schema for {application_name} that handles {data_types}. Include tables, relationships, indexes, and constraints. Database type: {database_type}.",
                validator_type="sql",
                validator_config={
                    "allowed_statements": ["CREATE", "ALTER"],
                    "require_primary_keys": True,
                    "require_foreign_keys": True,
                    "require_indexes": True,
                },
                tags=["database", "schema", "sql", "design", "technical"],
            ),
            PromptTemplate(
                name="system_integration_spec",
                category="tech_specs",
                description="Document system integration specifications",
                prompt_template="Create integration specification for connecting {system_a} with {system_b} to achieve {integration_goal}. Include data mapping, protocols, error handling, and security.",
                validator_type="json",
                validator_config={
                    "required_fields": ["integration_name", "systems", "data_mappings", "protocols", "error_handling", "security"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "integration_name": {"type": "string"},
                            "systems": {"type": "array", "items": {"type": "object"}},
                            "data_mappings": {"type": "array", "items": {"type": "object"}},
                            "protocols": {"type": "object"},
                            "error_handling": {"type": "object"},
                            "security": {"type": "object"},
                        },
                        "required": ["integration_name", "systems", "data_mappings", "protocols"],
                    },
                },
                tags=["integration", "specification", "technical", "api", "systems"],
            ),
            # User Stories and Requirements Templates
            PromptTemplate(
                name="user_story_agile",
                category="requirements",
                description="Generate user stories with acceptance criteria",
                prompt_template="Create user stories for {feature_name} in {product_name}. Focus on {user_type} who wants to {user_goal}. Include acceptance criteria and story points.",
                validator_type="markdown",
                validator_config={
                    "require_user_story_format": True,
                    "require_acceptance_criteria": True,
                    "require_story_points": True,
                    "story_format_regex": "As a .+, I want to .+, so that .+",
                },
                example_output="## User Story: Login Feature\n\n**As a** registered user\n**I want to** log in to my account\n**So that** I can access my personalized dashboard\n\n### Acceptance Criteria\n- Given valid credentials...\n\n**Story Points:** 3",
                tags=["agile", "user-story", "requirements", "scrum", "product"],
            ),
            PromptTemplate(
                name="use_case_specification",
                category="requirements",
                description="Write detailed use case specifications",
                prompt_template="Document use cases for {system_feature} in {system_name}. Include actors, preconditions, main flow, alternative flows, and postconditions.",
                validator_type="markdown",
                validator_config={
                    "required_sections": ["use-case-name", "actors", "description", "preconditions", "main-flow", "alternative-flows", "postconditions", "exceptions"],
                    "require_numbered_flows": True,
                },
                tags=["use-case", "requirements", "specification", "analysis", "documentation"],
            ),
            PromptTemplate(
                name="product_roadmap",
                category="requirements",
                description="Create product roadmap with milestones",
                prompt_template="Create a {timeframe} product roadmap for {product_name}. Include {num_releases} releases with features, priorities, and success metrics. Target market: {target_market}.",
                validator_type="json",
                validator_config={
                    "required_fields": ["product_name", "vision", "releases", "milestones"],
                    "schema": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string"},
                            "vision": {"type": "string"},
                            "releases": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "version": {"type": "string"},
                                        "date": {"type": "string", "format": "date"},
                                        "features": {"type": "array", "items": {"type": "object"}},
                                        "success_metrics": {"type": "array", "items": {"type": "string"}},
                                    },
                                    "required": ["version", "date", "features"],
                                },
                            },
                            "milestones": {"type": "array", "items": {"type": "object"}},
                        },
                        "required": ["product_name", "vision", "releases"],
                    },
                },
                tags=["roadmap", "product", "planning", "strategy", "requirements"],
            ),
        ]

        # Add built-in templates if they don't exist
        for template in builtin_templates:
            if template.name not in self._templates:
                self._templates[template.name] = template

    def add_template(self, template: PromptTemplate) -> None:
        """Add a new template to the library."""
        self._templates[template.name] = template
        self.save_template(template)

    def save_template(self, template: PromptTemplate) -> None:
        """Save template to disk."""
        template_path = self.library_path / f"{template.name}.json"
        with open(template_path, "w") as f:
            json.dump(template.to_dict(), f, indent=2)

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self._templates.get(name)

    def list_templates(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[PromptTemplate]:
        """
        List templates, optionally filtered by category or tags.

        Args:
            category: Filter by category
            tags: Filter by tags (matches any tag)

        Returns:
            List of matching templates
        """
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]

        return sorted(templates, key=lambda t: (t.category, t.name))

    def find_similar_templates(self, prompt: str, top_k: int = 5) -> List[Tuple[PromptTemplate, float]]:
        """
        Find templates similar to the given prompt.

        Args:
            prompt: The prompt to match
            top_k: Number of top matches to return

        Returns:
            List of (template, similarity_score) tuples
        """
        similarities = []

        for template in self._templates.values():
            # Calculate similarity based on prompt template
            template_words = set(template.prompt_template.lower().split())
            prompt_words = set(prompt.lower().split())

            # Jaccard similarity
            intersection = template_words.intersection(prompt_words)
            union = template_words.union(prompt_words)
            jaccard_sim = len(intersection) / len(union) if union else 0

            # Also use difflib for sequence matching
            seq_matcher = difflib.SequenceMatcher(None, template.prompt_template.lower(), prompt.lower())
            seq_sim = seq_matcher.ratio()

            # Combined similarity
            similarity = (jaccard_sim + seq_sim) / 2

            similarities.append((template, similarity))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return sorted(set(t.category for t in self._templates.values()))

    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        all_tags = set()
        for template in self._templates.values():
            all_tags.update(template.tags)
        return sorted(all_tags)

    def update_usage_count(self, template_name: str) -> None:
        """Increment usage count for a template."""
        if template_name in self._templates:
            self._templates[template_name].usage_count += 1
            self.save_template(self._templates[template_name])

    def get_popular_templates(self, top_k: int = 10) -> List[PromptTemplate]:
        """Get most used templates."""
        templates = list(self._templates.values())
        templates.sort(key=lambda t: t.usage_count, reverse=True)
        return templates[:top_k]

    def export_template(self, name: str, output_path: Path) -> None:
        """Export a template to a file."""
        template = self.get_template(name)
        if template:
            with open(output_path, "w") as f:
                json.dump(template.to_dict(), f, indent=2)

    def import_template(self, input_path: Path) -> PromptTemplate:
        """Import a template from a file."""
        with open(input_path, "r") as f:
            data = json.load(f)
            template = PromptTemplate.from_dict(data)
            self.add_template(template)
            return template

"""
Validation tasks for common LLM use cases.

Tasks pair prompts with their corresponding validators to create complete
LLM workflows with validation.
"""

from .base_task import BaseTask
from .code_generation import ClassGenerationTask, CodeGenerationTask, FunctionGenerationTask, ProgramGenerationTask
from .code_refactoring import CleanCodeRefactoringTask, CodeRefactoringTask, ModernizationRefactoringTask, PerformanceRefactoringTask
from .csv_generation import CSVGenerationTask
from .documentation import APIDocumentationTask, ChangelogTask, DocumentationTask, ReadmeTask, TechnicalSpecTask, TutorialTask, UserGuideTask
from .json_generation import PersonJSONTask, ProductCatalogTask
from .software_engineering import CodebaseAnalysisTask, RequirementsTask, UserStoryTask
from .story_to_scenes import StoryToScenesTask
from .test_generation import BDDTestGenerationTask, IntegrationTestGenerationTask, TestGenerationTask, UnitTestGenerationTask

__all__ = [
    "BaseTask",
    "APIDocumentationTask",
    "BDDTestGenerationTask",
    "ChangelogTask",
    "ClassGenerationTask",
    "CleanCodeRefactoringTask",
    "CodebaseAnalysisTask",
    "CodeGenerationTask",
    "CodeRefactoringTask",
    "CSVGenerationTask",
    "DocumentationTask",
    "FunctionGenerationTask",
    "IntegrationTestGenerationTask",
    "ModernizationRefactoringTask",
    "PerformanceRefactoringTask",
    "PersonJSONTask",
    "ProductCatalogTask",
    "ProgramGenerationTask",
    "ReadmeTask",
    "RequirementsTask",
    "StoryToScenesTask",
    "TechnicalSpecTask",
    "TestGenerationTask",
    "TutorialTask",
    "UnitTestGenerationTask",
    "UserGuideTask",
    "UserStoryTask",
]

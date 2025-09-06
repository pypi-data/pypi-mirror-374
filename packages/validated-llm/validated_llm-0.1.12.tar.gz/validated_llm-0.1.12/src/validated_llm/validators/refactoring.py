"""
Validator for verifying code refactoring maintains functionality while improving quality.
"""

import ast
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.validators.composite import CompositeValidator
from validated_llm.validators.syntax import SyntaxValidator


class RefactoringValidator(CompositeValidator):
    """Validates that refactored code maintains functionality while improving quality.

    This validator ensures that refactored code:
    1. Maintains syntactic correctness
    2. Preserves the original functionality (based on analysis)
    3. Shows quality improvements (readability, performance, maintainability)
    4. Follows language-specific best practices

    Example:
        ```python
        validator = RefactoringValidator(
            language="python",
            original_code=original_function_code,
            check_complexity=True,
            check_naming=True
        )

        result = validator.validate(refactored_code)
        ```
    """

    def __init__(
        self,
        language: str = "python",
        original_code: Optional[str] = None,
        check_complexity: bool = True,
        check_naming: bool = True,
        check_structure: bool = True,
        check_imports: bool = True,
        max_complexity: int = 10,
        **kwargs: Any,
    ):
        """Initialize the refactoring validator.

        Args:
            language: Programming language of the code
            original_code: The original code to compare against
            check_complexity: Whether to validate complexity improvements
            check_naming: Whether to check naming conventions
            check_structure: Whether to check code structure improvements
            check_imports: Whether to validate import organization
            max_complexity: Maximum allowed cyclomatic complexity
            **kwargs: Additional arguments for parent class
        """
        self.language = language
        self.original_code = original_code
        self.check_complexity = check_complexity
        self.check_naming = check_naming
        self.check_structure = check_structure
        self.check_imports = check_imports
        self.max_complexity = max_complexity

        # Always validate syntax first (but not in strict mode for refactoring)
        validators: List[BaseValidator] = [SyntaxValidator(language=language, strict_mode=False)]

        super().__init__(validators=validators, operator="AND", **kwargs)

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate the refactored code."""
        # First check syntax using parent class
        syntax_result = super().validate(output, context)
        if not syntax_result.is_valid:
            return syntax_result

        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"improvements": [], "preserved_functionality": True, "quality_metrics": {}}

        # Language-specific validation
        if self.language == "python":
            py_errors, py_warnings, py_metadata = self._validate_python_refactoring(output)
            errors.extend(py_errors)
            warnings.extend(py_warnings)
            metadata.update(py_metadata)
        elif self.language in ["javascript", "typescript"]:
            js_errors, js_warnings, js_metadata = self._validate_javascript_refactoring(output)
            errors.extend(js_errors)
            warnings.extend(js_warnings)
            metadata.update(js_metadata)
        else:
            # For other languages, just ensure syntax is valid
            metadata["improvements"].append("Syntax validated")

        # Check if original code was provided for comparison
        if self.original_code and not errors:
            comparison_errors, comparison_warnings, comparison_metadata = self._compare_functionality(output)
            errors.extend(comparison_errors)
            warnings.extend(comparison_warnings)
            # Don't overwrite improvements, just add new metadata
            for key, value in comparison_metadata.items():
                if key == "improvements" and key in metadata:
                    metadata[key].extend(value)
                else:
                    metadata[key] = value

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _validate_python_refactoring(self, code: str) -> Tuple[List[str], List[str], Dict[str, Any]]:
        """Validate Python-specific refactoring improvements."""
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"improvements": [], "quality_metrics": {}}

        try:
            tree = ast.parse(code)

            # Check complexity
            if self.check_complexity:
                complexity = self._calculate_complexity(tree)
                metadata["quality_metrics"]["complexity"] = complexity

                if complexity > self.max_complexity:
                    warnings.append(f"Code complexity ({complexity}) exceeds recommended maximum ({self.max_complexity})")
                else:
                    metadata["improvements"].append(f"Acceptable complexity: {complexity}")

            # Check naming conventions
            if self.check_naming:
                naming_issues = self._check_python_naming(tree)
                if naming_issues:
                    warnings.extend(naming_issues)
                else:
                    metadata["improvements"].append("Follows Python naming conventions")

            # Check structure improvements
            if self.check_structure:
                structure_improvements = self._check_python_structure(tree)
                metadata["improvements"].extend(structure_improvements)

            # Check imports
            if self.check_imports:
                import_issues = self._check_python_imports(tree)
                if import_issues:
                    warnings.extend(import_issues)
                else:
                    metadata["improvements"].append("Well-organized imports")

        except SyntaxError as e:
            errors.append(f"Syntax error in refactored code: {e}")
        except Exception as e:
            errors.append(f"Error analyzing refactored code: {e}")

        return errors, warnings, metadata

    def _validate_javascript_refactoring(self, code: str) -> Tuple[List[str], List[str], Dict[str, Any]]:
        """Validate JavaScript/TypeScript refactoring improvements."""
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"improvements": [], "quality_metrics": {}}

        # Check for modern JavaScript features
        if "var " in code:
            warnings.append("Consider using 'let' or 'const' instead of 'var'")
        else:
            metadata["improvements"].append("Uses modern variable declarations")

        # Check for arrow functions
        if "=>" in code:
            metadata["improvements"].append("Uses arrow functions")

        # Check for template literals
        if "`" in code and "${" in code:
            metadata["improvements"].append("Uses template literals")

        # Check for destructuring
        if re.search(r"const\s*{[^}]+}\s*=", code) or re.search(r"const\s*\[[^\]]+\]\s*=", code):
            metadata["improvements"].append("Uses destructuring")

        return errors, warnings, metadata

    def _compare_functionality(self, refactored_code: str) -> Tuple[List[str], List[str], Dict[str, Any]]:
        """Compare refactored code with original to ensure functionality is preserved."""
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"improvements": []}

        if not self.original_code:
            return errors, warnings, metadata

        # Extract function/class signatures
        original_signatures = self._extract_signatures(self.original_code)
        refactored_signatures = self._extract_signatures(refactored_code)

        # Check if main interfaces are preserved
        missing_signatures = set(original_signatures) - set(refactored_signatures)
        if missing_signatures:
            errors.append(f"Missing functions/classes in refactored code: {', '.join(missing_signatures)}")
            metadata["preserved_functionality"] = False
        else:
            metadata["preserved_functionality"] = True

        # Check for new additions (which might be helper functions)
        new_signatures = set(refactored_signatures) - set(original_signatures)
        if new_signatures:
            metadata["improvements"].append(f"Added helper functions/classes: {', '.join(new_signatures)}")

        return errors, warnings, metadata

    def _extract_signatures(self, code: str) -> List[str]:
        """Extract function and class signatures from code."""
        signatures = []

        if self.language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        signatures.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        signatures.append(node.name)
            except:
                pass
        elif self.language in ["javascript", "typescript"]:
            # Simple regex-based extraction for JS/TS
            function_pattern = r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)"
            class_pattern = r"class\s+(\w+)"

            for match in re.finditer(function_pattern, code):
                name = match.group(1) or match.group(2)
                if name:
                    signatures.append(name)

            for match in re.finditer(class_pattern, code):
                signatures.append(match.group(1))

        return signatures

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of Python code."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _check_python_naming(self, tree: ast.AST) -> List[str]:
        """Check Python naming conventions."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                    issues.append(f"Function '{node.name}' doesn't follow snake_case convention")
            elif isinstance(node, ast.ClassDef):
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                    issues.append(f"Class '{node.name}' doesn't follow PascalCase convention")

        return issues

    def _check_python_structure(self, tree: ast.AST) -> List[str]:
        """Check Python code structure improvements."""
        improvements = []

        # Check for docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if ast.get_docstring(node):
                    improvements.append(f"{node.__class__.__name__} '{node.name}' has docstring")

        # Check for type hints
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    improvements.append(f"Function '{node.name}' uses type hints")

        # Check for list comprehensions
        for node in ast.walk(tree):
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp)):
                improvements.append("Uses comprehensions for cleaner code")
                break

        return improvements

    def _check_python_imports(self, tree: ast.AST) -> List[str]:
        """Check Python import organization."""
        issues = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)

        # Check if imports are at the top
        if imports:
            first_import_line = imports[0].lineno
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.lineno < first_import_line:
                    issues.append("Imports should be at the top of the file")
                    break

        return issues

    @classmethod
    def get_source_code(cls) -> str:
        """Get source code for LLM prompt context."""
        return f"""RefactoringValidator: Validates code refactoring quality
- Ensures syntactic correctness
- Verifies functionality preservation
- Checks quality improvements (complexity, naming, structure)
- Language support: {", ".join(["python", "javascript", "typescript"])}
- Validates against original code when provided"""

"""
Import/Export formats for code - supporting common code exchange formats.

This module provides utilities for importing and exporting code in various formats:
- Jupyter notebooks (.ipynb)
- Markdown code blocks
- GitHub Gists format
- Code snippets with metadata (JSON)
- Docstring extraction
- Test case format
"""

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class CodeFormatter:
    """Base class for code format converters."""

    @staticmethod
    def extract_code_blocks(text: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract code blocks from markdown or other formatted text.

        Args:
            text: Text containing code blocks
            language: Optional language filter

        Returns:
            List of dicts with 'code', 'language', and 'line_number' keys
        """
        blocks = []

        # Markdown code blocks with ``` or ```language
        pattern = r"```(\w*)\n(.*?)```"
        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            lang = match.group(1) or "text"
            code = match.group(2).strip()

            if language is None or lang == language:
                blocks.append({"code": code, "language": lang, "line_number": text[: match.start()].count("\n") + 1})

        # Also check for indented code blocks (4 spaces)
        if not blocks:
            lines = text.split("\n")
            in_code_block = False
            current_block = []
            start_line = 0

            for i, line in enumerate(lines):
                if line.startswith("    ") and line.strip():
                    if not in_code_block:
                        in_code_block = True
                        start_line = i + 1
                    current_block.append(line[4:])  # Remove 4 spaces
                else:
                    if in_code_block and current_block:
                        blocks.append({"code": "\n".join(current_block), "language": language or "text", "line_number": start_line})
                        current_block = []
                        in_code_block = False

            # Don't forget last block
            if current_block:
                blocks.append({"code": "\n".join(current_block), "language": language or "text", "line_number": start_line})

        return blocks

    @staticmethod
    def to_markdown(code: str, language: str = "python", title: Optional[str] = None) -> str:
        """Convert code to markdown format.

        Args:
            code: Source code
            language: Programming language
            title: Optional title for the code block

        Returns:
            Markdown formatted string
        """
        result = []

        if title:
            result.append(f"## {title}\n")

        result.append(f"```{language}")
        result.append(code.strip())
        result.append("```")

        return "\n".join(result)

    @staticmethod
    def to_jupyter_cell(code: str, cell_type: str = "code", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert code to Jupyter notebook cell format.

        Args:
            code: Source code or markdown text
            cell_type: 'code' or 'markdown'
            metadata: Optional cell metadata

        Returns:
            Jupyter cell dictionary
        """
        cell = {"cell_type": cell_type, "metadata": metadata or {}, "source": code.strip().split("\n")}

        if cell_type == "code":
            cell["outputs"] = []
            cell["execution_count"] = None  # type: ignore

        return cell

    @staticmethod
    def to_gist_format(files: Dict[str, str], description: str = "", public: bool = False) -> Dict[str, Any]:
        """Convert code files to GitHub Gist format.

        Args:
            files: Dict mapping filenames to code content
            description: Gist description
            public: Whether gist should be public

        Returns:
            Gist-formatted dictionary
        """
        gist_files = {}

        for filename, content in files.items():
            gist_files[filename] = {"content": content}

        return {"description": description, "public": public, "files": gist_files}

    @staticmethod
    def to_snippet_format(code: str, language: str = "python", title: Optional[str] = None, description: Optional[str] = None, tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert code to snippet format with metadata.

        Args:
            code: Source code
            language: Programming language
            title: Snippet title
            description: Snippet description
            tags: List of tags
            metadata: Additional metadata

        Returns:
            Snippet dictionary
        """
        snippet = {"code": code.strip(), "language": language, "title": title or "Untitled Snippet", "description": description or "", "tags": tags or [], "metadata": metadata or {}}

        # Add code metrics
        lines = code.strip().split("\n")
        snippet["metrics"] = {"lines": len(lines), "characters": len(code), "non_empty_lines": len([l for l in lines if l.strip()])}

        return snippet


class CodeImporter:
    """Import code from various formats."""

    @staticmethod
    def from_jupyter(notebook_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Import code from Jupyter notebook.

        Args:
            notebook_path: Path to .ipynb file

        Returns:
            List of code cells with metadata
        """
        with open(notebook_path, "r") as f:
            notebook = json.load(f)

        code_cells = []

        for cell in notebook.get("cells", []):
            if cell["cell_type"] == "code":
                source = "".join(cell["source"])
                if source.strip():
                    code_cells.append(
                        {"code": source, "language": notebook.get("metadata", {}).get("kernelspec", {}).get("language", "python"), "metadata": cell.get("metadata", {}), "execution_count": cell.get("execution_count")}
                    )

        return code_cells

    @staticmethod
    def from_markdown(markdown_text: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Import code blocks from markdown.

        Args:
            markdown_text: Markdown content
            language: Optional language filter

        Returns:
            List of code blocks
        """
        return CodeFormatter.extract_code_blocks(markdown_text, language)

    @staticmethod
    def from_docstrings(python_code: str) -> List[Dict[str, Any]]:
        """Extract code examples from Python docstrings.

        Args:
            python_code: Python source code

        Returns:
            List of code examples with context
        """
        examples = []

        try:
            tree = ast.parse(python_code)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        # Look for >>> examples
                        example_lines = []
                        in_example = False

                        for line in docstring.split("\n"):
                            if line.strip().startswith(">>>"):
                                in_example = True
                                example_lines.append(line.strip()[3:].strip())
                            elif in_example and line.strip().startswith("..."):
                                example_lines.append(line.strip()[3:].strip())
                            elif in_example and not line.strip():
                                # Empty line might be part of output
                                continue
                            elif in_example and example_lines:
                                # End of example
                                examples.append({"code": "\n".join(example_lines), "language": "python", "context": f"{node.__class__.__name__}: {node.name}", "type": "doctest"})
                                example_lines = []
                                in_example = False

                        # Don't forget last example
                        if example_lines:
                            examples.append({"code": "\n".join(example_lines), "language": "python", "context": f"{node.__class__.__name__}: {node.name}", "type": "doctest"})
        except:
            pass

        return examples


class CodeExporter:
    """Export code to various formats."""

    @staticmethod
    def to_test_format(function_code: str, test_cases: List[Dict[str, Any]], language: str = "python") -> str:
        """Export code with test cases in a standard format.

        Args:
            function_code: Function source code
            test_cases: List of test case dicts with 'input', 'expected' keys
            language: Programming language

        Returns:
            Formatted test code
        """
        if language == "python":
            return CodeExporter._python_test_format(function_code, test_cases)
        elif language == "javascript":
            return CodeExporter._javascript_test_format(function_code, test_cases)
        else:
            # Generic format
            result = [function_code, "", "Test Cases:"]
            for i, tc in enumerate(test_cases, 1):
                result.append(f"Test {i}:")
                result.append(f"  Input: {tc.get('input', 'N/A')}")
                result.append(f"  Expected: {tc.get('expected', 'N/A')}")
            return "\n".join(result)

    @staticmethod
    def _python_test_format(function_code: str, test_cases: List[Dict[str, Any]]) -> str:
        """Generate Python test format."""
        # Extract function name
        try:
            tree = ast.parse(function_code)
            func_name = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    break
        except:
            func_name = "function_under_test"

        result = [function_code, "", "# Test cases", "def test_function():", f"    # Test the {func_name} function"]

        for i, tc in enumerate(test_cases, 1):
            input_val = tc.get("input", "")
            expected = tc.get("expected", "")
            result.append(f"    ")
            result.append(f"    # Test case {i}")
            result.append(f"    assert {func_name}({input_val}) == {expected}")

        result.append("")
        result.append("if __name__ == '__main__':")
        result.append("    test_function()")
        result.append("    print('All tests passed!')")

        return "\n".join(result)

    @staticmethod
    def _javascript_test_format(function_code: str, test_cases: List[Dict[str, Any]]) -> str:
        """Generate JavaScript test format."""
        # Simple regex to extract function name
        match = re.search(r"function\s+(\w+)|const\s+(\w+)\s*=", function_code)
        func_name = (match.group(1) or match.group(2)) if match else "functionUnderTest"

        result = [function_code, "", "// Test cases", f"function test{func_name.capitalize()}() {{"]

        for i, tc in enumerate(test_cases, 1):
            input_val = tc.get("input", "")
            expected = tc.get("expected", "")
            result.append(f"    // Test case {i}")
            result.append(f"    console.assert({func_name}({input_val}) === {expected}, 'Test case {i} failed');")

        result.append("    console.log('All tests passed!');")
        result.append("}")
        result.append("")
        result.append(f"test{func_name.capitalize()}();")

        return "\n".join(result)

    @staticmethod
    def to_documentation_format(code: str, language: str = "python", include_comments: bool = True) -> Dict[str, Any]:
        """Export code with extracted documentation.

        Args:
            code: Source code
            language: Programming language
            include_comments: Whether to include inline comments

        Returns:
            Dict with code structure and documentation
        """
        doc = {"language": language, "functions": [], "classes": [], "imports": [], "global_vars": [], "comments": []}

        if language == "python":
            try:
                tree = ast.parse(code)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_list = doc["functions"]
                        assert isinstance(func_list, list)
                        func_list.append({"name": node.name, "docstring": ast.get_docstring(node), "args": [arg.arg for arg in node.args.args], "line_number": node.lineno})
                    elif isinstance(node, ast.ClassDef):
                        class_list = doc["classes"]
                        assert isinstance(class_list, list)
                        class_list.append({"name": node.name, "docstring": ast.get_docstring(node), "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)], "line_number": node.lineno})
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            imports = [alias.name for alias in node.names]
                        else:
                            imports = [f"from {node.module} import {', '.join(alias.name for alias in node.names)}"]
                        import_list = doc["imports"]
                        assert isinstance(import_list, list)
                        import_list.extend(imports)
            except:
                pass

        # Extract comments
        if include_comments:
            comment_pattern = r"#\s*(.+)$" if language == "python" else r"//\s*(.+)$"
            for i, line in enumerate(code.split("\n"), 1):
                match = re.search(comment_pattern, line)
                if match:
                    comment_list = doc["comments"]
                    assert isinstance(comment_list, list)
                    comment_list.append({"text": match.group(1), "line_number": i})

        return doc

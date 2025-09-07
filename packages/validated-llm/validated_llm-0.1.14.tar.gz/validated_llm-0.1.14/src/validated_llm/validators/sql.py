"""
SQL validation for LLM outputs.
"""

import re
import sqlite3
from typing import Any, Dict, List, Optional, Set

from validated_llm.base_validator import BaseValidator, ValidationResult


class SQLValidator(BaseValidator):
    """
    Validates SQL queries in LLM output.

    Features:
    - Basic SQL syntax validation
    - Statement type detection (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)
    - SQL injection pattern detection
    - Multi-statement support
    - Common SQL dialect support
    """

    # Common SQL keywords for validation
    SQL_KEYWORDS = {
        "SELECT",
        "FROM",
        "WHERE",
        "INSERT",
        "INTO",
        "VALUES",
        "UPDATE",
        "SET",
        "DELETE",
        "CREATE",
        "TABLE",
        "DROP",
        "ALTER",
        "INDEX",
        "VIEW",
        "TRIGGER",
        "JOIN",
        "INNER",
        "LEFT",
        "RIGHT",
        "OUTER",
        "ON",
        "AS",
        "GROUP",
        "BY",
        "HAVING",
        "ORDER",
        "LIMIT",
        "OFFSET",
        "UNION",
        "ALL",
        "DISTINCT",
        "AND",
        "OR",
        "NOT",
        "IN",
        "EXISTS",
        "BETWEEN",
        "LIKE",
        "IS",
        "NULL",
        "BEGIN",
        "COMMIT",
        "ROLLBACK",
        "TRANSACTION",
        "WITH",
        "CASE",
        "WHEN",
        "THEN",
        "ELSE",
        "END",
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",
        "CAST",
    }

    # Dangerous patterns that might indicate SQL injection
    DANGEROUS_PATTERNS = [
        r";\s*DROP\s+TABLE",
        r";\s*DELETE\s+FROM\s+\w+\s*;?\s*$",  # DELETE without WHERE
        r"--\s*$",  # SQL comment at end
        r"/\*.*\*/",  # Block comments
        r"UNION\s+SELECT.*FROM\s+information_schema",
        r"OR\s+1\s*=\s*1",
        r"OR\s+['\"].*['\"]\s*=\s*['\"].*['\"]",
        r";\s*EXEC\s*\(",
        r";\s*EXECUTE\s+",
        r"xp_cmdshell",
        r"sp_executesql",
    ]

    def __init__(
        self,
        name: str = "SQLValidator",
        description: str = "Validates SQL queries",
        allowed_statements: Optional[List[str]] = None,
        blocked_statements: Optional[List[str]] = None,
        allow_multiple_statements: bool = True,
        check_syntax: bool = True,
        check_dangerous_patterns: bool = True,
        dialect: str = "sqlite",  # sqlite, mysql, postgresql
        case_sensitive: bool = False,
        require_semicolon: bool = False,
        max_query_length: Optional[int] = None,
    ):
        """
        Initialize the SQL validator.

        Args:
            name: Validator name
            description: Validator description
            allowed_statements: Whitelist of allowed SQL statement types (e.g., ['SELECT', 'INSERT'])
            blocked_statements: Blacklist of blocked SQL statement types
            allow_multiple_statements: Whether to allow multiple SQL statements
            check_syntax: Whether to perform syntax validation
            check_dangerous_patterns: Whether to check for SQL injection patterns
            dialect: SQL dialect to use for validation
            case_sensitive: Whether SQL keywords must match case
            require_semicolon: Whether statements must end with semicolon
            max_query_length: Maximum allowed query length
        """
        super().__init__(name, description)
        self.allowed_statements = set(s.upper() for s in (allowed_statements or []))
        self.blocked_statements = set(s.upper() for s in (blocked_statements or []))
        self.allow_multiple_statements = allow_multiple_statements
        self.check_syntax = check_syntax
        self.check_dangerous_patterns = check_dangerous_patterns
        self.dialect = dialect
        self.case_sensitive = case_sensitive
        self.require_semicolon = require_semicolon
        self.max_query_length = max_query_length

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate SQL queries in the output.

        Args:
            output: The LLM output containing SQL queries
            context: Optional context with additional validation parameters

        Returns:
            ValidationResult with validation status and details
        """
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"statement_types": [], "statement_count": 0, "queries": [], "dangerous_patterns_found": []}

        output = output.strip()
        if not output:
            errors.append("Output is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Check query length
        if self.max_query_length and len(output) > self.max_query_length:
            errors.append(f"Query exceeds maximum length of {self.max_query_length} characters")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Extract SQL queries (handle code blocks)
        sql_queries = self._extract_sql_queries(output)

        if not sql_queries:
            errors.append("No valid SQL queries found in output")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Check multiple statements policy
        if not self.allow_multiple_statements and len(sql_queries) > 1:
            errors.append(f"Multiple SQL statements not allowed (found {len(sql_queries)})")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        metadata["statement_count"] = len(sql_queries)

        # Validate each query
        for i, query in enumerate(sql_queries):
            query_errors = []
            query_warnings = []

            # Basic validation
            if not query.strip():
                continue

            metadata["queries"].append(query)

            # Check for semicolon requirement
            if self.require_semicolon and not query.rstrip().endswith(";"):
                query_warnings.append(f"Query {i+1} should end with semicolon")

            # Detect statement type
            statement_type = self._detect_statement_type(query)
            if statement_type:
                metadata["statement_types"].append(statement_type)

                # Check allowed/blocked statements
                if self.allowed_statements and statement_type not in self.allowed_statements:
                    query_errors.append(f"Statement type '{statement_type}' not in allowed list: {', '.join(sorted(self.allowed_statements))}")

                if self.blocked_statements and statement_type in self.blocked_statements:
                    query_errors.append(f"Statement type '{statement_type}' is blocked")
            else:
                query_warnings.append(f"Could not determine statement type for query {i+1}")

            # Check for dangerous patterns
            if self.check_dangerous_patterns:
                dangerous = self._check_dangerous_patterns(query)
                if dangerous:
                    metadata["dangerous_patterns_found"].extend(dangerous)
                    query_errors.append(f"Dangerous SQL patterns detected: {', '.join(dangerous)}")

            # Syntax validation
            if self.check_syntax:
                syntax_errors = self._validate_syntax(query)
                if syntax_errors:
                    query_errors.extend(syntax_errors)

            errors.extend(query_errors)
            warnings.extend(query_warnings)

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _extract_sql_queries(self, output: str) -> List[str]:
        """Extract SQL queries from output, handling code blocks."""
        queries = []

        # Check for SQL in code blocks
        code_block_pattern = r"```(?:sql)?\s*\n(.*?)\n\s*```"
        code_blocks = re.findall(code_block_pattern, output, re.DOTALL | re.IGNORECASE)

        if code_blocks:
            for block in code_blocks:
                # Split by semicolon but keep the semicolon
                statements = re.split(r"(;\s*(?=\n|$))", block)
                current_statement = ""
                for part in statements:
                    current_statement += part
                    if part.strip().endswith(";"):
                        if current_statement.strip():
                            queries.append(current_statement.strip())
                        current_statement = ""
                if current_statement.strip():
                    queries.append(current_statement.strip())
        else:
            # Treat entire output as SQL
            statements = re.split(r"(;\s*(?=\n|$))", output)
            current_statement = ""
            for part in statements:
                current_statement += part
                if part.strip().endswith(";"):
                    if current_statement.strip():
                        queries.append(current_statement.strip())
                    current_statement = ""
            if current_statement.strip():
                queries.append(current_statement.strip())

        return queries

    def _detect_statement_type(self, query: str) -> Optional[str]:
        """Detect the type of SQL statement."""
        query_upper = query.upper().strip()

        # Common statement starters
        statement_starters = [
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "DROP",
            "ALTER",
            "BEGIN",
            "COMMIT",
            "ROLLBACK",
            "WITH",
            "EXPLAIN",
            "SHOW",
            "DESCRIBE",
            "GRANT",
            "REVOKE",
            "TRUNCATE",
            "MERGE",
            "CALL",
            "EXECUTE",
        ]

        for starter in statement_starters:
            if query_upper.startswith(starter):
                return starter
            # Handle WITH clauses
            if starter == "WITH" and re.match(r"WITH\s+\w+\s+AS\s*\(", query_upper):
                # Find the main statement after WITH
                match = re.search(r"\)\s*(SELECT|INSERT|UPDATE|DELETE)", query_upper)
                if match:
                    return match.group(1)
                return "WITH"

        return None

    def _check_dangerous_patterns(self, query: str) -> List[str]:
        """Check for dangerous SQL patterns."""
        found_patterns = []

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                found_patterns.append(pattern)

        return found_patterns

    def _validate_syntax(self, query: str) -> List[str]:
        """Validate SQL syntax using appropriate method for dialect."""
        errors = []

        # Always run basic syntax validation first
        errors.extend(self._basic_syntax_validation(query))

        # If basic validation passed and dialect is sqlite, do deeper validation
        if not errors and self.dialect == "sqlite":
            # Use sqlite3 to check syntax
            try:
                conn = sqlite3.connect(":memory:")
                cursor = conn.cursor()
                cursor.execute("EXPLAIN " + query)
                conn.close()
            except sqlite3.Error as e:
                error_msg = str(e)
                # Clean up error message
                if "syntax error" in error_msg.lower():
                    errors.append(f"SQL syntax error: {error_msg}")
                else:
                    # Some errors might be due to missing tables, which is OK for validation
                    if "no such table" not in error_msg.lower():
                        errors.append(f"SQL validation error: {error_msg}")

        return errors

    def _basic_syntax_validation(self, query: str) -> List[str]:
        """Basic syntax validation without database connection."""
        errors = []

        # Check for balanced parentheses
        paren_count = query.count("(") - query.count(")")
        if paren_count != 0:
            errors.append(f"Unbalanced parentheses (difference: {paren_count})")

        # Check for balanced quotes
        single_quotes = query.count("'") % 2
        double_quotes = query.count('"') % 2
        if single_quotes != 0:
            errors.append("Unbalanced single quotes")
        if double_quotes != 0:
            errors.append("Unbalanced double quotes")

        # Check for common syntax patterns
        query_upper = query.upper()

        # SELECT validation
        if query_upper.startswith("SELECT"):
            if "FROM" not in query_upper and "*" not in query:
                warnings = ["SELECT statement might be missing FROM clause"]

        # INSERT validation
        if query_upper.startswith("INSERT"):
            if "INTO" not in query_upper:
                errors.append("INSERT statement missing INTO keyword")
            if "VALUES" not in query_upper and "SELECT" not in query_upper:
                errors.append("INSERT statement missing VALUES or SELECT clause")

        # UPDATE validation
        if query_upper.startswith("UPDATE"):
            if "SET" not in query_upper:
                errors.append("UPDATE statement missing SET keyword")

        # DELETE validation
        if query_upper.startswith("DELETE"):
            if "FROM" not in query_upper:
                errors.append("DELETE statement missing FROM keyword")

        return errors

    def get_validation_instructions(self) -> str:
        """Get specific validation instructions for SQL queries."""
        instructions = f"""
SQL QUERY VALIDATION REQUIREMENTS:
- Output must contain valid SQL query/queries
- SQL dialect: {self.dialect}"""

        if self.allowed_statements:
            instructions += f"\n- Allowed statement types: {', '.join(sorted(self.allowed_statements))}"

        if self.blocked_statements:
            instructions += f"\n- Blocked statement types: {', '.join(sorted(self.blocked_statements))}"

        if not self.allow_multiple_statements:
            instructions += "\n- Only ONE SQL statement is allowed"

        if self.require_semicolon:
            instructions += "\n- Each statement MUST end with a semicolon (;)"

        if self.max_query_length:
            instructions += f"\n- Maximum query length: {self.max_query_length} characters"

        if self.check_dangerous_patterns:
            instructions += "\n- Queries must not contain SQL injection patterns"

        instructions += """

Examples of valid SQL queries:
- SELECT * FROM users WHERE age > 18;
- INSERT INTO products (name, price) VALUES ('Widget', 9.99);
- UPDATE orders SET status = 'shipped' WHERE id = 123;
- CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);

Examples of invalid patterns:
- Unbalanced parentheses or quotes
- Missing required keywords (FROM, SET, etc.)
- SQL injection attempts (OR 1=1, etc.)
- Dangerous operations without conditions
"""

        return instructions

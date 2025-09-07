"""
XML validator for validating XML syntax and optional schema validation.
"""

import xml.etree.ElementTree as ET
from io import StringIO
from typing import Any, Dict, Optional
from xml.parsers.expat import ExpatError

try:
    from lxml import etree

    HAS_LXML = True
except ImportError:
    HAS_LXML = False

from validated_llm.base_validator import BaseValidator, ValidationResult


class XMLValidator(BaseValidator):
    """Validator for XML syntax and optional XML Schema (XSD) validation.

    This validator can check for:
    - Well-formed XML syntax
    - Valid XML according to an XSD schema (requires lxml)
    - Proper namespace usage
    - Required elements and attributes

    Example:
        ```python
        # Basic XML validation
        validator = XMLValidator()
        result = validator.validate('<root><item>test</item></root>')

        # With XSD schema validation (requires lxml)
        xsd_schema = '''<?xml version="1.0"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="root">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="item" type="xs:string"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema>'''

        validator = XMLValidator(xsd_schema=xsd_schema)
        result = validator.validate('<root><item>test</item></root>')
        ```
    """

    def __init__(self, xsd_schema: Optional[str] = None, require_root_element: Optional[str] = None, check_namespaces: bool = False, strict_mode: bool = True):
        """Initialize the XML validator.

        Args:
            xsd_schema: Optional XSD schema for validation (requires lxml)
            require_root_element: If specified, require this as the root element name
            check_namespaces: If True, validate namespace declarations
            strict_mode: If True, treat warnings as errors
        """
        self.xsd_schema = xsd_schema
        self.require_root_element = require_root_element
        self.check_namespaces = check_namespaces
        self.strict_mode = strict_mode

        # Parse XSD schema if provided
        self.schema_validator = None
        if xsd_schema and HAS_LXML:
            try:
                schema_doc = etree.parse(StringIO(xsd_schema))
                self.schema_validator = etree.XMLSchema(schema_doc)
            except Exception as e:
                raise ValueError(f"Invalid XSD schema: {str(e)}")
        elif xsd_schema and not HAS_LXML:
            raise ImportError("lxml is required for XSD schema validation. " "Install it with: pip install lxml")

    def validate(self, output: str, context: Optional[dict[str, Any]] = None) -> ValidationResult:
        """Validate XML output.

        Args:
            output: The XML string to validate
            context: Optional validation context

        Returns:
            ValidationResult containing any errors or warnings
        """
        llm_output = output
        errors = []
        warnings = []
        metadata: Dict[str, Any] = {}

        # Try to parse XML with ElementTree (standard library)
        try:
            root = ET.fromstring(llm_output.strip())
            metadata["root_tag"] = root.tag
            metadata["total_elements"] = len(list(root.iter()))

            # Check root element if required
            if self.require_root_element and root.tag != self.require_root_element:
                error_msg = f"Root element must be '{self.require_root_element}', " f"but got '{root.tag}'"
                if self.strict_mode:
                    errors.append(error_msg)
                else:
                    warnings.append(error_msg)

            # Basic namespace checking
            if self.check_namespaces:
                self._check_namespaces(root, errors, warnings)

        except (ET.ParseError, ExpatError) as e:
            errors.append(f"Invalid XML syntax: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # XSD schema validation if available
        if self.schema_validator and HAS_LXML:
            try:
                # Parse with lxml for schema validation
                xml_doc = etree.parse(StringIO(llm_output.strip()))

                if not self.schema_validator.validate(xml_doc):
                    # Get validation errors
                    for error in self.schema_validator.error_log:
                        error_msg = f"Schema validation error at line {error.line}: {error.message}"
                        errors.append(error_msg)
                else:
                    metadata["schema_valid"] = True

            except etree.XMLSyntaxError as e:
                errors.append(f"XML parsing error for schema validation: {str(e)}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _check_namespaces(self, root: ET.Element, errors: list, warnings: list) -> None:
        """Check for proper namespace usage.

        Args:
            root: The root XML element
            errors: List to append errors to
            warnings: List to append warnings to
        """
        # Check for namespace declarations
        namespaces = {}
        for elem in root.iter():
            # Extract namespace from tag
            if "}" in elem.tag:
                namespace = elem.tag.split("}")[0][1:]
                prefix = elem.tag.split("}")[1]
                namespaces[namespace] = prefix

        # Check attributes for namespace prefixes
        for elem in root.iter():
            for attr, value in elem.attrib.items():
                if ":" in attr and not attr.startswith("xmlns"):
                    prefix = attr.split(":")[0]
                    if prefix not in ["xml", "xsi"] and prefix not in namespaces.values():
                        warnings.append(f"Undefined namespace prefix '{prefix}' in attribute '{attr}'")

    def get_validator_description(self) -> str:
        """Get a description of this validator for LLM context."""
        desc = """XML Validator

Validates that the output is well-formed XML with:
1. Proper XML syntax (matching tags, proper nesting)
2. Valid attribute syntax
3. Proper character encoding
4. No duplicate attributes
"""

        if self.require_root_element:
            desc += f"5. Root element must be: <{self.require_root_element}>\n"

        if self.xsd_schema:
            desc += "\nThe XML must also conform to the provided XSD schema.\n"

        return desc

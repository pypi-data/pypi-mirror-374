"""Composite validator for combining multiple validators with logical operations."""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from ..base_validator import BaseValidator, ValidationResult


class LogicOperator(Enum):
    """Logical operators for combining validation results."""

    AND = "AND"
    OR = "OR"


class CompositeValidator(BaseValidator):
    """
    Combines multiple validators using logical operations (AND/OR).

    For AND operations: All validators must pass
    For OR operations: At least one validator must pass
    """

    def __init__(
        self,
        validators: List[BaseValidator],
        operator: Union[LogicOperator, str] = LogicOperator.AND,
        short_circuit: bool = True,
        aggregate_metadata: bool = True,
    ):
        """
        Initialize composite validator.

        Args:
            validators: List of validators to combine
            operator: Logic operator (AND/OR)
            short_circuit: Stop evaluation on first failure (AND) or success (OR)
            aggregate_metadata: Combine metadata from all validators
        """
        if not validators:
            raise ValueError("At least one validator must be provided")

        self.validators = validators
        self.operator = LogicOperator(operator) if isinstance(operator, str) else operator
        self.short_circuit = short_circuit
        self.aggregate_metadata = aggregate_metadata

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate content using all validators according to the logic operator.

        Args:
            output: Content to validate
            context: Optional context for validation

        Returns:
            ValidationResult with combined results
        """
        results = []
        all_errors = []
        all_warnings = []
        all_metadata: Dict[str, Any] = {}

        for i, validator in enumerate(self.validators):
            try:
                result = validator.validate(output, context)
                results.append(result)

                # Aggregate errors and warnings
                if result.errors:
                    all_errors.extend([f"Validator {i+1}: {error}" for error in result.errors])
                if result.warnings:
                    all_warnings.extend([f"Validator {i+1}: {warning}" for warning in result.warnings])

                # Aggregate metadata
                if self.aggregate_metadata and result.metadata:
                    all_metadata[f"validator_{i+1}"] = result.metadata

                # Short-circuit logic
                if self.short_circuit:
                    if self.operator == LogicOperator.AND and not result.is_valid:
                        # First failure in AND - stop processing
                        break
                    elif self.operator == LogicOperator.OR and result.is_valid:
                        # First success in OR - stop processing
                        break

            except Exception as e:
                error_msg = f"Validator {i+1} failed with exception: {str(e)}"
                all_errors.append(error_msg)

                # For AND operations, any exception is a failure
                if self.operator == LogicOperator.AND and self.short_circuit:
                    break

        # Determine overall validity based on operator
        if self.operator == LogicOperator.AND:
            # AND: All validators must pass
            is_valid = all(result.is_valid for result in results) and len(results) == len(self.validators)
        else:
            # OR: At least one validator must pass
            is_valid = any(result.is_valid for result in results)

        # Add operation metadata
        operation_metadata = {
            "operator": self.operator.value,
            "validator_count": len(self.validators),
            "results_count": len(results),
            "short_circuit": self.short_circuit,
        }

        if self.aggregate_metadata:
            all_metadata["operation"] = operation_metadata
        else:
            all_metadata = operation_metadata

        return ValidationResult(is_valid=is_valid, errors=all_errors, warnings=all_warnings, metadata=all_metadata)

    def get_description(self) -> str:
        """Get description of the composite validator."""
        validator_descriptions = [getattr(v, "get_description", lambda: "Unknown validator")() for v in self.validators]
        operator_word = "AND" if self.operator == LogicOperator.AND else "OR"
        return f"Composite validator combining {len(self.validators)} validators with {operator_word} logic: {', '.join(validator_descriptions)}"

    @classmethod
    def create_and(cls, *validators: BaseValidator, **kwargs: Any) -> "CompositeValidator":
        """Create an AND composite validator."""
        return cls(list(validators), LogicOperator.AND, **kwargs)

    @classmethod
    def create_or(cls, *validators: BaseValidator, **kwargs: Any) -> "CompositeValidator":
        """Create an OR composite validator."""
        return cls(list(validators), LogicOperator.OR, **kwargs)


class ValidationChain:
    """
    Builder pattern for creating complex validation chains.

    Allows fluent API for building composite validators:
    chain = ValidationChain().add(validator1).and_().add(validator2).or_().add(validator3)
    """

    def __init__(self) -> None:
        self._validators: List[BaseValidator] = []
        self._operators: List[LogicOperator] = []

    def add(self, validator: BaseValidator) -> "ValidationChain":
        """Add a validator to the chain."""
        self._validators.append(validator)
        return self

    def and_(self) -> "ValidationChain":
        """Add AND operator."""
        if len(self._validators) == 0:
            raise ValueError("Cannot add operator without validators")
        self._operators.append(LogicOperator.AND)
        return self

    def or_(self) -> "ValidationChain":
        """Add OR operator."""
        if len(self._validators) == 0:
            raise ValueError("Cannot add operator without validators")
        self._operators.append(LogicOperator.OR)
        return self

    def build(self, **kwargs: Any) -> CompositeValidator:
        """
        Build the composite validator from the chain.

        For complex chains with mixed operators, creates nested composites.
        For simple chains with single operator, creates single composite.
        """
        if len(self._validators) == 0:
            raise ValueError("No validators in chain")

        if len(self._validators) == 1:
            # Single validator - wrap in composite for consistency
            return CompositeValidator([self._validators[0]], LogicOperator.AND, **kwargs)

        if len(set(self._operators)) <= 1:
            # All same operator or no operators
            operator = self._operators[0] if self._operators else LogicOperator.AND
            return CompositeValidator(self._validators, operator, **kwargs)

        # Mixed operators - create nested structure
        # This is a simplified approach; could be made more sophisticated
        # For now, process left to right with AND having precedence

        result_validators: List[Union[BaseValidator, CompositeValidator]] = []
        current_and_group: List[BaseValidator] = []

        for i, validator in enumerate(self._validators):
            current_and_group.append(validator)

            # Check if next operator is OR or if we're at the end
            if i < len(self._operators):
                if self._operators[i] == LogicOperator.OR:
                    # End current AND group
                    if len(current_and_group) > 1:
                        result_validators.append(CompositeValidator(current_and_group, LogicOperator.AND))
                    else:
                        result_validators.append(current_and_group[0])
                    current_and_group = []
            else:
                # End of chain
                if len(current_and_group) > 1:
                    result_validators.append(CompositeValidator(current_and_group, LogicOperator.AND))
                elif current_and_group:
                    result_validators.append(current_and_group[0])

        # If we have multiple result validators, combine with OR
        if len(result_validators) > 1:
            # Cast to List[BaseValidator] since CompositeValidator extends BaseValidator
            base_validators: List[BaseValidator] = result_validators
            return CompositeValidator(base_validators, LogicOperator.OR, **kwargs)
        else:
            if result_validators:
                if isinstance(result_validators[0], CompositeValidator):
                    return result_validators[0]
                else:
                    return CompositeValidator([result_validators[0]], LogicOperator.AND, **kwargs)
            else:
                return CompositeValidator(self._validators, LogicOperator.AND, **kwargs)

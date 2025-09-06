"""
Async validation support for the LLM validation system.

This module provides async versions of validators and validation loops
to enable concurrent validation and better performance.
"""

import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Union

from .base_validator import BaseValidator, ValidationResult


class AsyncBaseValidator(ABC):
    """
    Abstract base class for async validators.

    Async validators can perform validation operations concurrently
    and are designed for better performance with I/O bound validation tasks.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    async def validate_async(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Async validate the LLM output and return detailed results.

        Args:
            output: The raw output from the LLM
            context: Optional context information for validation

        Returns:
            ValidationResult with validation status and detailed feedback
        """

    def get_source_code(self) -> str:
        """
        Get the source code of the validate_async method to include in LLM prompts.
        This allows the LLM to see exactly what validation criteria it needs to meet.
        """
        try:
            return inspect.getsource(self.validate_async)
        except OSError:
            # Fallback for dynamically created methods
            return f"Async Validator: {self.name}\nDescription: {self.description}"

    def get_validation_instructions(self) -> str:
        """
        Generate clear instructions for the LLM about validation requirements.
        Override this method to provide specific guidance for each validator.
        """
        return f"""
VALIDATION REQUIREMENTS for {self.name}:
{self.description}

Please ensure your output meets all the validation criteria.
If validation fails, you will receive specific error messages and be asked to correct your response.
"""


class AsyncValidatorAdapter(AsyncBaseValidator):
    """
    Adapter that wraps a synchronous BaseValidator to work in async contexts.

    This allows existing validators to be used in async validation loops
    without modification.
    """

    def __init__(self, sync_validator: BaseValidator):
        super().__init__(name=f"Async({sync_validator.name})", description=sync_validator.description)
        self.sync_validator = sync_validator

    async def validate_async(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Run the synchronous validator in a thread pool to avoid blocking.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.sync_validator.validate, output, context)

    def get_validation_instructions(self) -> str:
        """Delegate to the wrapped validator."""
        return self.sync_validator.get_validation_instructions()


class AsyncCompositeValidator(AsyncBaseValidator):
    """
    Async composite validator that combines multiple async validators.

    Can run validators concurrently for better performance.
    """

    def __init__(
        self,
        validators: List[Union[AsyncBaseValidator, BaseValidator]],
        operator: str = "AND",
        concurrent: bool = True,
        short_circuit: bool = True,
    ):
        """
        Initialize async composite validator.

        Args:
            validators: List of validators to combine
            operator: Logic operator ("AND" or "OR")
            concurrent: Whether to run validators concurrently
            short_circuit: Stop on first failure (AND) or success (OR)
        """
        names = [v.name for v in validators]
        super().__init__(name=f"AsyncComposite({operator})[{', '.join(names)}]", description=f"Combines multiple validators with {operator} logic")

        # Convert sync validators to async adapters
        self.validators: List[AsyncBaseValidator] = []
        for validator in validators:
            if isinstance(validator, AsyncBaseValidator):
                self.validators.append(validator)
            else:
                self.validators.append(AsyncValidatorAdapter(validator))

        self.operator = operator.upper()
        self.concurrent = concurrent
        self.short_circuit = short_circuit

    async def validate_async(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate using multiple validators with configurable concurrency.
        """
        if self.concurrent:
            return await self._validate_concurrent(output, context)
        else:
            return await self._validate_sequential(output, context)

    async def _validate_concurrent(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Run all validators concurrently."""
        tasks = [validator.validate_async(output, context) for validator in self.validators]

        if self.short_circuit and self.operator == "AND":
            # For AND with short circuit, use asyncio.gather with return_when=FIRST_EXCEPTION
            # But we need custom logic since we want to stop on first validation failure
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Run all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

        return self._combine_results(results)

    async def _validate_sequential(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Run validators sequentially."""
        results = []

        for validator in self.validators:
            result = await validator.validate_async(output, context)
            results.append(result)

            # Short circuit logic
            if self.short_circuit:
                if self.operator == "AND" and not result.is_valid:
                    break
                elif self.operator == "OR" and result.is_valid:
                    break

        return self._combine_results(results)

    def _combine_results(self, results: Sequence[Union[ValidationResult, BaseException]]) -> ValidationResult:
        """Combine validation results according to operator logic."""
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, ValidationResult)]

        if not valid_results:
            return ValidationResult(is_valid=False, errors=["All validators failed with exceptions"], warnings=[], metadata={"operator": self.operator, "validator_count": len(self.validators)})

        # Combine results based on operator
        if self.operator == "AND":
            is_valid = all(r.is_valid for r in valid_results)
        else:  # OR
            is_valid = any(r.is_valid for r in valid_results)

        # Combine errors and warnings
        all_errors: List[str] = []
        all_warnings: List[str] = []
        combined_metadata: Dict[str, Any] = {"operator": self.operator, "results": []}

        for i, result in enumerate(valid_results):
            validator_name = self.validators[i].name if i < len(self.validators) else f"validator_{i}"

            # Prefix errors/warnings with validator name
            prefixed_errors = [f"[{validator_name}] {error}" for error in result.errors]
            prefixed_warnings = [f"[{validator_name}] {warning}" for warning in (result.warnings or [])]

            all_errors.extend(prefixed_errors)
            all_warnings.extend(prefixed_warnings)

            combined_metadata["results"].append({"validator": validator_name, "is_valid": result.is_valid, "error_count": len(result.errors), "warning_count": len(result.warnings or [])})

        return ValidationResult(is_valid=is_valid, errors=all_errors, warnings=all_warnings, metadata=combined_metadata)

    def get_validation_instructions(self) -> str:
        """Combine validation instructions from all validators."""
        instructions = [f"COMPOSITE VALIDATION ({self.operator} logic):"]
        instructions.append(f"Concurrent execution: {self.concurrent}")
        instructions.append("")

        for i, validator in enumerate(self.validators, 1):
            instructions.append(f"{i}. {validator.get_validation_instructions()}")
            instructions.append("")

        return "\n".join(instructions)


class AsyncFunctionValidator(AsyncBaseValidator):
    """
    Async validator that wraps a callable function.

    The function can be either sync or async.
    """

    def __init__(self, func: Union[Callable[[str], bool], Callable[[str], Awaitable[bool]]], name: Optional[str] = None, description: str = "", error_message: str = "Validation failed"):
        """
        Initialize function-based async validator.

        Args:
            func: Function that takes output string and returns bool or awaitable bool
            name: Validator name (defaults to function name)
            description: Validator description
            error_message: Error message when validation fails
        """
        self.func = func
        self.error_message = error_message
        self.is_async = asyncio.iscoroutinefunction(func)

        func_name = name or getattr(func, "__name__", "anonymous_function")
        if not isinstance(func_name, str):
            func_name = "anonymous_function"
        super().__init__(name=func_name, description=description)

    async def validate_async(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate using the provided function."""
        try:
            if self.is_async:
                is_valid = await self.func(output)  # type: ignore
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                is_valid = await loop.run_in_executor(None, self.func, output)

            if is_valid:
                return ValidationResult(is_valid=True, errors=[])
            else:
                return ValidationResult(is_valid=False, errors=[self.error_message], metadata={"function": self.name})

        except Exception as e:
            return ValidationResult(is_valid=False, errors=[f"Validation function error: {str(e)}"], metadata={"function": self.name, "exception": str(e)})

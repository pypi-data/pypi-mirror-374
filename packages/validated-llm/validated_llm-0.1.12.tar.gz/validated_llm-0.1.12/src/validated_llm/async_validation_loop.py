"""
Async LLM Validation Loop implementation.

This module provides async validation capabilities with concurrent validation
and improved performance for I/O bound operations.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .async_validator import AsyncBaseValidator, AsyncFunctionValidator, AsyncValidatorAdapter
from .base_validator import BaseValidator, FunctionValidator, ValidationResult
from .config import ValidatedLLMConfig, get_config
from .llm_providers import LLMProvider, OllamaProvider, OpenAIProvider

logger = logging.getLogger(__name__)


class AsyncValidationLoop:
    """
    Async LLM validation loop with concurrent validation support.

    This class provides the same functionality as ValidationLoop but with
    async/await support for better performance and concurrent operations.
    """

    def __init__(
        self,
        vendor: Optional[str] = None,
        model: Optional[str] = None,
        default_max_retries: Optional[int] = None,
        config: Optional[ValidatedLLMConfig] = None,
        max_concurrent_validations: int = 10,
        llm_provider: Optional[LLMProvider] = None,
        **provider_kwargs: Any,
    ) -> None:
        """
        Initialize the async validation loop.

        Args:
            vendor: Name of the LLM vendor (e.g., 'ollama', 'openai', 'anthropic') (defaults to config value)
            model: Name of the model to use (defaults to config value)
            default_max_retries: Default maximum number of retry attempts (defaults to config value)
            config: Configuration object (defaults to loading from config files)
            max_concurrent_validations: Maximum number of concurrent validation operations
            llm_provider: Custom LLM provider instance (overrides vendor/model)
            **provider_kwargs: Additional parameters for LLM provider (api_key, base_url, etc.)
        """
        # Load config if not provided
        self.config = config or get_config()

        # Use provided values or fall back to config
        self.vendor = vendor or self.config.llm_vendor
        self.model = model or self.config.llm_model
        self.default_max_retries = default_max_retries or self.config.max_retries
        self.max_concurrent_validations = max_concurrent_validations

        # Initialize LLM provider
        if llm_provider is not None:
            self.llm_provider = llm_provider
        else:
            self.llm_provider = self._create_llm_provider(**provider_kwargs)

        # Semaphore to limit concurrent operations
        self._validation_semaphore = asyncio.Semaphore(max_concurrent_validations)

        # Validator registry
        self.validator_registry: Dict[str, Union[AsyncBaseValidator, BaseValidator]] = {}

    def _create_llm_provider(self, **provider_kwargs: Any) -> LLMProvider:
        """Create an LLM provider based on vendor configuration."""
        # Extract provider parameters from config and kwargs
        provider_params = {
            "model": self.model,
            "temperature": self.config.llm_temperature,
            **provider_kwargs,
        }

        if self.config.llm_max_tokens:
            provider_params["max_tokens"] = self.config.llm_max_tokens

        # Create provider based on vendor
        if self.vendor == "openai":
            return OpenAIProvider(**provider_params)
        elif self.vendor == "ollama":
            return OllamaProvider(**provider_params)
        elif self.vendor == "anthropic":
            # Use OpenAI provider with Anthropic base URL
            provider_params["base_url"] = "https://api.anthropic.com/v1"
            return OpenAIProvider(**provider_params)
        else:
            # Default to OpenAI provider for unknown vendors
            logger.warning(f"Unknown vendor '{self.vendor}', defaulting to OpenAI provider")
            return OpenAIProvider(**provider_params)

    def register_validator(self, name: str, validator: Union[AsyncBaseValidator, BaseValidator, Callable]) -> None:
        """
        Register a validator for reuse across different tasks.

        Args:
            name: Unique name for the validator
            validator: AsyncBaseValidator, BaseValidator instance, or callable function
        """
        if callable(validator) and not isinstance(validator, (AsyncBaseValidator, BaseValidator)):
            # Wrap callable in async function validator
            validator = AsyncFunctionValidator(validator, name)

        self.validator_registry[name] = validator
        logger.info(f"Registered async validator: {name}")

    def get_validator(self, name: str) -> Union[AsyncBaseValidator, BaseValidator]:
        """Get a registered validator by name."""
        if name not in self.validator_registry:
            raise ValueError(f"Validator '{name}' not found. Available: {list(self.validator_registry.keys())}")

        validator = self.validator_registry[name]
        if not isinstance(validator, (AsyncBaseValidator, BaseValidator)):
            raise TypeError(f"Expected AsyncBaseValidator or BaseValidator, got {type(validator)}")

        return validator

    async def execute(
        self,
        prompt_template: str,
        validator: Union[str, AsyncBaseValidator, BaseValidator, Callable],
        input_data: Dict[str, Any],
        max_retries: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        concurrent_validation: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute the async LLM validation loop.

        Args:
            prompt_template: Base prompt template with placeholders
            validator: Validator instance, function, or registered validator name
            input_data: Data to fill prompt template placeholders
            max_retries: Maximum retry attempts (uses default if None)
            context: Additional context for validation
            debug: Enable debug logging and output preservation
            concurrent_validation: Enable concurrent validation (for composite validators)

        Returns:
            Dictionary with execution results:
            {
                'success': bool,
                'output': str,
                'attempts': int,
                'validation_result': ValidationResult,
                'execution_time': float,
                'debug_info': Dict (if debug=True)
            }
        """
        start_time = time.time()
        max_retries = max_retries or self.default_max_retries
        debug_info: Optional[List[Dict[str, Any]]] = [] if debug else None

        # Resolve validator
        async_validator = await self._resolve_validator(validator, concurrent_validation)

        logger.info(f"Starting async LLM validation loop with validator: {async_validator.name}")

        # Build comprehensive system prompt for LLM provider
        system_prompt = self._build_system_prompt(prompt_template, async_validator, input_data)

        # Initialize validation_result for proper scoping
        validation_result: Optional[ValidationResult] = None
        cleaned_output = ""

        for attempt in range(max_retries):
            logger.info(f"Attempt {attempt + 1}/{max_retries}")

            try:
                # For first attempt, ask for the initial task
                if attempt == 0:
                    task_prompt = prompt_template.format(**input_data)
                    llm_response = await self._generate_async(system_prompt, task_prompt)
                else:
                    # For subsequent attempts, provide feedback
                    if validation_result is not None:
                        feedback_text = validation_result.get_feedback_text()
                        retry_prompt = f"""Your previous response had validation errors:
{feedback_text}

Please provide a corrected response that addresses these issues."""
                    else:
                        retry_prompt = "Please provide a corrected response."

                    llm_response = await self._generate_async(system_prompt, retry_prompt)

                if debug and debug_info is not None:
                    debug_info.append(
                        {
                            "attempt": attempt + 1,
                            "prompt": task_prompt if attempt == 0 else retry_prompt,
                            "raw_response": llm_response,
                            "timestamp": time.time(),
                        }
                    )

                # Extract and clean the output
                cleaned_output = self._extract_output(llm_response)

                # Validate the output using async validation
                async with self._validation_semaphore:
                    validation_result = await async_validator.validate_async(cleaned_output, context)

                if validation_result.is_valid:
                    execution_time = time.time() - start_time
                    logger.info(f"Async validation successful after {attempt + 1} attempt(s)")

                    result = {
                        "success": True,
                        "output": cleaned_output,
                        "attempts": attempt + 1,
                        "validation_result": validation_result,
                        "execution_time": execution_time,
                    }
                    if debug:
                        result["debug_info"] = debug_info
                    return result

                # Log validation failure for next iteration
                logger.warning(f"Async validation failed on attempt {attempt + 1}: {len(validation_result.errors)} errors")

            except Exception as e:
                logger.error(f"Error on async attempt {attempt + 1}: {str(e)}")
                if debug and debug_info is not None:
                    debug_info.append(
                        {
                            "attempt": attempt + 1,
                            "error": str(e),
                            "timestamp": time.time(),
                        }
                    )

        # All attempts failed
        execution_time = time.time() - start_time
        logger.error(f"Async validation failed after {max_retries} attempts")

        result = {
            "success": False,
            "output": cleaned_output if "cleaned_output" in locals() else "",
            "attempts": max_retries,
            "validation_result": validation_result if "validation_result" in locals() else None,
            "execution_time": execution_time,
        }
        if debug:
            result["debug_info"] = debug_info
        return result

    async def execute_batch(
        self,
        batch_requests: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple validation requests concurrently.

        Args:
            batch_requests: List of request dictionaries, each containing:
                - prompt_template: str
                - validator: validator instance or name
                - input_data: Dict[str, Any]
                - max_retries: Optional[int]
                - context: Optional[Dict[str, Any]]
                - debug: Optional[bool]
            max_concurrent: Maximum concurrent executions (defaults to class setting)

        Returns:
            List of execution results in the same order as requests
        """
        if max_concurrent is None:
            max_concurrent = self.max_concurrent_validations

        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_single(request: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                return await self.execute(**request)

        logger.info(f"Starting batch execution of {len(batch_requests)} requests")
        start_time = time.time()

        # Execute all requests concurrently
        results = await asyncio.gather(*[execute_single(request) for request in batch_requests], return_exceptions=True)

        execution_time = time.time() - start_time
        logger.info(f"Batch execution completed in {execution_time:.2f}s")

        # Convert exceptions to error results
        processed_results: List[Dict[str, Any]] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({"success": False, "output": "", "attempts": 0, "validation_result": None, "execution_time": 0.0, "error": str(result)})
            else:
                processed_results.append(result)  # type: ignore

        return processed_results

    async def _resolve_validator(self, validator: Union[str, AsyncBaseValidator, BaseValidator, Callable], concurrent_validation: bool = True) -> AsyncBaseValidator:
        """Resolve validator to AsyncBaseValidator instance."""
        resolved_validator: Union[AsyncBaseValidator, BaseValidator, Callable]

        if isinstance(validator, str):
            resolved_validator = self.get_validator(validator)
        else:
            resolved_validator = validator

        # Convert to async validator if needed
        if isinstance(resolved_validator, AsyncBaseValidator):
            return resolved_validator
        elif isinstance(resolved_validator, BaseValidator):
            return AsyncValidatorAdapter(resolved_validator)
        elif callable(resolved_validator):
            # Wrap callable in async function validator
            return AsyncFunctionValidator(resolved_validator)
        else:
            raise TypeError(f"Unsupported validator type: {type(resolved_validator)}")

    async def _generate_async(self, system_prompt: str, user_message: str) -> str:
        """
        Async wrapper for LLM provider generation.

        Runs the LLM provider's generate method in a thread pool to maintain async interface.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.llm_provider.generate, system_prompt, user_message)

    def _build_system_prompt(self, prompt_template: str, validator: AsyncBaseValidator, input_data: Dict[str, Any]) -> str:
        """Build comprehensive system prompt for LLM provider."""
        # Get validation instructions
        validation_instructions = validator.get_validation_instructions()

        # Create comprehensive system prompt
        system_prompt = f"""You are an expert assistant that provides precise, well-formatted responses according to the given instructions.

{validation_instructions}

IMPORTANT: Your responses will be automatically validated using async validation. Please ensure they exactly match the required format.

When I ask you to correct previous errors, please analyze the feedback carefully and provide an improved response that addresses all the validation issues."""

        return system_prompt

    def _extract_output(self, llm_response: str) -> str:
        """Extract the raw output from LLM response with minimal processing."""
        # Only strip whitespace - let the validator handle formatting validation
        return llm_response.strip()

    async def save_execution_log(self, result: Dict[str, Any], output_path: Path) -> None:
        """Save detailed execution log for debugging and analysis."""
        log_data = {
            "timestamp": time.time(),
            "success": result["success"],
            "attempts": result["attempts"],
            "execution_time": result["execution_time"],
            "vendor": self.vendor,
            "model": self.model,
            "async_execution": True,
        }

        if "debug_info" in result:
            log_data["debug_info"] = result["debug_info"]

        if result["validation_result"]:
            log_data["final_validation"] = {
                "is_valid": result["validation_result"].is_valid,
                "errors": result["validation_result"].errors,
                "warnings": result["validation_result"].warnings,
            }

        # Run file I/O in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self._write_log_file(log_data, output_path))

        logger.info(f"Async execution log saved to: {output_path}")

    def _write_log_file(self, log_data: Dict[str, Any], output_path: Path) -> None:
        """Write log file synchronously (to be run in thread pool)."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

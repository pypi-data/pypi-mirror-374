#!/usr/bin/env python3
"""
Example: Converting Langchain PromptTemplate to validated-llm Task.

This example demonstrates how to convert a simple Langchain prompt
to a validated task with automatic validation.
"""

# Note: This is a demonstration of how the integration would work
# Actual implementation requires langchain to be installed


def demo_langchain_conversion() -> None:
    """Demonstrate Langchain to validated-llm conversion."""

    # This is how it would work with Langchain installed:
    """
    from langchain.prompts import PromptTemplate
    from validated_llm.integrations.langchain.converter import PromptTemplateConverter
    from validated_llm.validation_loop import ValidationLoop

    # 1. Create a Langchain prompt
    langchain_prompt = PromptTemplate(
        input_variables=["product", "features"],
        template='''
        Generate a marketing description for {product} with these features:
        {features}

        Format the output as a JSON object with:
        - title: A catchy product title
        - description: 2-3 sentence description
        - benefits: List of 3 key benefits
        '''
    )

    # 2. Convert to validated-llm task
    converter = PromptTemplateConverter()

    # Analyze the prompt
    analysis = converter.analyze_prompt(langchain_prompt.template)
    print(f"Detected output type: {analysis['output_type']}")
    print(f"Suggested validators: {analysis['suggested_validators']}")

    # Convert to task
    ProductMarketingTask = converter.convert_prompt_template(
        langchain_prompt,
        task_name="ProductMarketingTask",
        validator_hints=["json", "required_fields:title,description,benefits"]
    )

    # 3. Use the task with validation
    loop = ValidationLoop(
        vendor="ollama",
        model="llama2"
    )

    result = loop.execute(
        product="Smart Water Bottle",
        features="- Tracks hydration levels\n- LED reminder lights\n- App connectivity"
    )

    print(f"Validated result: {result}")
    """

    # For now, let's show the conceptual flow
    print("Langchain to Validated-LLM Conversion Flow:")
    print("1. Create Langchain PromptTemplate with variables and template")
    print("2. Use PromptTemplateConverter to analyze the prompt")
    print("3. Converter suggests appropriate validators based on content")
    print("4. Generate a BaseTask subclass with validation")
    print("5. Execute task with ValidationLoop for automatic retry on validation failure")


if __name__ == "__main__":
    demo_langchain_conversion()

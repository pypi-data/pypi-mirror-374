"""
Story-to-scenes LLM validation task.

This task converts narrative stories into structured video scene YAML files.
It combines the prompt template and validator in a single cohesive unit.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml

from ..base_validator import BaseValidator, ValidationResult
from .base_task import BaseTask


class StoryToScenesTask(BaseTask):
    """
    Task for converting stories to scene YAML files.

    This task analyzes narrative stories and breaks them down into individual
    video scenes with detailed prompts for image generation, narration text,
    and caption overlays.
    """

    @property
    def name(self) -> str:
        return "Story to Scenes Conversion"

    @property
    def description(self) -> str:
        return "Convert narrative stories into structured video scene YAML files"

    @property
    def prompt_template(self) -> str:
        return """
You are an expert at converting narrative stories into structured video scenes for automatic video generation.

Your task is to analyze the following story and break it down into individual video scenes. Each scene will be used to generate an image, audio narration, and text caption for a video.

STORY TO CONVERT:
{story}

OUTPUT FORMAT REQUIREMENTS:
⚠️ CRITICAL: Do NOT wrap the output in markdown code blocks or backticks
⚠️ CRITICAL: Output should start directly with the YAML (starting with "- id: 1")
⚠️ CRITICAL: Do not include ```yaml at the beginning or ``` at the end
⚠️ CRITICAL: The response should be pure YAML that can be directly parsed
⚠️ CRITICAL: No markdown formatting whatsoever - just plain YAML text

CONVERSION GUIDELINES:

1. SCENE SEGMENTATION:
   - Identify natural scene boundaries (location changes, time shifts, new events)
   - Aim for 3-8 scenes for optimal video length
   - Each scene should represent a distinct visual moment

2. IMAGE PROMPTS:
   - Create detailed, visual descriptions for AI image generation
   - Focus on concrete, observable elements (settings, characters, objects, lighting)
   - ❌ NEVER include style words like "photorealistic", "cinematic", "artistic", "style" in the prompt text
   - ✅ ALWAYS use the separate 'style' field with EXACTLY one of: photorealistic, cinematic, artistic
   - Avoid abstract concepts that can't be visually represented

3. AUDIO NARRATION:
   - Extract or craft narrative text that describes what's happening
   - Use present tense and active voice
   - Keep narration natural and flowing for text-to-speech
   - Each scene should have 1-3 sentences

4. CAPTIONS:
   - Create short, impactful text overlays (1-5 words)
   - Capture the essence or key element of each scene
   - Should complement, not repeat, the narration

EXAMPLE OUTPUT FORMAT (remember - no markdown wrapping in your response):

- id: 1
  image:
    prompt: "A misty forest at dawn with towering ancient trees, soft golden light filtering through fog"
    style: "cinematic"
  audio:
    narration: "Deep in the heart of an ancient forest, morning mist dances between towering trees as the first rays of sunlight pierce the canopy."
  caption:
    text: "Ancient Forest"
    style: "elegant"

- id: 2
  image:
    prompt: "A hidden stone cottage with glowing windows nestled among the forest trees, smoke rising from chimney, warm inviting light"
    style: "photorealistic"
  audio:
    narration: "Nestled among the trees stands a forgotten cottage, its warm light beckoning travelers who dare to venture off the beaten path."
  caption:
    text: "Hidden Cottage"
    style: "elegant"

Please convert the story above into this YAML scene format. Focus on creating visually compelling scenes that tell the story effectively through images, narration, and captions.

❌ WRONG FORMAT EXAMPLE (DO NOT DO THIS):
image:
  prompt: "A forest scene with cinematic lighting and photorealistic style"  # WRONG - style info in prompt

✅ CORRECT FORMAT EXAMPLE (DO THIS):
image:
  prompt: "A forest scene with dappled sunlight filtering through trees"  # CORRECT - no style info
  style: "photorealistic"  # CORRECT - style in separate field
"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return StoryToScenesValidator


class StoryToScenesValidator(BaseValidator):
    """
    Validates that LLM output contains properly formatted scene YAML files.

    This validator checks for:
    - Valid YAML syntax
    - Required scene fields (image, audio, caption)
    - Valid field values and types
    - Proper scene numbering and structure
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the validator with configuration.

        Args:
            config_path: Path to config.yaml for style validation
        """
        super().__init__(name="story_to_scenes_validator", description="Validates YAML scene files generated from story text")

        self.config_path = config_path
        self.valid_styles = set()
        self.valid_positions = {"top", "center", "bottom"}
        self.valid_voices = {"male", "female"}
        self.valid_paces = {"slow", "moderate", "fast"}

        # Load valid styles from config if available
        if config_path and config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    if "styles" in config and "captions" in config["styles"]:
                        self.valid_styles = set(config["styles"]["captions"].keys())
            except Exception:
                # Fallback to default styles
                self.valid_styles = {"elegant", "bold", "minimal"}
        else:
            self.valid_styles = {"elegant", "bold", "minimal"}

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate the LLM-generated scenes output.

        Args:
            output: Raw LLM output containing scene YAML
            context: Optional context (story text, preferences, etc.)

        Returns:
            ValidationResult with detailed validation feedback
        """
        result = ValidationResult(is_valid=True, errors=[])

        try:
            # Try to parse as YAML
            scenes_data = yaml.safe_load(output)
        except yaml.YAMLError as e:
            result.add_error(f"Invalid YAML syntax: {str(e)}")
            return result

        # Check if output is a list of scenes
        if not isinstance(scenes_data, list):
            result.add_error("Output must be a list of scenes")
            return result

        if len(scenes_data) == 0:
            result.add_error("Must contain at least one scene")
            return result

        # Validate each scene
        for i, scene in enumerate(scenes_data, 1):
            self._validate_scene(scene, i, result)

        # Check scene numbering consistency
        self._validate_scene_numbering(scenes_data, result)

        # Add warnings for best practices
        self._add_best_practice_warnings(scenes_data, result)

        return result

    def _validate_scene(self, scene: Dict[str, Any], scene_num: int, result: ValidationResult) -> None:
        """Validate a single scene dictionary."""

        # Check if scene is a dictionary
        if not isinstance(scene, dict):
            result.add_error(f"Scene {scene_num}: Must be a dictionary/object")
            return

        # Required fields
        required_fields = ["image", "audio", "caption"]
        for field in required_fields:
            if field not in scene:
                result.add_error(f"Scene {scene_num}: Missing required field '{field}'")

        # Validate image section
        if "image" in scene:
            self._validate_image_section(scene["image"], scene_num, result)

        # Validate audio section
        if "audio" in scene:
            self._validate_audio_section(scene["audio"], scene_num, result)

        # Validate caption section
        if "caption" in scene:
            self._validate_caption_section(scene["caption"], scene_num, result)

        # Optional scene id validation
        if "id" in scene:
            if not isinstance(scene["id"], int) or scene["id"] <= 0:
                result.add_error(f"Scene {scene_num}: 'id' must be a positive integer")

    def _validate_image_section(self, image_data: Any, scene_num: int, result: ValidationResult) -> None:
        """Validate the image section of a scene."""

        if not isinstance(image_data, dict):
            result.add_error(f"Scene {scene_num}: 'image' must be a dictionary")
            return

        # Required: prompt
        if "prompt" not in image_data:
            result.add_error(f"Scene {scene_num}: image section missing 'prompt' field")
        elif not isinstance(image_data["prompt"], str) or len(image_data["prompt"].strip()) < 10:
            result.add_error(f"Scene {scene_num}: image prompt must be a descriptive string (at least 10 characters)")

        # Required: style (according to schema)
        valid_image_styles = {"photorealistic", "cinematic", "artistic"}
        if "style" not in image_data:
            result.add_error(f"Scene {scene_num}: image section missing required 'style' field")
        elif not isinstance(image_data["style"], str):
            result.add_error(f"Scene {scene_num}: image style must be a string")
        elif image_data["style"] not in valid_image_styles:
            result.add_error(f"Scene {scene_num}: image style must be one of: {', '.join(valid_image_styles)}")

        # Check that style info is NOT embedded in prompt
        if "prompt" in image_data and isinstance(image_data["prompt"], str):
            prompt_lower = image_data["prompt"].lower()
            style_keywords = ["photorealistic", "cinematic", "artistic", "style"]
            for keyword in style_keywords:
                if keyword in prompt_lower:
                    result.add_error(f"Scene {scene_num}: image prompt contains style keyword '{keyword}' - use separate 'style' field instead")

    def _validate_audio_section(self, audio_data: Any, scene_num: int, result: ValidationResult) -> None:
        """Validate the audio section of a scene."""

        if not isinstance(audio_data, dict):
            result.add_error(f"Scene {scene_num}: 'audio' must be a dictionary")
            return

        # Required: narration
        if "narration" not in audio_data:
            result.add_error(f"Scene {scene_num}: audio section missing 'narration' field")
        elif not isinstance(audio_data["narration"], str) or len(audio_data["narration"].strip()) < 5:
            result.add_error(f"Scene {scene_num}: audio narration must be a meaningful string (at least 5 characters)")

        # Optional: voice
        if "voice" in audio_data:
            if audio_data["voice"] not in self.valid_voices:
                result.add_error(f"Scene {scene_num}: audio voice must be one of: {', '.join(self.valid_voices)}")

        # Optional: pace
        if "pace" in audio_data:
            if audio_data["pace"] not in self.valid_paces:
                result.add_error(f"Scene {scene_num}: audio pace must be one of: {', '.join(self.valid_paces)}")

    def _validate_caption_section(self, caption_data: Any, scene_num: int, result: ValidationResult) -> None:
        """Validate the caption section of a scene."""

        if not isinstance(caption_data, dict):
            result.add_error(f"Scene {scene_num}: 'caption' must be a dictionary")
            return

        # Required: text
        if "text" not in caption_data:
            result.add_error(f"Scene {scene_num}: caption section missing 'text' field")
        elif not isinstance(caption_data["text"], str) or len(caption_data["text"].strip()) == 0:
            result.add_error(f"Scene {scene_num}: caption text must be a non-empty string")

        # Optional: style
        if "style" in caption_data:
            if caption_data["style"] not in self.valid_styles:
                result.add_error(f"Scene {scene_num}: caption style must be one of: {', '.join(self.valid_styles)}")

        # Optional: position
        if "position" in caption_data:
            if caption_data["position"] not in self.valid_positions:
                result.add_error(f"Scene {scene_num}: caption position must be one of: {', '.join(self.valid_positions)}")

    def _validate_scene_numbering(self, scenes: List[Dict], result: ValidationResult) -> None:
        """Validate that scene numbering is consistent."""

        # Check if all scenes have IDs
        scenes_with_ids = [scene for scene in scenes if "id" in scene]

        if scenes_with_ids:
            # If some scenes have IDs, all should have them
            if len(scenes_with_ids) != len(scenes):
                result.add_warning("Some scenes have IDs while others don't. Consider adding IDs to all scenes.")
            else:
                # Check for sequential numbering
                ids = [scene["id"] for scene in scenes_with_ids]
                expected_ids = list(range(1, len(scenes) + 1))
                if ids != expected_ids:
                    result.add_warning(f"Scene IDs are not sequential. Expected: {expected_ids}, Got: {ids}")

    def _add_best_practice_warnings(self, scenes: List[Dict], result: ValidationResult) -> None:
        """Add warnings for best practices and recommendations."""

        # Check scene count
        if len(scenes) < 3:
            result.add_warning("Consider having at least 3 scenes for better storytelling flow")
        elif len(scenes) > 10:
            result.add_warning("Very long videos (>10 scenes) may take significant time to generate")

        # Check for style consistency
        caption_styles = []
        for scene in scenes:
            if "caption" in scene and "style" in scene["caption"]:
                caption_styles.append(scene["caption"]["style"])

        if caption_styles and len(set(caption_styles)) > 2:
            result.add_warning("Consider using consistent caption styles for visual coherence")

        # Check narration lengths for balance
        narration_lengths = []
        for scene in scenes:
            if "audio" in scene and "narration" in scene["audio"]:
                narration_lengths.append(len(scene["audio"]["narration"]))

        if narration_lengths:
            avg_length = sum(narration_lengths) / len(narration_lengths)
            very_short = [i + 1 for i, length in enumerate(narration_lengths) if length < avg_length * 0.5]
            very_long = [i + 1 for i, length in enumerate(narration_lengths) if length > avg_length * 2]

            if very_short:
                result.add_warning(f"Scenes {very_short} have very short narrations - consider expanding for better pacing")
            if very_long:
                result.add_warning(f"Scenes {very_long} have very long narrations - consider shortening for better pacing")

    def get_validation_instructions(self) -> str:
        """Generate detailed instructions for the LLM about expected format."""

        return f"""
VALIDATION REQUIREMENTS FOR SCENE GENERATION:

⚠️ CRITICAL: Your response must be PURE YAML with NO markdown wrapping!
⚠️ CRITICAL: Do NOT use ```yaml or ``` in your response!
⚠️ CRITICAL: Start directly with "- id: 1"

Your output must be valid YAML containing a list of scenes. Each scene must have this exact structure:

- id: 1  # Optional but recommended: positive integer
  image:
    prompt: "Detailed visual description for AI image generation (minimum 10 characters)"
    style: "REQUIRED: photorealistic, cinematic, or artistic"
  audio:
    narration: "Text to be spoken as narration (minimum 5 characters)"
    voice: "Optional: {' or '.join(self.valid_voices)}"
    pace: "Optional: {' or '.join(self.valid_paces)}"
  caption:
    text: "Short text overlay for the scene (required)"
    style: "Optional: {' or '.join(self.valid_styles)}"
    position: "Optional: {' or '.join(self.valid_positions)}"

VALIDATION RULES:
1. Must be valid YAML syntax
2. Must be a list (array) of scene objects
3. Each scene must have: image, audio, caption sections
4. image.prompt: Descriptive text ≥10 characters for image generation (NO style info in prompt!)
5. image.style: REQUIRED field, must be: photorealistic, cinematic, or artistic
6. audio.narration: Meaningful text ≥5 characters for text-to-speech
7. caption.text: Non-empty text for video overlay
8. If using optional fields, values must be from the allowed lists above
9. Scene IDs (if used) should be sequential positive integers

BEST PRACTICES:
- Use 3-10 scenes for optimal video length
- Keep caption text concise (1-5 words)
- Make image prompts visually descriptive
- Balance narration lengths across scenes
- Use consistent caption styles

Your response will be validated against these exact requirements.
"""


# Standalone function version for backward compatibility
def validate_story_scenes_yaml(output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
    """
    Standalone function to validate story-to-scenes YAML output.

    This function can be used directly or wrapped in the FunctionValidator.
    """
    validator = StoryToScenesValidator()
    return validator.validate(output, context)

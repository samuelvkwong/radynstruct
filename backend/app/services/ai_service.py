from typing import Dict, Any, Optional, Type
import json
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel, Field, create_model
from app.core.config import settings


class AIService:
    def __init__(self):
        self.anthropic_client: Optional[Anthropic] = None
        self.openai_client: Optional[OpenAI] = None
        self.provider = self._determine_provider()

        # Initialize the appropriate client
        if self.provider == "anthropic":
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        elif self.provider == "openai":
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.provider == "ollama":
            # Ollama supports OpenAI-compatible API - reuse OpenAI client
            self.openai_client = OpenAI(
                base_url=f"{settings.OLLAMA_BASE_URL}/v1",
                api_key="ollama"  # Dummy key, Ollama doesn't require authentication
            )
        else:
            raise ValueError("No AI provider configured")

    def _determine_provider(self) -> str:
        """Auto-detect which AI provider to use"""
        # If explicitly set, use that
        if settings.AI_PROVIDER:
            provider = settings.AI_PROVIDER.lower()
            if provider not in ["anthropic", "openai", "ollama"]:
                raise ValueError(f"Invalid AI_PROVIDER: {provider}")
            return provider

        # Auto-detect based on available API keys
        if settings.ANTHROPIC_API_KEY:
            return "anthropic"
        elif settings.OPENAI_API_KEY:
            return "openai"
        else:
            # Default to Ollama (localhost) if no API keys
            return "ollama"

    def _create_pydantic_model_from_template(
        self,
        template_structure: Dict[str, Any],
        model_name: str = "RadiologyReport"
    ) -> Type[BaseModel]:
        """
        Dynamically create a Pydantic model from template structure.
        Handles nested objects recursively.
        """
        def build_field_type(field_info: Any) -> tuple:
            """Build field type and Field() for a single field"""
            if isinstance(field_info, dict):
                # Check if this is a field definition (has 'type' and 'description')
                if 'type' in field_info and 'description' in field_info:
                    description = field_info['description']
                    # All fields are Optional[str] since extraction might not find them
                    return (Optional[str], Field(default=None, description=description))
                else:
                    # This is a nested object - recursively create a model
                    nested_fields = {}
                    for key, value in field_info.items():
                        if isinstance(value, dict) and 'type' not in value:
                            # Skip type/description markers, only process actual fields
                            nested_fields[key] = build_field_type(value)
                        elif isinstance(value, dict):
                            nested_fields[key] = build_field_type(value)

                    if nested_fields:
                        nested_model = create_model(
                            f"{model_name}_{id(field_info)}",
                            **nested_fields
                        )
                        return (Optional[nested_model], Field(default=None))
                    return (Optional[str], Field(default=None))
            else:
                return (Optional[str], Field(default=None))

        # Build fields for the main model
        fields = {}
        for field_name, field_info in template_structure.items():
            fields[field_name] = build_field_type(field_info)

        # Create and return the model
        return create_model(model_name, **fields)

    async def structure_report(
        self,
        report_text: str,
        template_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to extract structured data from free-text report
        according to the provided template structure.
        Uses structured outputs with Pydantic models for guaranteed schema compliance.
        """
        # Create Pydantic model from template structure
        response_model = self._create_pydantic_model_from_template(template_structure)

        # Build prompt
        prompt = self._build_prompt(report_text, template_structure)

        try:
            if self.provider == "anthropic":
                return await self._call_anthropic(prompt, response_model)
            elif self.provider in ["openai", "ollama"]:
                # Both OpenAI and Ollama use the same client (OpenAI-compatible API)
                return await self._call_openai(prompt, response_model)
            else:
                raise ValueError(f"Unsupported AI provider: {self.provider}")
        except Exception as e:
            raise Exception(f"AI processing failed: {str(e)}")
    
    def _build_prompt(self, report_text: str, template_structure: Dict[str, Any]) -> str:
        """Build the prompt for the AI model"""
        template_fields = json.dumps(template_structure, indent=2)
        
        prompt = f"""You are a medical AI assistant specialized in structuring radiology reports.

Given the following radiology report text and template structure, extract the relevant information and return it as a structured JSON object.

RADIOLOGY REPORT:
{report_text}

TEMPLATE STRUCTURE:
{template_fields}

INSTRUCTIONS:
1. Extract information from the report that matches the template fields
2. Use null for fields where information is not found
3. Maintain medical accuracy and terminology
4. Return ONLY a valid JSON object matching the template structure
5. Do not include any explanatory text, only the JSON

RESPONSE (JSON only):"""
        
        return prompt
    
    async def _call_anthropic(self, prompt: str, response_model: Type[BaseModel]) -> Dict[str, Any]:
        """Call Anthropic's Claude API with structured outputs using tool calling"""
        # Convert Pydantic model to tool schema
        tool_schema = {
            "name": "extract_radiology_data",
            "description": "Extract structured radiology report data according to the template",
            "input_schema": response_model.model_json_schema()
        }

        message = self.anthropic_client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=2000,
            tools=[tool_schema],
            tool_choice={"type": "tool", "name": "extract_radiology_data"},
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract tool use result
        for content_block in message.content:
            if content_block.type == "tool_use":
                structured_data = content_block.input
                return {
                    "structured_data": structured_data,
                    "confidence_score": 85
                }

        raise Exception("No structured data returned from Anthropic")

    async def _call_openai(self, prompt: str, response_model: Type[BaseModel]) -> Dict[str, Any]:
        """Call OpenAI API (or Ollama with OpenAI-compatible API) with structured outputs"""

        # Use OpenAI's beta parse() method for structured outputs
        completion = self.openai_client.beta.chat.completions.parse(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a medical AI assistant specialized in structuring radiology reports."},
                {"role": "user", "content": prompt}
            ],
            response_format=response_model,
            temperature=0.1
        )

        # Extract parsed response
        parsed_response = completion.choices[0].message.parsed
        if parsed_response:
            # Convert Pydantic model to dict
            structured_data = parsed_response.model_dump(exclude_none=False)
            return {
                "structured_data": structured_data,
                "confidence_score": 85
            }

        raise Exception(f"No structured data returned from {self.provider}")

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON"""
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:
            structured_data = json.loads(response_text)
            return {
                "structured_data": structured_data,
                "confidence_score": 85  # Could be enhanced with actual confidence scoring
            }
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")


# Singleton instance
ai_service = AIService()

"""Clean translator for converting Gemini SDK responses to database models."""
import json
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
from ..intelligence_designs.llm_prompt_json_response_schema_for_time_series_prediction import LLMPromptJSONResponseSchemaForMarketPrediction
from .time_series_llm_prediction import TimeSeriesLLMPredictionResponse
from ipulse_shared_base_ftredge.enums import Currency, AIFramework
import uuid

class GeminiSDKResponseTranslator:
    """
    Clean translator between Gemini SDK responses and LLMForecastResponse database models.
    Works directly with the GenerateContentResponse and its parsed schema.
    """
    
    # Gemini API pricing (per 1M tokens) - update these as needed
    GEMINI_INPUT_COST_USD_PER_1M_TOKENS = 1.25  # $1.25 per 1M input tokens
    GEMINI_OUTPUT_COST_USD_PER_1M_TOKENS = 10.00  # $10.00 per 1M output tokens
    GEMINI_BATCHED_INPUT_COST_USD_PER_1M_TOKENS = 0.65  # $0.65 per 1M input tokens for batched requests
    GEMINI_BATCHED_OUTPUT_COST_USD_PER_1M_TOKENS = 6.00  # $6.00 per 1M output tokens for batched requests


    @classmethod
    def gemini_sdk_to_llm_response(
        cls,
        gemini_response,  # GenerateContentResponse object
        prompt_variant_id: str,
        target_object_id: str,
        target_object_name: str,
        model_version: str,
        prompt_requested_datetime_utc: datetime,
        response_received_datetime_utc: datetime,
        ai_framework: AIFramework = AIFramework.GENAI_PYTHON_SDK,
        input_timeseries_start_datetime: Optional[datetime] = None,
        input_timeseries_end_datetime: Optional[datetime] = None,
        batched: bool = False
    ) -> TimeSeriesLLMPredictionResponse:
        """
        Convert a Gemini SDK GenerateContentResponse to LLMForecastResponse database model.
        
        Args:
            gemini_response: GenerateContentResponse from Gemini SDK
            prompt_variant_id: ID of the prompt variant used
            target_object_id: ID of the target object (e.g., asset_id)
            target_object_name: Name/symbol of target object
            model_version: Version of the Gemini model used
            prompt_requested_datetime_utc: When the prompt was requested
            response_received_datetime_utc: When the response was received
            ai_framework: AIFramework used for the request (default is GENAI_PYTHON_SDK)
            input_timeseries_start_datetime: Optional start of input time series
            input_timeseries_end_datetime: Optional end of input time series
            batched: bool = False  # Whether this was a batched request (affects cost calculation)
        Returns:
            LLMForecastResponse: Database-ready model with embedded forecast points
        """
        # Extract the parsed schema directly from the response
        parsed_schema = gemini_response.parsed
        
        # Extract usage metadata
        usage_metadata = gemini_response.usage_metadata
        
        # Calculate cost
        cost_usd = cls._calculate_cost(usage_metadata, batched=batched)

        # Use forecast points directly (no conversion needed - identical models)
        forecast_points = parsed_schema.price_forecast
        
        # Determine forecast period
        forecast_start_datetime = None
        forecast_end_datetime = None
        if forecast_points:
            try:
                dates = [datetime.fromisoformat(point.forecast_date) for point in forecast_points]
                forecast_start_datetime = min(dates)
                forecast_end_datetime = max(dates)
            except (ValueError, AttributeError):
                pass
        
        # Convert key assumptions list to string
        key_assumptions_str = "; \n".join(parsed_schema.key_assumptions) if parsed_schema.key_assumptions else None
        
        # Use key risks directly (no conversion needed - identical models)
        key_risks = parsed_schema.key_risks
        
        return TimeSeriesLLMPredictionResponse(
            # Response Identity
            response_id=gemini_response.response_id or f"gemini_{uuid.uuid4()}",
            prompt_variant_id=prompt_variant_id,
            
            # Target Object Context
            target_object_id=target_object_id,
            target_object_name=target_object_name,
            
            # Model Configuration
            model_provider="google",
            model_version=gemini_response.model_version or model_version,
            ai_framework=ai_framework,
            
            # Input Context
            input_timeseries_start_datetime=input_timeseries_start_datetime,
            input_timeseries_end_datetime=input_timeseries_end_datetime,
            
            # Token Economics
            input_tokens=usage_metadata.prompt_token_count or 0,
            thinking_tokens=usage_metadata.thoughts_token_count,
            output_tokens=usage_metadata.candidates_token_count or 0,
            total_tokens_billed=usage_metadata.total_token_count or 0,
            cost_usd=cost_usd,
            
            # Request/Response Timing
            prompt_requested_datetime_utc=prompt_requested_datetime_utc,
            response_received_datetime_utc=response_received_datetime_utc,
            
            # Parsed Forecast Context
            prediction_start_datetime=forecast_start_datetime,
            forecast_end_datetime=forecast_end_datetime,
            
            # Investment Analysis Fields - directly from parsed schema
            overall_rating=parsed_schema.overall_rating,
            investment_thesis=parsed_schema.investment_thesis,
            key_assumptions=key_assumptions_str,
            key_risks=key_risks,
            
            # Forecast Metadata - directly from parsed schema
            prediction_value_type=parsed_schema.forecast_value_type,
            prediction_value_unit=parsed_schema.forecast_value_unit,
            
            # Embedded Forecast Points
            prediction_values=forecast_points,
            
            # Response Metadata
            finish_reason=gemini_response.candidates[0].finish_reason.name if gemini_response.candidates else None,
            reasoning_trace=None,  # Not provided in current response format
            error_message=None,
            retry_success=None,
            
            # Response Content
            raw_response=cls._serialize_gemini_response(gemini_response),
            
            # BaseDataModel required fields
            created_by="gemini_sdk_translator",
            updated_by="gemini_sdk_translator"
        )
    
    @classmethod
    def _calculate_cost(cls, usage_metadata, batched: bool) -> float:
        """Calculate the cost of the API call based on token usage."""
        input_tokens = usage_metadata.prompt_token_count or 0
        candidates_token_count = usage_metadata.candidates_token_count or 0
        thoughts_token_count = usage_metadata.thoughts_token_count or 0 # Includes thinking tokens
        output_tokens = candidates_token_count + thoughts_token_count
        if batched:
            input_cost = (input_tokens / 1_000_000) * cls.GEMINI_BATCHED_INPUT_COST_USD_PER_1M_TOKENS
            output_cost = (output_tokens / 1_000_000) * cls.GEMINI_BATCHED_OUTPUT_COST_USD_PER_1M_TOKENS
        else:
            input_cost = (input_tokens / 1_000_000) * cls.GEMINI_INPUT_COST_USD_PER_1M_TOKENS
            output_cost = (output_tokens / 1_000_000) * cls.GEMINI_OUTPUT_COST_USD_PER_1M_TOKENS
        
        return input_cost + output_cost
    
    @classmethod
    def _serialize_gemini_response(cls, gemini_response) -> Dict[str, Any]:
        """Convert GenerateContentResponse to a serializable dictionary."""
        try:
            # Extract the key information in a serializable format
            return {
                "response_id": gemini_response.response_id,
                "model_version": gemini_response.model_version,
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"text": part.text if hasattr(part, 'text') else str(part)}
                                for part in candidate.content.parts
                            ],
                            "role": candidate.content.role
                        },
                        "finish_reason": candidate.finish_reason.name,
                        "index": candidate.index
                    }
                    for candidate in gemini_response.candidates
                ],
                "usage_metadata": {
                    "prompt_token_count": gemini_response.usage_metadata.prompt_token_count,
                    "candidates_token_count": gemini_response.usage_metadata.candidates_token_count,
                    "thoughts_token_count": gemini_response.usage_metadata.thoughts_token_count,
                    "total_token_count": gemini_response.usage_metadata.total_token_count
                },
                "parsed_schema_present": gemini_response.parsed is not None
            }
        except Exception as e:
            # Fallback to string representation if serialization fails
            return {
                "error": f"Serialization failed: {str(e)}",
                "raw_string": str(gemini_response)
            }
    
    @classmethod
    def validate_gemini_sdk_response(cls, gemini_response) -> bool:
        """
        Validate that a Gemini SDK response has the expected structure.
        
        Args:
            gemini_response: GenerateContentResponse from Gemini SDK
            
        Returns:
            bool: True if structure is valid, False otherwise
        """
        try:
            # Check if we have the parsed schema
            if not hasattr(gemini_response, 'parsed') or gemini_response.parsed is None:
                return False
            
            # Check if we have usage metadata
            if not hasattr(gemini_response, 'usage_metadata') or gemini_response.usage_metadata is None:
                return False
                
            # Check if we have candidates
            if not hasattr(gemini_response, 'candidates') or not gemini_response.candidates:
                return False
                
            # Check if parsed schema is the expected type
            if not isinstance(gemini_response.parsed, LLMPromptJSONResponseSchemaForMarketPrediction):
                return False
            
            return True
            
        except Exception:
            return False

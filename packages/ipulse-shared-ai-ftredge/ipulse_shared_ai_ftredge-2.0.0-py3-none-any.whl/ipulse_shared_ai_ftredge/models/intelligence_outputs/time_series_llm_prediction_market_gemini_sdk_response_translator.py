"""Clean translator for converting Gemini SDK responses to market asset prediction models."""
import json
import uuid
from typing import Dict, Any, Optional, Union
from datetime import datetime
from ..intelligence_designs.llm_prompt_json_response_schema_for_time_series_prediction import LLMPromptJSONResponseSchemaForMarketPrediction
from .time_series_llm_prediction_market_asset import TimeSeriesLLMPredictionMarketAsset, PredictionValuePointMarketAsset
from .time_series_prediction_base import PredictionValuePointBase
from .helpers.market_key_risks import StockKeyRisks, CryptoKeyRisks, CommodityKeyRisks, ETFKeyRisks
from ipulse_shared_base_ftredge.enums import (
    AIFramework, ProgressStatus, AIModelStatus, TimeFrame,
    FincoreProductCategoryDetailed, ContractType, SectorCategory, SectorRecordsCategory
)


class TimeSeriesMarketLLMPredictionGeminiSDKResponseTranslator:
    """
    Translator for converting Gemini SDK responses to TimeSeriesLLMPredictionMarketAsset models.
    Specifically designed for market asset predictions.
    All asset classification parameters must be provided from request context.
    """

    # Gemini API pricing (per 1M tokens) - update these as needed
    GEMINI_INPUT_COST_USD_PER_1M_TOKENS = 1.25
    GEMINI_OUTPUT_COST_USD_PER_1M_TOKENS = 10.00
    GEMINI_BATCHED_INPUT_COST_USD_PER_1M_TOKENS = 0.65
    GEMINI_BATCHED_OUTPUT_COST_USD_PER_1M_TOKENS = 6.00

    @classmethod
    def convert_gemini_response_to_market_prediction(
        cls,
        gemini_response,  # GenerateContentResponse object
        # Request Context - Asset Classification (must be provided)
        asset_category_detailed: FincoreProductCategoryDetailed,
        asset_contract_type: ContractType,
        object_category: Union[str, SectorCategory],
        prediction_step_timeframe: TimeFrame,
        # Request Context - Prediction Identity
        prompt_variant_id: str,
        target_object_id: str,
        target_object_name: str,
        # Request Context - Model & Framework
        ai_framework: AIFramework,
        model_provider: str,
        model_name: str,
        model_version_id: str,
        # Request Context - Timing
        prediction_requested_datetime_utc: datetime,
        prediction_received_datetime_utc: datetime,
        # Request Context - Input Data Window (optional)
        input_data_start_datetime: Optional[Union[datetime, str]] = None,
        input_data_end_datetime: Optional[Union[datetime, str]] = None,
        # Request Context - User & Environment
        created_by: str = "system",
        prediction_environment: str = "production",
        # Request Context - Cost & Batching
        batched: bool = False,
    ) -> TimeSeriesLLMPredictionMarketAsset:
        """
        Convert a Gemini SDK GenerateContentResponse to TimeSeriesLLMPredictionMarketAsset model.
        All asset classification parameters are provided from request context.
        
        Args:
            gemini_response: GenerateContentResponse from Gemini SDK
            asset_category_detailed: Specific asset category (from request context)
            asset_contract_type: Contract type (from request context)
            object_category: High-level object category (from request context)
            prediction_step_timeframe: Time frequency of predictions (from request context)
            prompt_variant_id: ID of the prompt variant used
            target_object_id: ID of the target object (e.g., asset_id)
            target_object_name: Name/symbol of target object
            ai_framework: AIFramework used for the request
            model_provider: AI model provider (e.g., 'google')
            model_name: Name of the AI model (e.g., 'Gemini')
            model_version_id: Version of the AI model
            prediction_requested_datetime_utc: When the prediction was requested
            prediction_received_datetime_utc: When the response was received
            input_data_start_datetime: Optional start of input time series
            input_data_end_datetime: Optional end of input time series
            created_by: User/system that created this prediction
            prediction_environment: Environment where prediction was made
            batched: Whether this was a batched request (affects cost calculation)
            
        Returns:
            TimeSeriesLLMPredictionMarketAsset: Complete prediction model ready for storage
        """
        try:
            # Validate response structure
            if not cls._validate_gemini_response(gemini_response):
                raise ValueError("Invalid Gemini SDK response structure")

            # Extract the parsed schema directly from the response
            parsed_schema = gemini_response.parsed
            
            # Extract usage metadata
            usage_metadata = gemini_response.usage_metadata
            
            # Calculate cost
            cost_usd = cls._calculate_cost(usage_metadata, batched=batched)

            # Convert prediction points from Gemini schema to base model format
            # Note: Using PredictionValuePointBase due to inheritance constraints,
            # but this is still appropriate for market predictions
            base_prediction_points = [
                PredictionValuePointBase(
                    prediction_timestamp_utc=point.prediction_date,
                    prediction_value=point.prediction_value,
                    prediction_value_upper_bound=point.prediction_value_upper_bound,
                    prediction_value_lower_bound=point.prediction_value_lower_bound,
                    prediction_confidence_score=point.confidence_score
                )
                for point in parsed_schema.price_prediction
            ]
            
            # Determine prediction period from data
            prediction_start_datetime = None
            prediction_end_datetime = None
            if base_prediction_points:
                try:
                    dates = [
                        datetime.fromisoformat(str(point.prediction_timestamp_utc)) 
                        for point in base_prediction_points
                    ]
                    prediction_start_datetime = min(dates)
                    prediction_end_datetime = max(dates)
                except (ValueError, AttributeError):
                    pass
            
            # Convert key assumptions list to string
            key_assumptions_str = None
            if parsed_schema.key_assumptions:
                key_assumptions_str = "; ".join(parsed_schema.key_assumptions)
            
            # Create asset-specific risk model based on asset category
            key_risks = cls._create_asset_specific_risks(parsed_schema, asset_category_detailed)
            
            return TimeSeriesLLMPredictionMarketAsset(
                # Core Identity (from base class)
                prediction_id=gemini_response.response_id or f"gemini_{uuid.uuid4()}",
                prediction_ai_model_status=AIModelStatus.SERVING,
                
                # Target Context (from request context)
                target_object_id=target_object_id,
                target_object_name=target_object_name,
                target_object_domain="market_prediction",
                object_sector=SectorRecordsCategory.MARKET,
                object_category=object_category,
                
                # AI Framework Context (from request context)
                ai_framework=ai_framework,
                model_provider=model_provider,
                model_name=model_name,
                model_version_id=model_version_id,
                
                # Input Data Context (from request context)
                input_values_oldest_timestamp_utc=input_data_start_datetime,
                input_data_recent_timestamp_utc=input_data_end_datetime,
                
                # Prediction Context and Cost
                prediction_status=ProgressStatus.DONE,
                prediction_requested_datetime_utc=prediction_requested_datetime_utc,
                prediction_received_datetime_utc=prediction_received_datetime_utc,
                prediction_latency_ms=(
                    prediction_received_datetime_utc - prediction_requested_datetime_utc
                ).total_seconds() * 1000,
                prediction_cost_usd=cost_usd,
                
                # Value Context
                prediction_values_start_timestamp_utc=prediction_start_datetime,
                prediction_values_end_timestamp_utc=prediction_end_datetime,
                prediction_steps_count=len(base_prediction_points),
                prediction_step_timeframe=prediction_step_timeframe,
                prediction_value_type=parsed_schema.prediction_value_type,
                prediction_value_unit=parsed_schema.prediction_value_unit,
                prediction_values=base_prediction_points,
                
                # Status & Error Handling
                prediction_error=None,
                
                # LLM-Specific Identity
                prompt_variant_id=prompt_variant_id,
                
                # Token Economics (LLM-specific)
                input_tokens=usage_metadata.prompt_token_count or 0,
                thinking_tokens=usage_metadata.thoughts_token_count,
                output_tokens=usage_metadata.candidates_token_count or 0,
                total_tokens_billed=usage_metadata.total_token_count or 0,
                
                # LLM-Specific Response Metadata
                finish_reason=(
                    gemini_response.candidates[0].finish_reason.name 
                    if gemini_response.candidates else None
                ),
                reasoning_trace=None,  # Not provided in current response format
                retry_success=None,
                
                # LLM Response Content
                raw_response=cls._serialize_gemini_response(gemini_response),
                
                # Market-Specific Fields (from request context)
                asset_category_detailed=asset_category_detailed,
                asset_contract_type=asset_contract_type,
                overall_rating=parsed_schema.overall_rating,
                investment_thesis=parsed_schema.investment_thesis,
                key_assumptions=key_assumptions_str,
                key_risks=key_risks,
                volatility_assessment=None,  # Not provided in current schema
                
                # Metadata
                tags={},  # Keep tags empty for market predictions
                prediction_metadata={
                    "gemini_response_id": gemini_response.response_id,
                    "model_version": model_version_id,
                    "prediction_environment": prediction_environment
                },
                
                # BaseDataModel required fields
                created_by=created_by,
                updated_by=created_by
            )
            
        except Exception as e:
            # Return error response with provided context
            return TimeSeriesLLMPredictionMarketAsset(
                # Core Identity
                prediction_id=f"error_{uuid.uuid4()}",
                prediction_ai_model_status=AIModelStatus.FAILED,
                
                # Target Context (from request context)
                target_object_id=target_object_id,
                target_object_name=target_object_name,
                target_object_domain="market_prediction",
                object_sector=SectorRecordsCategory.MARKET,
                object_category=object_category,
                
                # AI Framework Context
                ai_framework=ai_framework,
                model_provider=model_provider,
                model_name=model_name,
                model_version_id=model_version_id,
                
                # Input Data Context
                input_values_oldest_timestamp_utc=input_data_start_datetime,
                input_data_recent_timestamp_utc=input_data_end_datetime,
                
                # Prediction Context and Cost
                prediction_status=ProgressStatus.FAILED,
                prediction_requested_datetime_utc=prediction_requested_datetime_utc,
                prediction_received_datetime_utc=prediction_received_datetime_utc,
                prediction_latency_ms=(
                    prediction_received_datetime_utc - prediction_requested_datetime_utc
                ).total_seconds() * 1000,
                prediction_cost_usd=0.0,
                
                # Value Context
                prediction_values_start_timestamp_utc=None,
                prediction_values_end_timestamp_utc=None,
                prediction_steps_count=0,
                prediction_step_timeframe=prediction_step_timeframe,
                prediction_value_type="price",
                prediction_value_unit="USD",
                prediction_values=[],
                
                # Status & Error Handling
                prediction_error=f"Error processing Gemini response: {str(e)}",
                
                # LLM-Specific Identity
                prompt_variant_id=prompt_variant_id,
                
                # Token Economics (defaults)
                input_tokens=0,
                thinking_tokens=None,
                output_tokens=0,
                total_tokens_billed=0,
                
                # LLM-Specific Response Metadata
                finish_reason="ERROR",
                reasoning_trace=None,
                retry_success=False,
                
                # LLM Response Content
                raw_response={"error": str(e)},
                
                # Market-Specific Fields (from request context)
                asset_category_detailed=asset_category_detailed,
                asset_contract_type=asset_contract_type,
                overall_rating=None,
                investment_thesis=None,
                key_assumptions=None,
                key_risks=None,
                volatility_assessment=None,
                
                # Metadata
                tags={},  # Keep tags empty even for error cases
                prediction_metadata={"error_details": str(e)},
                
                # BaseDataModel required fields
                created_by=created_by,
                updated_by=created_by
            )

    @classmethod
    def _create_asset_specific_risks(cls, parsed_schema, asset_category_detailed: FincoreProductCategoryDetailed):
        """Create the appropriate risk model based on asset category."""
        try:
            # Extract base risk fields that are common to all models
            base_risks = {
                'regulatory_risks': parsed_schema.key_risks.regulatory_risks,
                'macroeconomic_risks': parsed_schema.key_risks.macroeconomic_risks,
                'political_geopolitical_risks': parsed_schema.key_risks.political_geopolitical_risks,
                'climate_risks': parsed_schema.key_risks.climate_risks,
            }
            
            # Map asset category to appropriate risk model
            if asset_category_detailed in [FincoreProductCategoryDetailed.CRYPTO_COIN, FincoreProductCategoryDetailed.CRYPTO_TOKEN, FincoreProductCategoryDetailed.STABLECOIN, FincoreProductCategoryDetailed.DEFI_GOV_TOKEN]:
                crypto_specific_risks = {
                    'adoption_risks': parsed_schema.key_risks.adoption_risks,
                    'security_risks': parsed_schema.key_risks.security_risks,
                    'volatility_risks': parsed_schema.key_risks.volatility_risks,
                    'liquidity_risks': parsed_schema.key_risks.liquidity_risks,
                }
                return CryptoKeyRisks(**base_risks, **crypto_specific_risks)
                
            elif asset_category_detailed in [FincoreProductCategoryDetailed.PRECIOUS_METAL, FincoreProductCategoryDetailed.INDUSTRIAL_METAL, FincoreProductCategoryDetailed.ENERGY, FincoreProductCategoryDetailed.AGRICULTURE]:
                commodity_specific_risks = {
                    'supply_demand_imbalance_risks': parsed_schema.key_risks.supply_demand_imbalance_risks,
                    'producer_risks': parsed_schema.key_risks.producer_risks,
                    'substitute_risks': parsed_schema.key_risks.substitute_risks,
                    'inventory_risks': parsed_schema.key_risks.inventory_risks,
                }
                return CommodityKeyRisks(**base_risks, **commodity_specific_risks)
                
            elif asset_category_detailed in [FincoreProductCategoryDetailed.EQUITY_FUND, FincoreProductCategoryDetailed.BOND_FUND, FincoreProductCategoryDetailed.COMMODITY_FUND, FincoreProductCategoryDetailed.INDEX_FUND]:
                etf_specific_risks = {
                    'counterparty_risks': parsed_schema.key_risks.counterparty_risks,
                    'management_risks': parsed_schema.key_risks.management_risks,
                    'expense_and_fees_risks': parsed_schema.key_risks.expense_and_fees_risks,
                    'closure_risks': getattr(parsed_schema.key_risks, 'closure_risks', None),
                }
                return ETFKeyRisks(**base_risks, **etf_specific_risks)
            else:
                # Default to stock risks for common stocks, REITs, etc.
                stock_specific_risks = {
                    'competitive_risks': parsed_schema.key_risks.competitive_risks,
                    'operational_execution_risks': parsed_schema.key_risks.operational_execution_risks,
                    'management_risks': parsed_schema.key_risks.management_risks,
                    'earnings_risks': parsed_schema.key_risks.earnings_risks,
                    'sector_specific_risks': parsed_schema.key_risks.sector_specific_risks,
                }
                return StockKeyRisks(**base_risks, **stock_specific_risks)
                
        except (AttributeError, TypeError):
            # Fallback with defaults - use appropriate model for the asset category
            if asset_category_detailed in [FincoreProductCategoryDetailed.CRYPTO_COIN, FincoreProductCategoryDetailed.CRYPTO_TOKEN, FincoreProductCategoryDetailed.STABLECOIN, FincoreProductCategoryDetailed.DEFI_GOV_TOKEN]:
                return CryptoKeyRisks(
                    regulatory_risks="Risk data unavailable",
                    macroeconomic_risks="Risk data unavailable", 
                    political_geopolitical_risks="Risk data unavailable",
                    climate_risks="Risk data unavailable",
                    adoption_risks="Risk data unavailable",
                    security_risks="Risk data unavailable",
                    volatility_risks="Risk data unavailable",
                    liquidity_risks="Risk data unavailable"
                )
            elif asset_category_detailed in [FincoreProductCategoryDetailed.PRECIOUS_METAL, FincoreProductCategoryDetailed.INDUSTRIAL_METAL, FincoreProductCategoryDetailed.ENERGY, FincoreProductCategoryDetailed.AGRICULTURE]:
                return CommodityKeyRisks(
                    regulatory_risks="Risk data unavailable",
                    macroeconomic_risks="Risk data unavailable", 
                    political_geopolitical_risks="Risk data unavailable",
                    climate_risks="Risk data unavailable",
                    supply_demand_imbalance_risks="Risk data unavailable",
                    producer_risks="Risk data unavailable",
                    substitute_risks="Risk data unavailable",
                    inventory_risks="Risk data unavailable"
                )
            elif asset_category_detailed in [FincoreProductCategoryDetailed.EQUITY_FUND, FincoreProductCategoryDetailed.BOND_FUND, FincoreProductCategoryDetailed.COMMODITY_FUND, FincoreProductCategoryDetailed.INDEX_FUND]:
                return ETFKeyRisks(
                    regulatory_risks="Risk data unavailable",
                    macroeconomic_risks="Risk data unavailable", 
                    political_geopolitical_risks="Risk data unavailable",
                    climate_risks="Risk data unavailable",
                    counterparty_risks="Risk data unavailable",
                    management_risks="Risk data unavailable",
                    expense_and_fees_risks="Risk data unavailable",
                    closure_risks=None
                )
            else:
                # Default to stock risks
                return StockKeyRisks(
                    regulatory_risks="Risk data unavailable",
                    macroeconomic_risks="Risk data unavailable", 
                    political_geopolitical_risks="Risk data unavailable",
                    climate_risks="Risk data unavailable",
                    competitive_risks="Risk data unavailable",
                    operational_execution_risks="Risk data unavailable",
                    management_risks="Risk data unavailable",
                    earnings_risks="Risk data unavailable",
                    sector_specific_risks="Risk data unavailable"
                )

    @classmethod
    def _calculate_cost(cls, usage_metadata, batched: bool) -> float:
        """Calculate the cost of the API call based on token usage."""
        input_tokens = usage_metadata.prompt_token_count or 0
        candidates_token_count = usage_metadata.candidates_token_count or 0
        thoughts_token_count = usage_metadata.thoughts_token_count or 0
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
            return {
                "error": f"Serialization failed: {str(e)}",
                "raw_string": str(gemini_response)
            }

    @classmethod
    def _validate_gemini_response(cls, gemini_response) -> bool:
        """Validate that a Gemini SDK response has the expected structure."""
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


# Alias for backward compatibility (if needed)
TimeSeriesLLMPredictionGeminiSDKResponseTranslator = TimeSeriesMarketLLMPredictionGeminiSDKResponseTranslator

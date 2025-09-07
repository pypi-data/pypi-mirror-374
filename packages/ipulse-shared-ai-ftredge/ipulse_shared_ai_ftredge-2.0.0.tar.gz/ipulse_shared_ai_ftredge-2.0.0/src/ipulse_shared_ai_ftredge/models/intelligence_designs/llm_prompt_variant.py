"""Pydantic model for LLM prompt variants and templates."""
from typing import ClassVar, Dict, Any, Optional, Literal
from pydantic import Field
from datetime import datetime
from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge import ObjectOverallStatus

class LLMPromptVariant(BaseDataModel):
    """
    LLM prompt variant model for managing prompt templates and configurations.
    This is the dimension table for all LLM prompt variations and their parameters.
    """
    VERSION: ClassVar[float] = 2.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "llmpromptvariant"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )
    
    # --- Prompt Identity ---
    prompt_variant_id: str = Field(..., description="The unique identifier for this prompt variant.")
    encoded_name: str = Field(..., description="URL-safe encoded name for this prompt variant.")
    name: str = Field(..., description="Human-readable name for this prompt variant.")
    version: int = Field(..., description="Version number of this prompt variant.")
    description: str = Field(..., description="Detailed description of this prompt variant's purpose and use case.")
    created_at_prompt: datetime = Field(..., description="Timestamp when this prompt variant was created.")
    pulse_status: ObjectOverallStatus = Field(..., description="Lifecycle status: ACTIVE, DISABLED, DEPRECATED.")
    
    # --- Prompt Instructions ---
    prompt_system_instruction: Optional[str] = Field(None, description="System instruction/context for the LLM (where applicable).")
    prompt_base_text_instruction: str = Field(..., description="Core text instruction for the prompt.")
    prompt_response_json_format_specification: Optional[str] = Field(None, description="JSON schema specification for expected response format.")
    
    # --- Historical Context Configuration ---
    historical_timeseries_context_type: Optional[Literal[
        "None", 
        "max_history_monthly_close", 
        "last_10Y_monthly_close", 
        "last_5Y_weekly_close",
        "last_6M_daily_close",
        "custom_range"
    ]] = Field(None, description="Type of historical time series context to include in prompt.")
    
    # --- Research Configuration ---
    use_deep_research: bool = Field(default=False, description="Whether to include additional research context in the prompt.")
    
    # --- LLM Generation Parameters ---
    max_output_tokens: Optional[int] = Field(None, description="Maximum number of output tokens for response generation.")
    temperature: Optional[float] = Field(None, description="Temperature parameter for response generation (0.0 to 2.0).")
    top_p: Optional[float] = Field(None, description="Top-p parameter for nucleus sampling (0.0 to 1.0).")
    
    # --- Metadata ---
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization and filtering.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for this prompt variant.")

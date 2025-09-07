"""Base model for all time series LLM predictions."""
from typing import ClassVar, Dict, Any, Optional, List, Union
from pydantic import Field, BaseModel
from datetime import datetime
from ipulse_shared_base_ftredge.enums import ProgressStatus
from .time_series_prediction_base import TimeSeriesPredictionBase



class TimeSeriesLLMPredictionBase(TimeSeriesPredictionBase):
    """
    Base model for all time series LLM predictions.
    Contains only LLM-specific fields that extend the common prediction base.
    Version 1.0: LLM-specific architecture extending common base.
    """
    VERSION: ClassVar[float] = 1.0
    OBJ_REF: ClassVar[str] = "tsllmpredbase"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )
    
    # --- LLM-Specific Identity ---
    prompt_variant_id: str = Field(..., description="ID of the prompt variant used")
    
    # --- Token Economics (LLM-specific) ---
    input_tokens: int = Field(default=0, description="Number of input tokens")
    thinking_tokens: Optional[int] = Field(None, description="Number of thinking/reasoning tokens")
    output_tokens: int = Field(default=0, description="Number of output tokens")
    total_tokens_billed: int = Field(default=0, description="Total tokens billed")
    

    # --- LLM-Specific Response Metadata ---
    finish_reason: Optional[str] = Field(None, description="Reason the prediction completed")
    reasoning_trace: Optional[str] = Field(None, description="LLM reasoning trace if available")
    retry_success: Optional[bool] = Field(None, description="Whether this was a successful retry")
    
    # --- LLM Response Content ---
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Raw response from LLM")

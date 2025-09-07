"""Common base model for all time series predictions (LLM and Quant)."""
from typing import ClassVar, Dict, Any, Optional, Union, List
from pydantic import Field
from datetime import datetime
from pydantic import BaseModel
from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge.enums import AIFramework, SectorCategory, SectorRecordsCategory, AIModelStatus, ProgressStatus,TimeFrame


class PredictionValuePointBase(BaseModel):
    """
    Base prediction point with financial analysis.
    """
    prediction_timestamp_utc: Union[datetime, str] = Field(..., description="Timestamp of the prediction in datetime utc format or YYYY-MM-DD format")
    prediction_value: float = Field()
    prediction_value_upper_bound: float = Field(..., description="Upper bound of the prediction confidence interval")
    prediction_value_lower_bound: float = Field(..., description="Lower bound of the prediction confidence interval")
    prediction_confidence_score: float = Field(..., description="Confidence score of the prediction")
    


class TimeSeriesPredictionBase(BaseDataModel):
    """
    Common base class for all time series predictions.
    Contains fields that apply to ANY time series prediction, regardless of method (LLM or Quant).
    Version 1.0: Unified base architecture for extensible prediction types.
    """
    VERSION: ClassVar[float] = 1.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "tspredbase"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )
    
    # --- Core Identity ---
    prediction_id: str = Field(..., description="Unique identifier for this prediction")
    prediction_ai_model_status : AIModelStatus = Field(..., description="Current lifecycle status of the AI model used, ie Training , Validation, Serving..")
    # --- Target Context ---
    target_object_id: str = Field(..., description="ID of the object being predicted")
    target_object_name: str = Field(..., description="Name of the object being predicted")
    target_object_domain: Optional[str] = Field(None, description="Domain of the predicted object")
    object_sector: Optional[Union[str, SectorRecordsCategory]] = Field(None, description="Object sector, like MARKET, FUNDAMENTAL, etc.")
    object_category: Optional[Union[str, SectorCategory]] = Field(None, description="Category: 'EQUITY', 'FIXED_INCOME', 'Commodity', etc.")
    
    # --- AI Framework Context ---
    ai_framework: AIFramework = Field(..., description="AI framework/method used")
    model_provider: str = Field(..., description="AI model provider (e.g., 'google', 'openai')")
    model_name: str = Field(..., description="Readable Name of the AI model")
    model_version_id: str = Field(..., description="Version of the AI model. For internal model this comes from AIModelVersion")
    

    # --- Input Data Context (Unified naming) ---
    input_values_oldest_timestamp_utc:  Optional[Union[datetime, str]] = Field(None, 
        description="Start datetime of input data window used")
    input_data_recent_timestamp_utc:  Optional[Union[datetime, str]] = Field(None, 
        description="End datetime of input data window used")   
    
    # --- Prediction Context and Cost---
    prediction_status: ProgressStatus = Field(..., description="Status of the prediction generation process.")
    prediction_requested_datetime_utc: datetime = Field(..., description="When prediction was requested")
    prediction_received_datetime_utc: datetime = Field(..., description="When response was received")
    prediction_latency_ms: Optional[float] = Field(None, description="Time taken to generate prediction in milliseconds")
    prediction_cost_usd: Optional[float] = Field(None, description="Cost of prediction in USD")

    # --- Value Context ---
    prediction_values_start_timestamp_utc: Optional[Union[datetime, str]] = Field(None, description="Start of prediction horizon,Timestamp in datetime or YYYY-MM-DD format ")
    prediction_values_end_timestamp_utc: Optional[Union[datetime, str]] = Field(None, description="End of prediction horizon,Timestamp in datetime or YYYY-MM-DD format ")
    prediction_steps_count: int = Field(..., description="Number of time steps predicted.")
    prediction_step_timeframe: TimeFrame = Field(..., description="Time frequency of predictions.")
    prediction_value_type: Optional[str] = Field(None, description="Type of value being predicted")
    prediction_value_unit: Optional[str] = Field(None, description="Unit/dimension of predicted values")
    prediction_values: List[PredictionValuePointBase] = Field(default_factory=list, 
        description="List of prediction points with timestamps and values")
    

    # --- Status & Error Handling (Generic) ---
    prediction_error: Optional[str] = Field(None, description="Error message if prediction failed")
    
    # --- Metadata ---
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Tags for categorization and filtering")
    prediction_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        extra = "forbid"  # Prevent unexpected fields

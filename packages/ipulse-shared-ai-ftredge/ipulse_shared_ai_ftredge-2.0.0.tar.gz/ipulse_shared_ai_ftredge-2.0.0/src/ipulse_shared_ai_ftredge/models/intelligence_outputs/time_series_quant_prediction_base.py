"""Pydantic model for time series forecasting results."""
from typing import ClassVar, Dict, Any, Optional, List, Tuple
from pydantic import Field
from datetime import datetime
from ipulse_shared_base_ftredge import AIModelStatus, TimeFrame
from .time_series_prediction_base import TimeSeriesPredictionBase


class TimeSeriesQuantPredictionBase(TimeSeriesPredictionBase):
    """
    Time series forecasting results model extending the common prediction base.
    Focused specifically on quantitative time series predictions with numerical data.
    """
    VERSION: ClassVar[float] = 2.0
    OBJ_REF: ClassVar[str] = "timeseriesforecast"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )
    
    # --- Quant-Specific Input Context ---
    input_features_used: Dict[str, Any] = Field(..., description="The input features/data used to generate prediction.")
    feature_store_version: Optional[str] = Field(None, description="Version of feature store used.")

    
    # --- CONFIDENCE & UNCERTAINTY (Quant-specific) --- TO BE CHECKED IF CANT BE WITHIN PREDICTION VALUES 
    prediction_uncertainty_bounds: Optional[List[Tuple[float, float]]] = Field(
        None, description="Upper and lower bounds for each predicted value."
    )
    # prediction_variance: Optional[List[float]] = Field(None, description="Variance estimates for each prediction.")
    # prediction_std_dev: Optional[List[float]] = Field(None, description="Standard deviation for each prediction.")
    # prediction_confidence_intervals: Optional[List[float]] = Field(
    #     None, description="Confidence interval widths."
    # )
    
    # --- TIME SERIES DECOMPOSITION ---
    trend_component: Optional[List[float]] = Field(None, description="Trend component for this prediction.")
    seasonal_component: Optional[List[float]] = Field(None, description="Seasonal component for this prediction.")
    residual_component: Optional[List[float]] = Field(None, description="Residual component for this prediction.")
    seasonality_strength: Optional[float] = Field(None, description="Strength of seasonality detected.")
    trend_strength: Optional[float] = Field(None, description="Strength of trend detected.")
        
    # --- Quality and Performance (Quant-specific) ---
    anomaly_flags: Optional[List[bool]] = Field(None, description="Boolean flags for anomalous prediction points.")
    uncertainty_scores: Optional[List[float]] = Field(None, description="Uncertainty scores for each prediction point.")
    
    # --- Compute Resources ---
    compute_resources_used: Optional[Dict[str, Any]] = Field(None, description="Compute resources used.")

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal
from ipulse_shared_base_ftredge.enums import Currency, AssetRating


class KeyRisks(BaseModel):
    regulatory_risks: str
    competitive_risks: str
    operational_execution_risks: str
    macroeconomic_risks: str
    political_geopolitical_risks: str
    climate_risks: str


class PredictionValuePoint(BaseModel):
    """
    Individual price prediction point from LLM predictions.
    Embedded within LLMPredictionResponse for BigQuery optimization.
    """
    # --- Prediction Point Data ---
    prediction_date: str = Field(..., description="Date of the prediction in ISO format (YYYY-MM-DD).")
    prediction_value: float = Field(..., description="Primary predicted value.")
    prediction_value_upper_bound: float = Field(..., description="Upper bound of the prediction confidence interval.")
    prediction_value_lower_bound: float = Field(..., description="Lower bound of the prediction confidence interval.")
    confidence_score: float = Field(..., description="Confidence score between 0 and 1.")
    milestones_and_events: str = Field(..., description="Key milestones and events affecting this prediction point.")

class LLMPromptJSONResponseSchemaForMarketPrediction(BaseModel):
    """
    Pydantic model for parsing the expected LLM JSON response structure.
    Use this to validate and parse raw LLM responses before storing in database.
    """
    ticker: str = Field(..., description="Ticker of what the object for which prediction is made (e.g., 'APPL').")
    prediction_value_type: Literal["adjusted_close"] = Field(..., description="Description of what is being predicted (e.g., 'adjusted_close').")
    prediction_value_unit: Currency = Field(..., description="Unit/dimension of the predicted values (e.g., Currency.USD).")
    overall_rating: AssetRating = Field(..., description="Overall analyst rating for the asset (e.g., 'BUY', 'HOLD').")
    investment_thesis: str
    key_assumptions: List[str]
    key_risks: KeyRisks
    price_prediction: List[PredictionValuePoint]
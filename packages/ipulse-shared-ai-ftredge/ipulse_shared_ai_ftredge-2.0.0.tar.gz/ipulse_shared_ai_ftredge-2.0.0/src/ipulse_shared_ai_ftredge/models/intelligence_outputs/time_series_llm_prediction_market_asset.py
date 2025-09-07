"""Market-specific time series LLM prediction model."""
from typing import ClassVar, Dict, Any, Optional, List, Literal, Union
from pydantic import Field, BaseModel
from datetime import datetime
from ipulse_shared_base_ftredge.enums import Unit, AssetRating, ProgressStatus, SectorCategory, FincoreProductCategoryDetailed, ContractType
from .time_series_llm_prediction_base import TimeSeriesLLMPredictionBase
from .helpers.market_key_risks import (
    BaseMarketKeyRisks,
    StockKeyRisks, 
    CryptoKeyRisks, 
    CommodityKeyRisks, 
    ETFKeyRisks
)


class PredictionValuePointMarketAsset(BaseModel):
    """
    Market-specific prediction point with financial analysis.
    """

    prediction_timestamp_utc: Union[datetime,str] = Field(..., description="Timestamp of the prediction in datetime utc or YYYY-MM-DD format")
    prediction_value: float = Field()
    prediction_value_upper_bound: float = Field(..., description="Upper bound of the prediction confidence interval")
    prediction_value_lower_bound: float = Field(..., description="Lower bound of the prediction confidence interval")
    prediction_confidence_score: float = Field(..., description="Confidence score of the prediction")
    milestones_and_events: str = Field(..., description="Key milestones and events affecting this prediction point")
    technical_factors: Optional[str] = Field(None, description="Technical analysis factors")
    fundamental_factors: Optional[str] = Field(None, description="Fundamental analysis factors")



class TimeSeriesLLMPredictionMarketAsset(TimeSeriesLLMPredictionBase):
    """
    Market-specific time series LLM prediction model.
    Specialized for asset price predictions (stocks, crypto, commodities).
    Inherits all generic fields and adds market-specific analysis.
    Version 1.0: Market prediction specialization.
    """
    VERSION: ClassVar[float] = 1.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction_market"
    OBJ_REF: ClassVar[str] = "tsllmpredmarkt"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )
    
    # Override target category to be market-specific
    
    asset_category_detailed: FincoreProductCategoryDetailed = Field(..., description="Category: COMMON_STOCK, PREFERRED_STOCK, GOVERNMENT_BOND, PRECIOUS_METAL etc.")
    asset_contract_type: ContractType = Field(..., description="Financial instrument being predicted (e.g., stock ticker)")

    # --- Market-Specific Analysis Fields ---
    overall_rating: Optional[AssetRating] = Field(None, 
        description="Overall analyst rating for the asset (BUY, HOLD, SELL)")
    investment_thesis: Optional[str] = Field(None, 
        description="Investment thesis provided by the LLM")
    key_assumptions: Optional[str] = Field(None, 
        description="Key assumptions underlying the prediction")
    key_risks: Optional[Union[StockKeyRisks, CryptoKeyRisks, CommodityKeyRisks, ETFKeyRisks]] = Field(None,
        description="Asset-specific risk analysis based on asset type")
    volatility_assessment: Optional[str] = Field(None, description="Volatility analysis")
        
    @classmethod
    def get_firestore_collection_name(cls) -> str:
        """Return the table name for market predictions."""
        return "timeseries_llm_predictions"  # Same table as base, different fields populated

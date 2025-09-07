"""Specialized risk models for different market asset types."""
from typing import Optional
from pydantic import BaseModel, Field


class BaseMarketKeyRisks(BaseModel):
    """Base class for all market-specific risk models."""
    regulatory_risks: str = Field(..., description="Regulatory risks affecting the asset")
    macroeconomic_risks: str = Field(..., description="Macroeconomic risks")
    political_geopolitical_risks: str = Field(..., description="Political and geopolitical risks")
    climate_risks: str = Field(..., description="Climate and environmental risks")


class StockKeyRisks(BaseMarketKeyRisks):
    """Risk model specifically for stock/equity investments."""
    competitive_risks: str = Field(..., description="Competitive risks in the sector/industry")
    operational_execution_risks: str = Field(..., description="Company operational execution risks")
    management_risks: str = Field(..., description="Management and leadership risks")
    earnings_risks: str = Field(..., description="Earnings volatility and guidance risks")
    sector_specific_risks: str = Field(..., description="Industry/sector-specific risks")


class CryptoKeyRisks(BaseMarketKeyRisks):
    """Risk model specifically for cryptocurrency investments."""
    adoption_risks: str = Field(..., description="Market adoption and network effect risks")
    security_risks: str = Field(..., description="Security vulnerabilities and hacking risks")
    volatility_risks: str = Field(..., description="Extreme price volatility risks")
    liquidity_risks: str = Field(..., description="Market liquidity and exchange risks")


class CommodityKeyRisks(BaseMarketKeyRisks):
    """Risk model specifically for commodity investments."""
    supply_demand_imbalance_risks: str = Field(..., description="Supply and demand imbalance risks")
    producer_risks: str = Field(..., description="Major producer and supplier concentration risks")
    substitute_risks: str = Field(..., description="Substitute products and alternatives risks")
    inventory_risks: str = Field(..., description="Global inventory levels and stockpile risks")


class ETFKeyRisks(BaseMarketKeyRisks):
    """Risk model specifically for ETF (Exchange-Traded Fund) investments."""
    counterparty_risks: str = Field(..., description="Counterparty and issuer risks")
    management_risks: str = Field(..., description="Fund management and operational risks")
    expense_and_fees_risks: str = Field(..., description="Fee structure and expense impact risks")
    closure_risks: Optional[str] = Field(None, description="ETF closure or merger risks")
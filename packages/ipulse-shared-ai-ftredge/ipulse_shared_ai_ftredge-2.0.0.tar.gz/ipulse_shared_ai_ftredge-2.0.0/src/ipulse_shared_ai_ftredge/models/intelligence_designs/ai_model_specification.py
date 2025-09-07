# pylint: disable=missing-module-docstring, missing-class-docstring, line-too-long, invalid-name
from typing import List, Optional, Dict, Any, ClassVar, Literal
from pydantic import Field
from datetime import datetime

from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge import (
    AILearningParadigm,
    AIArchitectureFamily,
    RegressionAlgorithm,
    ClassificationAlgorithm,
    TimeSeriesAlgorithm,
)


class AIModelSpecification(BaseDataModel):
    """
    Represents a specific AI/ML model's specification and configuration.
    This is a blueprint for a model, independent of any specific training run.
    """

    VERSION: ClassVar[float] = 2.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "aimodel"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )

    model_spec_id: str = Field(..., description="The unique identifier for this AI model, often matching the asset ID.")
    model_spec_name: str = Field(..., description="The name of the AI model, e.g., 'ARIMA_v1'.")
    target_object_id: str = Field(..., description="The unique identifier of the Predictable Object this model is trained for.")
    target_object_name: str = Field(..., description="The short name of the Predictable Object for easy reference.")
    target_object_domain: str = Field(..., description="The domain of the Predictable Object this model is trained for.")
    
    # --- Model Classification (Supervised Learning + Foundation Models) ---
    learning_paradigm: AILearningParadigm = Field(default=AILearningParadigm.SUPERVISED, description="Always supervised for this application.")
    ai_architecture_family: AIArchitectureFamily = Field(..., description="The supervised learning family: Regression, Classification, Time Series, or Foundation Model.")
    
    # --- Model Source ---
    model_source: Literal["internal", "external_foundational", "open_source_finetuned", "external_service"] = Field(..., description="Source and training approach: 'internal' (built from scratch), 'foundational' (API-based LLM), 'open_source_finetuned' (open-source base + our training), 'cloud_service' (cloud provider's ML service).")

    # --- Foundation Model Fields (Only for foundational models) ---
    foundation_model_provider: Optional[str] = Field(None, description="Provider of the foundational model, e.g., 'openai', 'google', 'anthropic'.")
    foundation_model_family: Optional[str] = Field(None, description="Model family, e.g., 'gpt-4', 'gemini-pro', 'claude-3'.")
    foundation_model_api_endpoint: Optional[str] = Field(None, description="API endpoint for the foundational model.")
    foundation_model_pricing_usd: Optional[Dict[str, float]] = Field(None, description="Pricing structure, e.g., {'input_tokens': 0.01, 'output_tokens': 0.03}.")
    
    # --- Open Source + Fine-tuning Fields (Only for open_source_finetuned) ---
    base_model_source: Optional[str] = Field(None, description="Source of base model, e.g., 'huggingface', 'tensorflow_hub', 'pytorch_hub'.")
    base_model_name: Optional[str] = Field(None, description="Name of base model, e.g., 'microsoft/DialoGPT-medium', 'google/flan-t5-base'.")
    base_model_version: Optional[str] = Field(None, description="Version of base model used.")
    
    # --- External Service Fields (Only for cloud_service) ---
    external_service_provider: Optional[str] = Field(None, description="Service provider, e.g., 'gcp', 'aws', 'azure', 'openai', 'xai'.")
    external_service_name: Optional[str] = Field(None, description="Specific service, e.g., 'bigquery_ml', 'vertex_ai', 'sagemaker', 'databricks_ml'.")
    external_service_model_type: Optional[str] = Field(None, description="Service model type, e.g., 'ARIMA_PLUS', 'AUTOML_FORECASTING', 'XGBOOST'.")
    external_service_endpoint: Optional[str] = Field(None, description="Service endpoint or model resource identifier.")

    # --- Algorithm Selection (All model sources - algorithm varies by type) ---
    algorithm: Optional[
        RegressionAlgorithm | 
        ClassificationAlgorithm | 
        TimeSeriesAlgorithm
    ] = Field(None, description="The underlying algorithm used. For foundational models, this represents their core architecture (e.g., TRANSFORMER for GPT).")

    # --- Training & Features ---
    ml_architecture_name: str = Field(..., description="A user-defined name for the specific model architecture, e.g., 'ARIMA_v1'.")
    parameters_count: Optional[int] = Field(..., description="The number of parameters in the model, used for complexity assessment.")
    hyperparameters_schema: Optional[Dict[str, Any]] = Field(None, description="The hyperparameters used to train the model, e.g.,'learning_rate', 'batch_size', epochs, optimizer, dropout_rate, activation_function...")
    feature_input_schema: Optional[Dict[str, Any]] = Field(None, description="The input schema for the model, e.g., {'type': 'object', 'properties': {'feature1': {'type': 'number'}, ...}}.")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="The output schema of the model, e.g., {'type': 'object', 'properties': {'prediction': {'type': 'number'}}}.")
    model_framework: Optional[Dict[str, Any]] = Field(None, description="Information about the model framework, e.g., TensorFlow, PyTorch, Scikit-learn.")
    model_description: Optional[str] = Field(None, description="A detailed description of the model, its purpose, and its architecture.")
    
     # --- Metadata ---
    author: str = Field(..., description="The author or team responsible for the model.")
    model_provider_organization: List[str] = Field(..., description="The provider of the model, e.g., 'OpenAI', 'Google'.")
    model_license: Optional[str] = Field(None, description="The license under which the model is released, e.g., 'MIT', 'Apache 2.0'.")
    model_rights_description: Optional[str] = Field(None, description="A description of the rights associated with the model, e.g., 'Open for research use only'.")
    model_conceived_on: Optional[datetime] = Field(..., description="The timestamp when the model was created.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization, e.g., 'production', 'experimental'.")
    model_performance_score: Optional[float] = Field(None, description="A performance score for the model, e.g., accuracy, F1 score, RMSE.")
    latest_episode_id: Optional[str] = Field(None, description="The ID of the latest training or prediction episode for this model.")
    total_known_episodes: int = Field(0, description="The total number of training or prediction episodes associated with this model.")

    # --- Episodes & Packaging --- # Below is COMMENTED OUT , BECAUSE THERE ARE POTENTIALLY MANY EPISODES FOR A SINGLE MODEL
    notes: Optional[str] = Field(None, description="Any additional notes about this model specification.")
    strengths: Optional[str] = Field(None, description="A description of the strengths of the model specification, e.g., 'High accuracy on recent data'.")
    weaknesses: Optional[str] = Field(None, description="A description of the weaknesses of the model specification, e.g., 'Struggles with outliers'.")
    recommended_use_cases: Optional[List[str]] = Field(None, description="Recommended use cases for this model specification.")
    recommended_consumer: Optional[str] = Field(None, description="Who/what requested this prediction, e.g., 'trading_system', 'user_dashboard'.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization, e.g., 'production', 'experimental'.")

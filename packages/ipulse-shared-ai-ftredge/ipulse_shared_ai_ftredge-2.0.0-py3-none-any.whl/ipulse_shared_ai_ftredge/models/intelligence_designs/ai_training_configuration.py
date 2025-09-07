# pylint: disable=missing-module-docstring, missing-class-docstring, line-too-long, invalid-name
from typing import List, Optional, Dict, Any, ClassVar, Tuple
from pydantic import Field
from datetime import datetime

from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge import TimeFrame, DatasetScope, AIModelUpdateType, AIModelStatus



class AITrainingConfiguration(BaseDataModel):
    """
    Represents a reusable training configuration template for a specific AIModel.
    This defines HOW to train a model but not the execution details of any specific training run.
    Think of this as a "training recipe" that can be applied multiple times.
    """

    VERSION: ClassVar[float] = 2.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "aitrainingconfig"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )

    training_config_id: str = Field(..., description="The unique identifier for this training configuration episode.")
    model_spec_id: str = Field(..., description="The UID of the AIModel this episode belongs to.")
    target_object_id: Optional[str] = Field(..., description="The unique identifier of the Predictable Object this model is trained for.")
    target_object_name: Optional[str] = Field(..., description="The short name of the Predictable Object for easy reference.")
    target_object_domain: Optional[str] = Field(..., description="The domain of the Predictable Object this model is trained for.")
    training_config_short_name: str = Field(..., description="A short name for this training configuration, e.g., 'Big model with cost_optimized retraining'.")
    # --- Training Data Scope ---
    training_dataset_scope: Optional[DatasetScope] = Field(..., description="The type of data subset used for training etc.")
    training_dataset_oldest_datetime: Optional[datetime] = Field(..., description="The start datetime of the training data.")
    training_dataset_recent_datetime: Optional[datetime] = Field(..., description="The end datetime of the training data.")
    training_dataset_count: Optional[int] = Field(..., description="The number of records in the training data subset.")
    training_dataset_version: Optional[str] = Field(..., description="The source of the training data, e.g., 'historical market data', 'synthetic data'.")

    # --- Hyperparameters and Training Strategy ---
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="The precise hyperparameters used for training the model.")
    training_and_update_strategy: Optional[Tuple[AIModelUpdateType, TimeFrame]] = Field(..., description="The training strategy : Full retraining every N days, fine tuning every F days, State update every... etc.")
    training_stopping_criteria: Optional[str] = Field(..., description="The criteria used to stop training, e.g., 'Early stopping based on validation loss'.")
    
    # --- Expected Performance and Cost ---
    training_config_performance_score: Optional[float] = Field(None, description="Expected or average performance score for this configuration.")
    training_config_avg_monthly_cost: Optional[float] = Field(None, description="Expected average monthly cost of this training configuration.")
    training_config_avg_performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Expected average performance metrics for this configuration.")
    # --- General ---
    notes: Optional[str] = Field(None, description="Any additional notes about this episode, e.g., 'Initial training with default parameters'.")
    strengths: Optional[str] = Field(None, description="A description of the strengths of the model after this episode, e.g., 'High accuracy on recent data'.")
    weaknesses: Optional[str] = Field(None, description="A description of the weaknesses of the model after this episode, e.g., 'Struggles with outliers'.")
    recommended_use_cases: Optional[List[str]] = Field(None, description="Recommended use cases for this training configuration.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization, e.g., 'production', 'experimental'.")
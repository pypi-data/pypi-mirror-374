# pylint: disable=missing-module-docstring, missing-class-docstring, line-too-long, invalid-name
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import Field
from datetime import datetime

from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge import TimeFrame, DatasetScope, AIModelUpdateType, AIModelStatus


class AITrainingRun(BaseDataModel):
    """
    Represents a single execution instance of training based on a specific AITrainingConfiguration.
    This captures the actual runtime details, timing, costs, and immediate results of a training execution.
    """

    VERSION: ClassVar[float] = 2.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "aitrainingrun"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )

    # --- Identifiers and Relationships ---
    training_run_id: str = Field(..., description="The unique identifier for this specific training run execution.")
    training_config_id: str = Field(..., description="Reference to the AITrainingConfiguration that defined this run.")
    model_spec_id: str = Field(..., description="Reference to the AIModelSpecification being trained.")
    target_object_id: str = Field(..., description="The unique identifier of the Predictable Object this model is trained for.")
    target_object_name: str = Field(..., description="The short name of the Predictable Object for easy reference.")
    target_object_domain: str = Field(..., description="The domain of the Predictable Object this model is trained for.")
    experiment_id: Optional[str] = Field(None, description="Experiment ID for grouping related training runs.")
    parent_run_id: Optional[str] = Field(None, description="Parent training run ID if this is a continuation or fine-tuning.")

    # --- Execution Context ---
    run_name: str = Field(..., description="Human-readable name for this training run, e.g., 'AAPL_daily_retrain_2024_08_06'.")
    run_environment: str = Field(..., description="Environment where training was executed, e.g., 'production', 'staging', 'development'.")
    compute_environment: Optional[Dict[str, Any]] = Field(None, description="Details about compute resources used, e.g., instance type, GPU, memory.")
    
    # --- Training Data Details ---
    training_dataset_version: str = Field(..., description="Specific version/hash of the training dataset used.")
    feature_store_version: Optional[str] = Field(None, description="Version of the feature store snapshot used.")
    training_data_lineage: Optional[Dict[str, Any]] = Field(None, description="Detailed lineage of training data sources and transformations.")
    actual_training_data_count: int = Field(..., description="Actual number of records used in training after any filtering.")
    validation_data_count: Optional[int] = Field(None, description="Number of records in validation set, if used.")
    test_data_count: Optional[int] = Field(None, description="Number of records in test set, if used.")

    # --- Execution Timing ---
    training_start_datetime: datetime = Field(..., description="Timestamp when the training process started.")
    training_end_datetime: Optional[datetime] = Field(None, description="Timestamp when the training process concluded.")
    training_duration_seconds: Optional[float] = Field(None, description="Total training duration in seconds.")
    
    # --- Training Process Details ---
    hyperparameters_used: Optional[Dict[str, Any]] = Field(None, description="Actual hyperparameters used if different from configuration. Only populated when runtime parameters differ from the training configuration template.")
    training_stopping_reason: Optional[str] = Field(None, description="Reason training stopped, e.g., 'convergence', 'early_stopping', 'max_epochs'.")
    epochs_completed: Optional[int] = Field(None, description="Number of training epochs completed.")
    best_epoch: Optional[int] = Field(None, description="Epoch that produced the best validation performance.")
    
    # --- Cost and Resource Tracking ---
    training_run_cost: Optional[float] = Field(None, description="Cost of this specific training run in USD.")
    compute_hours: Optional[float] = Field(None, description="Total compute hours consumed.")
    peak_memory_usage_gb: Optional[float] = Field(None, description="Peak memory usage during training in GB.")
    
    # --- Model Output and Artifacts ---
    model_artifact_id: Optional[str] = Field(None, description="Identifier for the serialized model artifact produced.")
    model_artifact_location: Optional[str] = Field(None, description="Storage location of the trained model artifact.")
    model_artifact_size_mb: Optional[float] = Field(None, description="Size of the model artifact in MB.")
    checkpoint_locations: Optional[List[str]] = Field(None, description="List of checkpoint storage locations saved during training.")
    
    # --- Performance Metrics ---
    final_training_loss: Optional[float] = Field(None, description="Final training loss value.")
    final_validation_loss: Optional[float] = Field(None, description="Final validation loss value.")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Detailed performance metrics from this run.")
    convergence_metrics: Optional[Dict[str, Any]] = Field(None, description="Metrics tracking convergence behavior.")
    
    # --- Status and State ---
    run_status: AIModelStatus = Field(..., description="Current status of this training run.")
    error_message: Optional[str] = Field(None, description="Error message if training failed.")
    warnings: Optional[List[str]] = Field(None, description="List of warnings encountered during training.")
    
    # --- Reproducibility ---
    random_seed: Optional[int] = Field(None, description="Random seed used for reproducibility.")
    code_version: Optional[str] = Field(None, description="Git commit hash or version of training code used.")
    framework_version: Optional[Dict[str, str]] = Field(None, description="Versions of ML frameworks used, e.g., {'tensorflow': '2.13.0'}.")
    
    # --- Metadata ---
    triggered_by: Optional[str] = Field(None, description="What triggered this training run, e.g., 'scheduled', 'manual', 'drift_detected'.")
    notes: Optional[str] = Field(None, description="Additional notes about this specific training run.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization and filtering.")

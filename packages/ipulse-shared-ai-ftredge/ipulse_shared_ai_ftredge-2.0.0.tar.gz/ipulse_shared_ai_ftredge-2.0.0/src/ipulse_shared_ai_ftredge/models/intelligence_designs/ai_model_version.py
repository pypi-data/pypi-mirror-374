# pylint: disable=missing-module-docstring, missing-class-docstring, line-too-long, invalid-name
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import Field
from datetime import datetime

from ipulse_shared_core_ftredge.models import BaseDataModel
from ipulse_shared_base_ftredge import AIModelStatus


class AIModelVersion(BaseDataModel):
    """
    Represents a specific version of a trained AI model that is ready for deployment or evaluation.
    This is the versioned artifact produced by successful training runs.
    """

    VERSION: ClassVar[float] = 2.0
    DOMAIN: ClassVar[str] = "papp_oracle_fincore_prediction"
    OBJ_REF: ClassVar[str] = "aimodelversion"

    schema_version: float = Field(
        default=VERSION,
        frozen=True,
        description="Version of this Class == version of DB Schema"
    )

    # --- Identifiers and Relationships ---
    model_version_id: str = Field(..., description="The unique identifier for this specific model version.")
    model_spec_id: str = Field(..., description="Reference to the AIModelSpecification this version implements.")
    training_run_id: Optional[str] = Field(None, description="Reference to the AITrainingRun that produced this version (None for foundational models).")
    training_config_id: Optional[str] = Field(None, description="Reference to the AITrainingConfiguration that defined this run.")
    target_object_id: str = Field(..., description="The unique identifier of the Predictable Object this model is trained for.")
    target_object_name: str = Field(..., description="The short name of the Predictable Object for easy reference.")
    target_object_domain: str = Field(..., description="The domain of the Predictable Object this model is trained for.")
    model_version_training_cost_usd:Optional[float] = Field(None, description="The domain of the Predictable Object this model is trained for.")
    # --- Versioning ---
    version_number: str = Field(..., description="Semantic version number, e.g., '1.2.3' or '2024.08.06.1'.")
    version_name: Optional[str] = Field(None, description="Human-readable version name, e.g., 'Summer_2024_Production'.")
    is_major_version: bool = Field(False, description="Whether this represents a major architectural change.")
    parent_version_id: Optional[str] = Field(None, description="Parent model version if this is an incremental update.")
    
    # --- Model Artifacts ---
    model_artifact_location: str = Field(..., description="Primary storage location of the trained model artifact.")
    model_artifact_checksum: str = Field(..., description="Checksum/hash of the model artifact for integrity verification.")
    model_artifact_size_mb: float = Field(..., description="Size of the model artifact in MB.")
    model_format: str = Field(..., description="Format of the model artifact, e.g., 'pickle', 'onnx', 'tensorflow_savedmodel'.")
    
    # --- Model Metadata ---
    model_complexity_score: Optional[float] = Field(None, description="Complexity score for model comparison and resource planning.")
    inference_latency_ms: Optional[float] = Field(None, description="Average inference latency in milliseconds.")
    memory_footprint_mb: Optional[float] = Field(None, description="Memory footprint required for inference in MB.")
    
    # --- Performance and Validation ---
    validation_performance_metrics: Dict[str, Any] = Field(..., description="Final validation metrics for this model version.")
    test_performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Test set performance metrics if available.")
    benchmark_performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance on standard benchmarks.")
    performance_summary_score: float = Field(..., description="Primary performance score for quick comparison.")
    
    # --- Model State and Status ---
    model_status: AIModelStatus = Field(..., description="Current lifecycle status of this model version.")
    is_production_ready: bool = Field(False, description="Whether this model version is approved for production deployment.")
        
    # --- Deployment Information ---
    deployment_environments: List[str] = Field(default_factory=list, description="List of environments where this version is deployed.")
    first_deployed_datetime: Optional[datetime] = Field(None, description="When this version was first deployed to any environment.")
    production_deployed_datetime: Optional[datetime] = Field(None, description="When this version was deployed to production.")
    last_inference_datetime: Optional[datetime] = Field(None, description="Last time this model version made a prediction.")
    total_predictions_made: int = Field(0, description="Total number of predictions made by this model version.")
    
    # --- Quality and Monitoring ---
    model_quality_score: Optional[float] = Field(None, description="Overall quality assessment score.")
    drift_detection_enabled: bool = Field(True, description="Whether drift detection is enabled for this model version.")
    monitoring_alerts_count: int = Field(0, description="Number of monitoring alerts triggered by this model version.")
    # --- Lifecycle Timestamps ---
    model_created_datetime: datetime = Field(..., description="When this model version was created.")
    model_validated_datetime: Optional[datetime] = Field(None, description="When this model version passed validation.")
    model_approved_datetime: Optional[datetime] = Field(None, description="When this model version was approved for use.")
    model_retired_datetime: Optional[datetime] = Field(None, description="When this model version was retired from active use.")

    # --- Approval and Governance ---
    model_approved_by: Optional[str] = Field(None, description="Who approved this model version for deployment.")
    approval_notes: Optional[str] = Field(None, description="Notes from the approval process.")
    compliance_status: Optional[str] = Field(None, description="Compliance status, e.g., 'approved', 'pending_review'.")
    
    # --- Comparison and Selection ---
    comparison_baseline_version_id: Optional[str] = Field(None, description="Baseline model version used for comparison.")
    performance_improvement_pct: Optional[float] = Field(None, description="Performance improvement over baseline as percentage.")
    resource_efficiency_score: Optional[float] = Field(None, description="Score combining performance and resource usage.")
    
    # --- Metadata ---
    model_description: Optional[str] = Field(None, description="Description of what makes this model version unique.")
    release_notes: Optional[str] = Field(None, description="Release notes describing changes and improvements.")
    known_limitations: Optional[str] = Field(None, description="Known limitations or issues with this model version.")
    strengths: Optional[str] = Field(None, description="Strengths of this model version, e.g., 'high accuracy on recent data'.")
    weaknesses: Optional[str] = Field(None, description="Weaknesses of this model version (e.g., 'struggles with outliers').")
    recommended_use_cases: Optional[List[str]] = Field(None, description="Recommended use cases for this model version.")
    notes: Optional[str] = Field(None, description="Additional notes about this model version.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for categorization and filtering.")

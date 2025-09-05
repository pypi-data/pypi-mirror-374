"""
Foundry SDK Artifacts Package.

This package provides a model-agnostic artifact management system for packaging,
exporting, and loading ML models with their complete runtime context.

Key Components:
- BaseArtifactManager: Core interface for artifact lifecycle management
- BaseExporter: Abstract class for creating artifacts from trained models
- BaseLoader: Abstract class for reconstructing models from artifacts
- ModelFamilyRegistry: Plugin system for registering model family handlers
- Bundle schemas: Flexible Pydantic models for artifact metadata

The system supports both MLflow (development) and HuggingFace Hub (production)
as artifact storage backends, with a focus on reproducible deployments.
"""

from foundry_sdk.artifacts.base import (
    BaseArtifactManager,
    BaseExporter,
    BaseLoader,
    BaseModelFamily,
)
from foundry_sdk.artifacts.exceptions import (
    ArtifactError,
    BundleValidationError,
    ModelFamilyNotFoundError,
    SchemaVersionError,
)
from foundry_sdk.artifacts.families import XGBFamily
from foundry_sdk.artifacts.schema import (
    ArchitectureSpec,
    BundleSchema,
    DataSpec,
    EnvironmentSpec,
    IOSpec,
    LineageSpec,
)

__all__ = [
    # Base classes
    "BaseArtifactManager",
    "BaseExporter",
    "BaseLoader",
    "BaseModelFamily",
    # Model families
    "XGBFamily",
    # Schemas
    "BundleSchema",
    "ArchitectureSpec",
    "DataSpec",
    "IOSpec",
    "LineageSpec",
    "EnvironmentSpec",
    # Exceptions
    "ArtifactError",
    "BundleValidationError",
    "ModelFamilyNotFoundError",
    "SchemaVersionError",
]

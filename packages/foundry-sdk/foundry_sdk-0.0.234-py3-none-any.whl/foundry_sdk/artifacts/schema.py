"""
Pydantic schemas for foundry bundle validation.

This module provides flexible, extensible schemas that allow model families
to define their own architecture, data specifications, and I/O requirements
while maintaining a consistent core structure.
"""

import typing as t
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class ExtensibleBaseModel(BaseModel):
    """Base model that allows arbitrary additional fields for extensibility."""

    class Config:
        extra = "allow"  # Allow additional fields not defined in the schema
        validate_assignment = True


class ArchitectureSpec(ExtensibleBaseModel):
    """
    Architecture specification for model reconstruction.

    Core required fields for all model families, with extensibility
    for family-specific parameters.
    """

    class_path: str = Field(
        ...,
        description="Importable class path for model reconstruction (e.g., 'foundry.models.VanillaTransformer')",
        min_length=1,
    )

    @field_validator("class_path")
    @classmethod
    def validate_class_path(cls, v: str) -> str:
        """Validate class path format."""
        if not v or "." not in v:
            raise ValueError("class_path must be a valid importable path (e.g., 'module.ClassName')")
        return v


class DataSpec(ExtensibleBaseModel):
    """
    Data specification and preprocessing contract.

    Completely extensible - each model family defines what data
    contract information they need for reproducible preprocessing.
    """

    # Intentionally empty - model families add their own fields


class IOSpec(ExtensibleBaseModel):
    """
    Input/output format specification.

    Extensible specification for describing model input and output formats,
    shapes, semantics, etc. Model families define their own requirements.
    """

    # Intentionally empty - model families add their own fields


class LineageSpec(ExtensibleBaseModel):
    """
    Provenance and lineage information.

    Tracks the origin and reproducibility information for the model.
    Core fields are optional, model families can add additional tracking.
    """

    mlflow_run_id: str | None = Field(
        None,
        description="MLflow run ID where this model was trained",
    )

    code_git_sha: str | None = Field(
        None,
        description="Git commit SHA of the code used for training",
        pattern=r"^[a-f0-9]{7,40}$",  # Git SHA format
    )

    dataset_ref: str | None = Field(
        None,
        description="Reference to dataset used for training (e.g., 'org/dataset@revision')",
    )

    created_at: datetime | None = Field(
        None,
        description="Timestamp when this bundle was created",
    )


class EnvironmentSpec(ExtensibleBaseModel):
    """
    Environment and dependency specification.

    Core environment tracking with extensibility for family-specific dependencies.
    """

    python: str | None = Field(
        None,
        description="Python version used",
        pattern=r"^\d+\.\d+(\.\d+)?$",  # Version format like "3.11" or "3.11.0"
    )

    foundry_sdk: str | None = Field(
        None,
        description="Foundry SDK version used",
    )


class BundleSchema(ExtensibleBaseModel):
    """
    Core bundle schema for foundry_bundle.json.

    Defines the minimal required structure while allowing complete extensibility
    for model family-specific requirements. Only bundle_version, family, and
    arch.class_path are strictly required.
    """

    bundle_version: str = Field(
        ...,
        description="Semantic version of the bundle schema",
        pattern=r"^\d+\.\d+(\.\d+)?(-[\w\d\-_]+)?(\+[\w\d\-_]+)?$",  # Semantic versioning
    )

    family: str = Field(
        ...,
        description="Model family identifier (e.g., 'torch-lightning', 'xgboost')",
        min_length=1,
    )

    arch: ArchitectureSpec = Field(
        ...,
        description="Architecture specification for model reconstruction",
    )

    data_spec: DataSpec | None = Field(
        None,
        description="Data preprocessing and contract specification",
    )

    io: IOSpec | None = Field(
        None,
        description="Input/output format specification",
    )

    lineage: LineageSpec | None = Field(
        None,
        description="Provenance and reproducibility information",
    )

    env: EnvironmentSpec | None = Field(
        None,
        description="Environment and dependency information",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_bundle_structure(cls, values: dict[str, t.Any]) -> dict[str, t.Any]:
        """Perform cross-field validation on the bundle."""
        # Ensure arch has required class_path
        arch = values.get("arch")
        if arch and not hasattr(arch, "class_path"):
            raise ValueError("arch.class_path is required for model reconstruction")

        return values

    def get_family_specific_data(self, section: str) -> dict[str, t.Any]:
        """
        Get all family-specific data from a section as a dict.

        Args:
            section: Section name ("arch", "data_spec", "io", "lineage", "env")

        Returns:
            Dictionary of all fields in that section

        """
        section_data = getattr(self, section, None)
        if section_data is None:
            return {}
        return section_data.dict()

    def validate_for_family(self, family_validator: t.Callable[["BundleSchema"], None]) -> None:
        """
        Validate bundle using family-specific validation logic.

        Args:
            family_validator: Function that raises ValidationError if invalid


        """
        family_validator(self)

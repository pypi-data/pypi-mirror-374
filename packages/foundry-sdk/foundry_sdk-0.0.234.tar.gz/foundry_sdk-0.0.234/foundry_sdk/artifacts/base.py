"""
Abstract base classes for the artifacts system.

This module defines the core interfaces that all model family implementations
must provide for artifact management, export, and loading functionality.
"""

import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

from foundry_sdk.artifacts.schema import BundleSchema


class BaseModelFamily(ABC):
    """
    Abstract base class for model family handlers.

    Each model family (torch-lightning, xgboost, etc.) must implement this
    interface to integrate with the artifact management system.
    """

    @property
    @abstractmethod
    def family_name(self) -> str:
        """Return the unique identifier for this model family."""
        ...

    @abstractmethod
    def save_model_weights(self, model: t.Any, output_dir: Path) -> list[str]:
        """
        Save model weights to output directory.

        Args:
            model: Trained model to save
            output_dir: Directory to save weights to

        Returns:
            List of relative file paths that were created

        """
        ...

    @abstractmethod
    def load_model_weights(self, model: t.Any, weights_dir: Path, bundle: BundleSchema) -> t.Any:
        """
        Load weights into a model instance.

        Args:
            model: Model instance to load weights into
            weights_dir: Directory containing weight files
            bundle: Bundle containing metadata

        Returns:
            Model with loaded weights

        """
        ...

    @abstractmethod
    def reconstruct_model(self, bundle: BundleSchema) -> t.Any:
        """
        Reconstruct model instance from bundle specification.

        Args:
            bundle: Bundle containing architecture and other specs

        Returns:
            Reconstructed model instance (without weights)

        """


class BaseExporter(ABC):
    """
    Abstract base class for creating artifacts from trained models.

    Exporters handle the process of taking a trained model and its context
    and creating a complete artifact bundle for storage and distribution.
    """

    @abstractmethod
    def export(
        self,
        model: t.Any,
        output_dir: Path,
        *,
        family: str | None = None,
        data_module: t.Any | None = None,
        metrics: dict[str, t.Any] | None = None,
        lineage: dict[str, t.Any] | None = None,
        **kwargs: t.Any,
    ) -> Path:
        """
        Export a trained model to a complete artifact bundle.

        Args:
            model: Trained model to export
            output_dir: Directory to create the bundle in
            family: Model family name (will auto-detect if None)
            data_module: Optional data module for extracting data spec
            metrics: Optional evaluation metrics to include
            lineage: Optional lineage/provenance information
            **kwargs: Additional family-specific export parameters

        Returns:
            Path to the created bundle directory

        Raises:
            ModelFamilyNotFoundError: If family cannot be determined
            ArtifactError: If export fails

        """
        ...

    @abstractmethod
    def validate_export_inputs(
        self,
        model: t.Any,
        output_dir: Path,
        **kwargs: t.Any,
    ) -> None:
        """
        Validate that all required inputs for export are present and valid.

        Args:
            model: Model to validate
            output_dir: Output directory to validate
            **kwargs: Additional parameters to validate

        Raises:
            ArtifactError: If inputs are invalid

        """
        ...


class BaseLoader(ABC):
    """
    Abstract base class for loading models from artifact bundles.

    Loaders handle reconstructing complete models from stored bundles,
    supporting both MLflow and HuggingFace Hub sources.
    """

    @abstractmethod
    def load(
        self,
        source: str | Path,
        *,
        family: str | None = None,
        **kwargs: t.Any,
    ) -> tuple[t.Any, BundleSchema]:
        """
        Load a model from an artifact bundle.

        Args:
            source: Path or identifier for the bundle source
            family: Expected model family (will auto-detect if None)
            **kwargs: Additional family-specific loading parameters

        Returns:
            Tuple of (reconstructed model, bundle schema)

        Raises:
            ModelFamilyNotFoundError: If family cannot be determined
            ModelReconstructionError: If model reconstruction fails
            ArtifactSourceError: If source cannot be accessed

        """
        ...

    @abstractmethod
    def resolve_source(self, source: str | Path) -> tuple[Path, dict[str, t.Any]]:
        """
        Resolve a source identifier to a local directory and metadata.

        Args:
            source: Source identifier (local path, MLflow run, HF repo, etc.)

        Returns:
            Tuple of (local_directory, source_metadata)

        Raises:
            ArtifactSourceError: If source cannot be resolved

        """
        ...

    @abstractmethod
    def validate_bundle_integrity(self, bundle_dir: Path) -> None:
        """
        Validate the integrity of a bundle directory.

        Args:
            bundle_dir: Path to bundle directory

        Raises:
            ArtifactIntegrityError: If integrity checks fail
            BundleValidationError: If bundle structure is invalid

        """
        ...


class BaseArtifactManager(ABC):
    """
    Core interface for complete artifact lifecycle management.

    This is the main entry point for artifact operations, combining
    export and loading functionality with registry management.
    """

    @abstractmethod
    def create_bundle(
        self,
        model: t.Any,
        output_dir: Path,
        *,
        bundle_name: str | None = None,
        **kwargs: t.Any,
    ) -> Path:
        """
        Create a complete artifact bundle from a trained model.

        Args:
            model: Trained model to bundle
            output_dir: Directory to create bundle in
            bundle_name: Optional name for the bundle directory
            **kwargs: Additional export parameters

        Returns:
            Path to created bundle directory

        """
        ...

    @abstractmethod
    def load_bundle(
        self,
        source: str | Path,
        **kwargs: t.Any,
    ) -> tuple[t.Any, BundleSchema]:
        """
        Load a model from a bundle source.

        Args:
            source: Bundle source identifier
            **kwargs: Additional loading parameters

        Returns:
            Tuple of (loaded model, bundle schema)

        """
        ...

    @abstractmethod
    def validate_bundle(self, bundle_path: Path) -> BundleSchema:
        """
        Validate a bundle and return its schema.

        Args:
            bundle_path: Path to bundle directory

        Returns:
            Validated bundle schema

        Raises:
            BundleValidationError: If validation fails

        """
        ...

    @abstractmethod
    def list_bundles(self, search_path: Path) -> list[dict[str, t.Any]]:
        """
        List all valid bundles in a directory.

        Args:
            search_path: Directory to search for bundles

        Returns:
            List of bundle metadata dictionaries

        """
        ...


class BaseBundleValidator(ABC):
    """
    Abstract base class for bundle validation logic.

    Provides extensible validation that can be customized per model family
    while maintaining core consistency checks.
    """

    @abstractmethod
    def validate_schema_version(self, bundle: BundleSchema) -> None:
        """
        Validate that bundle schema version is supported.

        Args:
            bundle: Bundle to validate

        Raises:
            SchemaVersionError: If version is unsupported

        """
        ...

    @abstractmethod
    def validate_core_structure(self, bundle: BundleSchema) -> None:
        """
        Validate core bundle structure and required fields.

        Args:
            bundle: Bundle to validate

        Raises:
            BundleValidationError: If core structure is invalid

        """
        ...

    @abstractmethod
    def validate_family_specific(self, bundle: BundleSchema, family: BaseModelFamily) -> None:
        """
        Validate family-specific bundle requirements.

        Args:
            bundle: Bundle to validate
            family: Model family handler

        Raises:
            BundleValidationError: If family-specific validation fails

        """
        ...

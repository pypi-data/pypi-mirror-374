"""Exception classes for the artifacts package."""

import typing as t


class ArtifactError(Exception):
    """Base exception for all artifact-related errors."""

    def __init__(self, message: str, *, remediation: str | None = None) -> None:
        """
        Initialize with message and optional remediation advice.

        Args:
            message: Error description
            remediation: Optional suggestion for fixing the error

        """
        super().__init__(message)
        self.message = message
        self.remediation = remediation

    def __str__(self) -> str:
        """Return formatted error message with remediation if available."""
        if self.remediation:
            return f"{self.message}\nSuggestion: {self.remediation}"
        return self.message


class BundleValidationError(ArtifactError):
    """Raised when bundle validation fails."""

    def __init__(
        self,
        message: str,
        *,
        field_path: str | None = None,
        expected_type: str | None = None,
        actual_value: t.Any = None,
        remediation: str | None = None,
    ) -> None:
        """
        Initialize bundle validation error.

        Args:
            message: Error description
            field_path: JSON path to the invalid field (e.g., "arch.n_layer")
            expected_type: Expected type or format
            actual_value: The actual invalid value
            remediation: Suggestion for fixing the error

        """
        super().__init__(message, remediation=remediation)
        self.field_path = field_path
        self.expected_type = expected_type
        self.actual_value = actual_value


class SchemaVersionError(ArtifactError):
    """Raised when bundle schema version is incompatible."""

    def __init__(
        self,
        message: str,
        *,
        bundle_version: str | None = None,
        supported_versions: list[str] | None = None,
        remediation: str | None = None,
    ) -> None:
        """
        Initialize schema version error.

        Args:
            message: Error description
            bundle_version: The unsupported bundle version
            supported_versions: List of versions that are supported
            remediation: Suggestion for handling version mismatch

        """
        super().__init__(message, remediation=remediation)
        self.bundle_version = bundle_version
        self.supported_versions = supported_versions or []


class ModelFamilyNotFoundError(ArtifactError):
    """Raised when requested model family is not registered."""

    def __init__(
        self,
        message: str,
        *,
        family_name: str | None = None,
        available_families: list[str] | None = None,
        remediation: str | None = None,
    ) -> None:
        """
        Initialize model family not found error.

        Args:
            message: Error description
            family_name: The requested family that wasn't found
            available_families: List of registered families
            remediation: Suggestion for resolving the missing family

        """
        super().__init__(message, remediation=remediation)
        self.family_name = family_name
        self.available_families = available_families or []


class ArtifactIntegrityError(ArtifactError):
    """Raised when artifact integrity checks fail."""

    def __init__(
        self,
        message: str,
        *,
        file_path: str | None = None,
        expected_checksum: str | None = None,
        actual_checksum: str | None = None,
        remediation: str | None = None,
    ) -> None:
        """
        Initialize artifact integrity error.

        Args:
            message: Error description
            file_path: Path to the corrupted file
            expected_checksum: Expected file checksum
            actual_checksum: Actual file checksum
            remediation: Suggestion for handling corruption

        """
        super().__init__(message, remediation=remediation)
        self.file_path = file_path
        self.expected_checksum = expected_checksum
        self.actual_checksum = actual_checksum


class ArtifactSourceError(ArtifactError):
    """Raised when artifact source (MLflow/HF) cannot be accessed."""

    def __init__(
        self,
        message: str,
        *,
        source_type: str | None = None,
        source_path: str | None = None,
        remediation: str | None = None,
    ) -> None:
        """
        Initialize artifact source error.

        Args:
            message: Error description
            source_type: Type of source ("mlflow", "huggingface", "local")
            source_path: Path or identifier that failed
            remediation: Suggestion for resolving source issues

        """
        super().__init__(message, remediation=remediation)
        self.source_type = source_type
        self.source_path = source_path


class ModelReconstructionError(ArtifactError):
    """Raised when model cannot be reconstructed from bundle."""

    def __init__(
        self,
        message: str,
        *,
        family: str | None = None,
        class_path: str | None = None,
        missing_weights: bool = False,
        remediation: str | None = None,
    ) -> None:
        """
        Initialize model reconstruction error.

        Args:
            message: Error description
            family: Model family that failed reconstruction
            class_path: Class path that couldn't be imported
            missing_weights: Whether weights file is missing
            remediation: Suggestion for fixing reconstruction

        """
        super().__init__(message, remediation=remediation)
        self.family = family
        self.class_path = class_path
        self.missing_weights = missing_weights

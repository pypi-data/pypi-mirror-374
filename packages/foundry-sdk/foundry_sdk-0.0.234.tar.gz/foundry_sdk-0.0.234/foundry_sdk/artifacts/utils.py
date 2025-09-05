"""
Core utilities for artifact management.

This module provides common functionality for file operations, integrity checking,
validation, and other utilities needed across the artifacts system.
"""

import hashlib
import json
import shutil
import typing as t
from datetime import datetime
from pathlib import Path

from foundry_sdk.artifacts.exceptions import ArtifactError, ArtifactIntegrityError, BundleValidationError
from foundry_sdk.artifacts.schema import BundleSchema, ManifestEntry, ManifestSchema


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file.

    Args:
        file_path: Path to file to hash
        algorithm: Hash algorithm to use ("sha256", "md5", etc.)

    Returns:
        Hex-encoded hash string

    Raises:
        ArtifactError: If file cannot be read or algorithm is unsupported

    """
    try:
        hasher = hashlib.new(algorithm)
    except ValueError as e:
        raise ArtifactError(f"Unsupported hash algorithm: {algorithm}") from e

    try:
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError as e:
        raise ArtifactError(f"Cannot read file for hashing: {file_path}") from e


def calculate_string_hash(content: str, algorithm: str = "sha256") -> str:
    """
    Calculate hash of a string.

    Args:
        content: String content to hash
        algorithm: Hash algorithm to use

    Returns:
        Hex-encoded hash string

    """
    try:
        hasher = hashlib.new(algorithm)
        hasher.update(content.encode("utf-8"))
        return hasher.hexdigest()
    except ValueError as e:
        raise ArtifactError(f"Unsupported hash algorithm: {algorithm}") from e


def create_manifest(bundle_dir: Path, bundle_checksum: str | None = None) -> ManifestSchema:
    """
    Create a manifest for all files in a bundle directory.

    Args:
        bundle_dir: Path to bundle directory
        bundle_checksum: Optional pre-calculated bundle checksum

    Returns:
        Manifest schema with file integrity information

    Raises:
        ArtifactError: If bundle directory is invalid

    """
    if not bundle_dir.exists() or not bundle_dir.is_dir():
        raise ArtifactError(f"Bundle directory does not exist: {bundle_dir}")

    # Calculate bundle checksum if not provided
    if bundle_checksum is None:
        bundle_json_path = bundle_dir / "bundle" / "foundry_bundle.json"
        if not bundle_json_path.exists():
            raise ArtifactError(f"Bundle JSON not found: {bundle_json_path}")
        bundle_checksum = calculate_file_hash(bundle_json_path)

    manifest_entries = []

    # Walk all files in bundle directory
    for file_path in bundle_dir.rglob("*"):
        if file_path.is_file() and file_path.name != "MANIFEST.json":
            try:
                relative_path = file_path.relative_to(bundle_dir)
                file_hash = calculate_file_hash(file_path)
                file_size = file_path.stat().st_size
                created_at = datetime.fromtimestamp(file_path.stat().st_ctime)

                manifest_entries.append(
                    ManifestEntry(
                        path=str(relative_path),
                        sha256=file_hash,
                        size=file_size,
                        created_at=created_at,
                    )
                )
            except (OSError, ValueError) as e:
                raise ArtifactError(f"Error processing file {file_path}: {e}") from e

    return ManifestSchema(
        bundle_checksum=bundle_checksum,
        files=manifest_entries,
    )


def validate_manifest(bundle_dir: Path, manifest: ManifestSchema) -> None:
    """
    Validate that all files in manifest match their checksums.

    Args:
        bundle_dir: Path to bundle directory
        manifest: Manifest to validate against

    Raises:
        ArtifactIntegrityError: If any file fails integrity check

    """
    for entry in manifest.files:
        file_path = bundle_dir / entry.path

        if not file_path.exists():
            raise ArtifactIntegrityError(
                f"File missing from bundle: {entry.path}",
                file_path=str(file_path),
                remediation="Re-download or re-create the bundle",
            )

        actual_hash = calculate_file_hash(file_path)
        if actual_hash != entry.sha256:
            raise ArtifactIntegrityError(
                f"File checksum mismatch: {entry.path}",
                file_path=str(file_path),
                expected_checksum=entry.sha256,
                actual_checksum=actual_hash,
                remediation="File may be corrupted, re-download or re-create the bundle",
            )

        # Check file size
        actual_size = file_path.stat().st_size
        if actual_size != entry.size:
            raise ArtifactIntegrityError(
                f"File size mismatch: {entry.path} (expected {entry.size}, got {actual_size})",
                file_path=str(file_path),
                remediation="File may be corrupted or truncated",
            )


def save_json(data: t.Any, file_path: Path, *, indent: int = 2) -> None:
    """
    Save data as JSON file with error handling.

    Args:
        data: Data to save (must be JSON serializable)
        file_path: Path to save JSON to
        indent: JSON indentation for readability

    Raises:
        ArtifactError: If data cannot be serialized or file cannot be written

    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
    except (TypeError, ValueError) as e:
        raise ArtifactError(f"Cannot serialize data to JSON: {e}") from e
    except OSError as e:
        raise ArtifactError(f"Cannot write JSON file: {file_path}") from e


def load_json(file_path: Path, *, schema_class: type[t.Any] | None = None) -> t.Any:
    """
    Load and optionally validate JSON file.

    Args:
        file_path: Path to JSON file
        schema_class: Optional Pydantic model class for validation

    Returns:
        Loaded data (optionally validated)

    Raises:
        ArtifactError: If file cannot be read or JSON is invalid
        BundleValidationError: If schema validation fails

    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise ArtifactError(f"Cannot read JSON file: {file_path}") from e
    except json.JSONDecodeError as e:
        raise ArtifactError(f"Invalid JSON in file: {file_path}") from e

    if schema_class is not None:
        try:
            return schema_class.parse_obj(data)
        except Exception as e:
            raise BundleValidationError(
                f"JSON validation failed for {file_path}: {e}",
                remediation="Check that the JSON structure matches expected schema",
            ) from e

    return data


def copy_directory_tree(source: Path, destination: Path, *, ignore_patterns: list[str] | None = None) -> None:
    """
    Copy directory tree with optional ignore patterns.

    Args:
        source: Source directory to copy from
        destination: Destination directory to copy to
        ignore_patterns: Optional list of patterns to ignore (shell-style)

    Raises:
        ArtifactError: If copy operation fails

    """
    try:
        if ignore_patterns:
            ignore_func = shutil.ignore_patterns(*ignore_patterns)
        else:
            ignore_func = None

        shutil.copytree(source, destination, ignore=ignore_func, dirs_exist_ok=True)
    except OSError as e:
        raise ArtifactError(f"Failed to copy directory tree: {source} -> {destination}") from e


def ensure_directory(directory: Path) -> None:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        directory: Directory path to ensure exists

    Raises:
        ArtifactError: If directory cannot be created

    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ArtifactError(f"Cannot create directory: {directory}") from e


def validate_bundle_structure(bundle_dir: Path) -> BundleSchema:
    """
    Validate basic bundle directory structure and load bundle schema.

    Args:
        bundle_dir: Path to bundle directory

    Returns:
        Validated bundle schema

    Raises:
        BundleValidationError: If bundle structure is invalid
        ArtifactError: If files cannot be read

    """
    if not bundle_dir.exists() or not bundle_dir.is_dir():
        raise BundleValidationError(
            f"Bundle directory does not exist: {bundle_dir}",
            remediation="Ensure the bundle path is correct and accessible",
        )

    # Check for required bundle structure
    bundle_subdir = bundle_dir / "bundle"
    if not bundle_subdir.exists():
        raise BundleValidationError(
            "Bundle directory missing required 'bundle' subdirectory",
            remediation="Bundle must contain a 'bundle' subdirectory with foundry_bundle.json",
        )

    bundle_json_path = bundle_subdir / "foundry_bundle.json"
    if not bundle_json_path.exists():
        raise BundleValidationError(
            "Bundle missing foundry_bundle.json file",
            remediation="Bundle must contain bundle/foundry_bundle.json with model metadata",
        )

    # Load and validate bundle schema
    try:
        bundle_data = load_json(bundle_json_path)
        bundle_schema = BundleSchema.parse_obj(bundle_data)
        return bundle_schema
    except Exception as e:
        raise BundleValidationError(f"Invalid bundle schema: {e}") from e


def get_bundle_model_dir(bundle_dir: Path) -> Path:
    """
    Get the model directory within a bundle.

    Args:
        bundle_dir: Path to bundle directory

    Returns:
        Path to model directory

    Raises:
        BundleValidationError: If model directory doesn't exist

    """
    model_dir = bundle_dir / "model"
    if not model_dir.exists():
        raise BundleValidationError(
            "Bundle missing 'model' directory",
            remediation="Bundle must contain a 'model' directory with model weights",
        )
    return model_dir


def generate_bundle_readme(bundle_schema: BundleSchema, metrics: dict[str, t.Any] | None = None) -> str:
    """
    Generate a README.md content for a bundle.

    Args:
        bundle_schema: Bundle schema to document
        metrics: Optional metrics to include

    Returns:
        README content as string

    """
    lines = [
        f"# {bundle_schema.family.replace('-', ' ').title()} Model",
        "",
        "## Overview",
        f"- **Family**: {bundle_schema.family}",
        f"- **Bundle Version**: {bundle_schema.bundle_version}",
        f"- **Architecture**: {bundle_schema.arch.class_path}",
    ]

    if bundle_schema.lineage:
        lines.extend(
            [
                "",
                "## Lineage",
            ]
        )
        if bundle_schema.lineage.mlflow_run_id:
            lines.append(f"- **MLflow Run**: {bundle_schema.lineage.mlflow_run_id}")
        if bundle_schema.lineage.dataset_ref:
            lines.append(f"- **Dataset**: {bundle_schema.lineage.dataset_ref}")
        if bundle_schema.lineage.code_git_sha:
            lines.append(f"- **Code SHA**: {bundle_schema.lineage.code_git_sha}")
        if bundle_schema.lineage.created_at:
            lines.append(f"- **Created**: {bundle_schema.lineage.created_at}")

    if metrics:
        lines.extend(
            [
                "",
                "## Metrics",
            ]
        )
        for metric_name, metric_value in metrics.items():
            lines.append(f"- **{metric_name}**: {metric_value}")

    if bundle_schema.env:
        lines.extend(
            [
                "",
                "## Environment",
            ]
        )
        if bundle_schema.env.python:
            lines.append(f"- **Python**: {bundle_schema.env.python}")
        if bundle_schema.env.foundry_sdk:
            lines.append(f"- **Foundry SDK**: {bundle_schema.env.foundry_sdk}")

    lines.extend(
        [
            "",
            "## Usage",
            "",
            "```python",
            "from foundry_sdk.artifacts import BaseArtifactManager",
            "",
            "# Load model from bundle",
            "manager = BaseArtifactManager()",
            f'model, bundle = manager.load_bundle("{bundle_schema.family}-model")',
            "```",
            "",
        ]
    )

    return "\n".join(lines)

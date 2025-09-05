"""
XGBoost model family implementation.

This module provides XGBoost-specific artifact management functionality,
supporting both single models and local model banks (sharded collections).
"""

import json
import typing as t
from pathlib import Path

from foundry_sdk.artifacts.base import BaseModelFamily
from foundry_sdk.artifacts.exceptions import ArtifactError, BundleValidationError
from foundry_sdk.artifacts.schema import BundleSchema


class XGBFamily(BaseModelFamily):
    """
    XGBoost model family handler.

    Supports both single XGBoost models and local model banks (collections
    of thousands of models stored in sharded SQLite files).
    """

    @property
    def family_name(self) -> str:
        """Return the unique identifier for XGBoost family."""
        return "xgboost"

    @property
    def supported_extensions(self) -> list[str]:
        """Return file extensions XGBoost can handle."""
        return [".json", ".model", ".sqlite", ".sqlite.zst"]

    def can_handle_model(self, model: t.Any) -> bool:
        """
        Check if this family can handle the given model instance.

        Args:
            model: Model instance to check

        Returns:
            True if this is an XGBoost model

        """
        # Check for XGBoost Booster
        model_type = type(model).__name__
        module_name = getattr(type(model), "__module__", "")

        return (model_type == "Booster" and "xgboost" in module_name) or (
            # Also check for common XGBoost wrapper classes
            hasattr(model, "get_booster") or (hasattr(model, "save_model") and hasattr(model, "load_model"))
        )

    def validate_bundle(self, bundle: BundleSchema) -> None:
        """
        Validate that the bundle contains all required XGBoost-specific fields.

        Args:
            bundle: Bundle to validate

        Raises:
            BundleValidationError: If bundle is invalid for XGBoost

        """
        if bundle.family not in ["xgboost", "xgboost-local-bank"]:
            raise BundleValidationError(
                f"Bundle family '{bundle.family}' is not supported by XGBFamily",
                remediation="Use 'xgboost' or 'xgboost-local-bank' family",
            )

        # Check architecture section
        arch_data = bundle.get_family_specific_data("arch")

        # For local banks, we need different validation
        if bundle.family == "xgboost-local-bank":
            required_fields = ["shard_count", "model_count"]
        else:
            required_fields = ["objective", "num_features"]

        for field in required_fields:
            if field not in arch_data:
                raise BundleValidationError(
                    f"Missing required XGBoost architecture field: {field}",
                    field_path=f"arch.{field}",
                    remediation=f"Add {field} to the architecture specification",
                )

    def extract_architecture_spec(self, model: t.Any, training_config: t.Any = None) -> dict[str, t.Any]:
        """
        Extract architecture specification from an XGBoost model.

        Args:
            model: Trained XGBoost model
            training_config: Optional TrainingConfig object with hyperparameters

        Returns:
            Dictionary containing XGBoost parameters needed for reconstruction

        """
        try:
            # Get the booster (handle both Booster and wrapper classes)
            if hasattr(model, "get_booster"):
                booster = model.get_booster()
            else:
                booster = model

            # Extract key parameters from model
            config = json.loads(booster.save_config())
            learner_config = config.get("learner", {})

            arch_spec = {
                "class_path": "xgboost.Booster",  # Standard XGBoost class
                "objective": learner_config.get("objective", {}).get("name", "unknown"),
                "num_features": booster.num_features(),
                "num_boosted_rounds": booster.num_boosted_rounds(),
                "booster_type": learner_config.get("gradient_booster", {}).get("name", "gbtree"),
            }

            # Extract hyperparameters from TrainingConfig if provided
            if training_config is not None:
                if hasattr(training_config, "model_configs") and training_config.model_configs:
                    model_config = training_config.model_configs[0]  # Assume first config

                    # Add model type and quantile info
                    if hasattr(model_config, "model_type"):
                        arch_spec["model_type"] = model_config.model_type
                    if hasattr(model_config, "quantile_alpha"):
                        arch_spec["quantile_alpha"] = model_config.quantile_alpha

                    # Add all hyperparameters from training config
                    if hasattr(model_config, "hyperparameters"):
                        arch_spec["hyperparameters"] = model_config.hyperparameters.copy()

                # Add random state from training config
                if hasattr(training_config, "random_state"):
                    arch_spec["random_state"] = training_config.random_state

            # Fallback: try to get hyperparameters from model if no config provided
            elif hasattr(model, "get_params"):
                params = model.get_params()
                arch_spec["hyperparameters"] = {
                    "max_depth": params.get("max_depth"),
                    "learning_rate": params.get("learning_rate"),
                    "n_estimators": params.get("n_estimators"),
                    "subsample": params.get("subsample"),
                    "colsample_bytree": params.get("colsample_bytree"),
                    "reg_alpha": params.get("reg_alpha"),
                    "reg_lambda": params.get("reg_lambda"),
                }

            return arch_spec

        except Exception as e:
            raise ArtifactError(f"Failed to extract XGBoost architecture: {e}") from e

    def extract_data_spec(
        self, data_module: t.Any | None = None, data_config: t.Any = None, **kwargs: t.Any
    ) -> dict[str, t.Any]:
        """
        Extract data specification for XGBoost models.

        Args:
            data_module: Optional data module (XGBoost-specific feature builder)
            data_config: Optional DataConfig from your pipeline
            **kwargs: Additional parameters like feature_names, target_column

        Returns:
            Dictionary containing XGBoost data contract

        """
        data_spec = {}

        # Extract from data_config if provided
        if data_config is not None:
            # Add any data configuration parameters
            if hasattr(data_config, "target_column"):
                data_spec["target_column"] = data_config.target_column
            if hasattr(data_config, "feature_columns"):
                data_spec["feature_columns"] = data_config.feature_columns
            if hasattr(data_config, "time_column"):
                data_spec["time_column"] = data_config.time_column
            if hasattr(data_config, "id_columns"):
                data_spec["id_columns"] = data_config.id_columns

            # Add data source information
            if hasattr(data_config, "data_source"):
                data_spec["data_source"] = data_config.data_source
            if hasattr(data_config, "preprocessing_steps"):
                data_spec["preprocessing_steps"] = data_config.preprocessing_steps

        # Feature information from kwargs
        if "feature_names" in kwargs:
            data_spec["feature_names"] = kwargs["feature_names"]

        if "target_column" in kwargs:
            data_spec["target_column"] = kwargs["target_column"]

        # XGBoost-specific data handling
        data_spec.update(
            {
                "data_format": "DMatrix",
                "missing_value_handling": kwargs.get("missing", 0.0),
                "categorical_features": kwargs.get("categorical_features", []),
            }
        )

        # If we have a data module, extract more information
        if data_module is not None:
            if hasattr(data_module, "get_feature_names"):
                data_spec["feature_names"] = data_module.get_feature_names()
            if hasattr(data_module, "get_preprocessing_params"):
                data_spec["preprocessing"] = data_module.get_preprocessing_params()

        return data_spec

    def save_model_weights(self, model: t.Any, output_dir: Path) -> list[str]:
        """
        Save XGBoost model to output directory.

        Args:
            model: Trained XGBoost model
            output_dir: Directory to save model to

        Returns:
            List of relative file paths that were created

        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get the booster
            if hasattr(model, "get_booster"):
                booster = model.get_booster()
            else:
                booster = model

            # Save as JSON (portable format)
            model_path = output_dir / "model.json"
            booster.save_model(str(model_path))

            return ["model.json"]

        except Exception as e:
            raise ArtifactError(f"Failed to save XGBoost model: {e}") from e

    def load_model_weights(self, model: t.Any, weights_dir: Path, bundle: BundleSchema) -> t.Any:
        """
        Load weights into an XGBoost model instance.

        Args:
            model: XGBoost model instance to load weights into
            weights_dir: Directory containing weight files
            bundle: Bundle containing metadata

        Returns:
            Model with loaded weights

        """
        try:
            model_path = weights_dir / "model.json"

            if not model_path.exists():
                raise ArtifactError(f"XGBoost model file not found: {model_path}")

            # Load the model
            if hasattr(model, "load_model"):
                model.load_model(str(model_path))
            else:
                # For raw Booster objects
                model.load_model(str(model_path))

            return model

        except Exception as e:
            raise ArtifactError(f"Failed to load XGBoost model: {e}") from e

    def reconstruct_model(self, bundle: BundleSchema) -> t.Any:
        """
        Reconstruct XGBoost model instance from bundle specification.

        Args:
            bundle: Bundle containing architecture and other specs

        Returns:
            Reconstructed XGBoost model instance (without weights)

        """
        try:
            # Import XGBoost
            import xgboost as xgb

            arch_data = bundle.get_family_specific_data("arch")

            # Create a new Booster instance
            # For XGBoost, we can't reconstruct without weights, so we create empty
            booster = xgb.Booster()

            return booster

        except ImportError as e:
            raise ArtifactError(
                "XGBoost not available for model reconstruction",
                remediation="Install XGBoost: pip install xgboost",
            ) from e
        except Exception as e:
            raise ArtifactError(f"Failed to reconstruct XGBoost model: {e}") from e

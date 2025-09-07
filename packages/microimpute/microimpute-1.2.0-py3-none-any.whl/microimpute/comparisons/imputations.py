"""Imputation generation utilities.

This module handles the generation of imputations using multiple model classes.
It provides functions to generate predictions at different quantiles,
and organize results in a consistent format for comparison.
"""

import logging
from typing import Any, Dict, List, Optional, Type

import numpy as np
import pandas as pd
from pydantic import validate_call

from microimpute.config import QUANTILES, VALIDATE_CONFIG
from microimpute.models.quantreg import QuantReg

log = logging.getLogger(__name__)


@validate_call(config=VALIDATE_CONFIG)
def get_imputations(
    model_classes: List[Type],
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    predictors: List[str],
    imputed_variables: List[str],
    quantiles: Optional[List[float]] = QUANTILES,
) -> Dict[str, Dict[float, pd.DataFrame]]:
    """Generate imputations using multiple model classes for the specified variables.

    Args:
        model_classes: List of model classes to use (e.g., QRF, OLS, QuantReg, Matching).
        X_train: Training data containing predictors and variables to impute.
        X_test: Test data on which to make imputations.
        predictors: Names of columns to use as predictors.
        imputed_variables: Names of columns to impute.
        quantiles: List of quantiles to predict.

    Returns:
        Nested dictionary mapping method names to dictionaries mapping quantiles to imputations.

    Raises:
        ValueError: If input data is invalid or missing required columns.
        RuntimeError: If model fitting or prediction fails.
    """
    try:
        # Input validation
        if not model_classes:
            error_msg = "model_classes list is empty"
            log.error(error_msg)
            raise ValueError(error_msg)

        # Validate that predictor and imputed variable columns exist in training data
        missing_predictors_train = [
            col for col in predictors if col not in X_train.columns
        ]
        if missing_predictors_train:
            error_msg = f"Missing predictor columns in training data: {missing_predictors_train}"
            log.error(error_msg)
            raise ValueError(error_msg)

        missing_imputed_train = [
            col for col in imputed_variables if col not in X_train.columns
        ]
        if missing_imputed_train:
            error_msg = f"Missing imputed variable columns in training data: {missing_imputed_train}"
            log.error(error_msg)
            raise ValueError(error_msg)

        # Validate that predictor columns exist in test data (imputed variables may not be present in test)
        missing_predictors_test = [
            col for col in predictors if col not in X_test.columns
        ]
        if missing_predictors_test:
            error_msg = f"Missing predictor columns in test data: {missing_predictors_test}"
            log.error(error_msg)
            raise ValueError(error_msg)

        # Validate quantiles if provided
        if quantiles:
            invalid_quantiles = [q for q in quantiles if not 0 <= q <= 1]
            if invalid_quantiles:
                error_msg = f"Invalid quantiles (must be between 0 and 1): {invalid_quantiles}"
                log.error(error_msg)
                raise ValueError(error_msg)

        log.info(
            f"Generating imputations for {len(model_classes)} model classes"
        )
        log.info(
            f"Training data shape: {X_train.shape}, Test data shape: {X_test.shape}"
        )
        log.info(
            f"Using {len(predictors)} predictors and imputing {len(imputed_variables)} variables"
        )
        log.info(
            f"Evaluating at {len(quantiles) if quantiles else 'default'} quantiles"
        )

        method_imputations: Dict[str, Dict[float, Any]] = {}

        fitted_models: Dict[str, Any] = {}
        for model_class in model_classes:
            model_name = model_class.__name__
            log.info(f"Processing model: {model_name}")
            method_imputations[model_name] = {}

            try:
                # Instantiate the model
                model = model_class()

                # Handle QuantReg which needs quantiles during fitting
                if model_class == QuantReg:
                    log.info(f"Fitting {model_name} with explicit quantiles")
                    fitted_model = model.fit(
                        X_train,
                        predictors,
                        imputed_variables,
                        quantiles=quantiles,
                    )
                else:
                    log.info(f"Fitting {model_name}")
                    fitted_model = model.fit(
                        X_train, predictors, imputed_variables
                    )

                fitted_models[model_name] = fitted_model

                # Get predictions
                log.info(f"Generating predictions with {model_name}")
                imputations = fitted_model.predict(X_test, quantiles)
                method_imputations[model_name] = imputations

                # Log a summary of predictions
                num_quantiles = len(imputations)
                first_quantile = next(iter(imputations.keys()))
                first_pred = imputations[first_quantile]

                if isinstance(first_pred, np.ndarray):
                    pred_shape = first_pred.shape
                elif isinstance(first_pred, pd.DataFrame):
                    pred_shape = first_pred.shape
                else:
                    pred_shape = "unknown"

                log.info(
                    f"Model {model_name} generated predictions for {num_quantiles} quantiles with shape {pred_shape}"
                )

            except Exception as model_error:
                log.error(
                    f"Error processing model {model_name}: {str(model_error)}"
                )
                raise RuntimeError(
                    f"Failed to process model {model_name}: {str(model_error)}"
                ) from model_error

        log.info(
            f"Successfully generated imputations for all {len(model_classes)} models"
        )
        return method_imputations

    except ValueError as e:
        # Re-raise validation errors directly
        raise e
    except Exception as e:
        log.error(f"Unexpected error during imputation generation: {str(e)}")
        raise RuntimeError(f"Failed to generate imputations: {str(e)}") from e

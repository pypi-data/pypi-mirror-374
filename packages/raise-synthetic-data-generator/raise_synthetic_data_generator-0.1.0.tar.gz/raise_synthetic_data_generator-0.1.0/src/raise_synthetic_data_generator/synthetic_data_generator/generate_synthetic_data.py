# -*- coding: utf-8 -*-
"""
    RAISE Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""

# ============================================
# IMPORTS
# ============================================

# Stdlib imports
import inspect
import traceback
from typing import Union
from pathlib import Path

# Third-party app imports
import pandas as pd

# Imports from your apps
from raise_synthetic_data_generator.synthetic_data_generator.synthetic_data_generator import (
    SyntheticDataGenerator,
)
from raise_synthetic_data_generator.sd_evaluation.synthetic_data_evaluation import (
    SyntheticDataEvaluator,
)
from raise_synthetic_data_generator.custom_exceptions import SDGModelSelectionError
from raise_synthetic_data_generator import LogClass
from raise_synthetic_data_generator.utils.paths import prepare_output_folder


# ============================================
# GLOBAL CONSTANTS
# ============================================
AVAILABLE_MODELS = ["CTGAN", "TVAE", "Copulas", "auto-select"]
LOGGER = LogClass()

# ============================================
# CLASSES
# ============================================


# ============================================
# PUBLIC METHODS
# ============================================


def generate_synthetic_data(
    dataset: Union[str, pd.DataFrame],
    selected_model: str = "auto-select",
    n_samples: int = None,
    evaluation_report: bool = True,
    output_dir: Union[str, Path] = None,
    run_name: str = None,
):
    try:
        input_data = _load_dataset(dataset)
        LOGGER.log_info("Original data file read and validated!")

        LOGGER.log_info("Proceeding with output folder creation...")
        output_folder = _get_output_folder(output_dir, run_name)
        LOGGER.log_info("Output folder successfully created!")

        # Select synthetic data generation model
        LOGGER.log_info("Proceeding to model selection...")
        if selected_model == "auto-select":
            selected_model = _select_synthetic_data_generation_model(dataset=input_data)
        elif selected_model not in AVAILABLE_MODELS:
            raise SDGModelSelectionError(
                f"Selected model ({selected_model}) is not available"
            )
        LOGGER.log_info(f"{selected_model} model has been selected!")
        LOGGER.log_info("Proceeding with synthetic data generation...")

        # Generate and store synthetic data and model info
        synthetic_data_generator = SyntheticDataGenerator(
            dataset=input_data, sdg_model=selected_model
        )
        if n_samples is None:
            n_samples = len(input_data)
        synthetic_data = synthetic_data_generator.generate_synthetic_data(
            n_samples=n_samples
        )
        synthetic_data_path = output_folder / "synthetic_data.csv"
        if synthetic_data_path.exists():
            LOGGER.log_warning(f"File {synthetic_data_path.name} will be overwritten!")
        synthetic_data.to_csv(synthetic_data_path, index=False)
        # Store model info
        synthetic_data_generator.store_model_info(output_folder=output_folder)
        LOGGER.log_info(
            f"Synthetic data generated and saved successfully in: {output_folder}."
        )
        LOGGER.log_info("Proceeding with synthetic data evaluation...")

        # Evaluate synthetic data (optional)
        if evaluation_report:
            synthetic_data_evaluator = SyntheticDataEvaluator(
                original_dataset=input_data,
                synthetic_data=synthetic_data,
                output_folder=output_folder,
                information_text=synthetic_data_generator.get_model_info(),
            )
            synthetic_data_evaluator.evaluate_data()
        LOGGER.log_info(
            f"Synthetic data evaluation report generated and saved successfully in: {output_folder}."
        )

    except Exception as exception:
        # Log and raise the exception
        function_name = inspect.currentframe().f_code.co_name
        error_msg = (
            f"{function_name}() : An exception has occurred\n{traceback.format_exc()}"
        )
        LOGGER.log_error(error_msg)
        raise exception


# ============================================
# PRIVATE METHODS
# ============================================


def _select_synthetic_data_generation_model(dataset: pd.DataFrame):
    n_rows = dataset.shape[0]
    n_columns = dataset.shape[1]

    if n_rows > 2000:
        if n_rows > 3000 and n_columns < 20:
            return "CTGAN"
        else:
            return "TVAE"
    elif n_rows > 100 and n_rows < 2000:
        return "Copulas"
    else:
        raise SDGModelSelectionError(
            "There is no enough data to train a synthetic data generation model"
        )


def _load_dataset(dataset: Union[str, pd.DataFrame]) -> pd.DataFrame:
    if isinstance(dataset, str):
        dataset_path = Path(dataset)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Input file '{dataset}' does not exist.")
        if not dataset_path.is_file() or not dataset_path.stat().st_size:
            raise Exception(f"Input file '{dataset}' is not a valid, non-empty file.")
        try:
            input_data = pd.read_csv(dataset)
        except Exception as e:
            raise Exception(f"Failed to read input file '{dataset}': {e}")
    else:
        input_data = dataset.copy()
    return input_data


def _get_output_folder(output_dir, run_name):
    output_folder = prepare_output_folder(output_dir=output_dir, run_name=run_name)
    output_folder = Path(output_folder).resolve(strict=False)
    if not str(output_folder).startswith(str(Path.cwd().resolve())):
        raise ValueError("Invalid output_folder: directory traversal detected.")
    return output_folder


# ============================================
# MAIN BLOCK
# ============================================

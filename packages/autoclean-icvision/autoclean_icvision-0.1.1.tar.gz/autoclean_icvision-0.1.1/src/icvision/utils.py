"""
Utility functions for ICVision.

This module contains helper functions for file I/O, validation, and data loading
that support the main functionality of the ICVision package.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import mne
import pandas as pd
from dotenv import load_dotenv

from .config import COMPONENT_LABELS

# Set up logging for the module
logger = logging.getLogger("icvision.utils")


def load_raw_data(raw_input: Union[str, Path, mne.io.BaseRaw]) -> mne.io.BaseRaw:
    """
    Load raw EEG data from file path or return existing Raw object.

    Supports EEGLAB .set/.fdt format (continuous data only) and MNE-compatible formats.
    If an EEGLAB .set file contains epoched data, an informative error will be raised
    with instructions on how to convert to continuous data.

    Args:
        raw_input: Either a file path (str/Path) or an existing mne.io.Raw object.
                   For EEGLAB format, provide path to .set file (continuous data only).

    Returns:
        Loaded mne.io.Raw object.

    Raises:
        FileNotFoundError: If file path does not exist.
        ValueError: If file format is not supported or contains epoched data.
        RuntimeError: If data loading fails.

    Example:
        >>> raw = load_raw_data("data/sub-01_task-rest_eeg.set")  # Continuous raw data
        >>> raw = load_raw_data(existing_raw_object)
    """
    if isinstance(raw_input, mne.io.BaseRaw):
        logger.info("Using provided mne.io.BaseRaw object")
        return raw_input

    # Convert to Path object for easier handling
    file_path = Path(raw_input)

    if not file_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {file_path}")

    file_extension = file_path.suffix.lower()

    if file_extension == ".set":
        logger.debug("Loading EEGLAB data from: %s", file_path)
        try:
            # Suppress MNE montage warnings for cleaner output
            import warnings

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", message="Not setting positions.*eog channels.*montage", category=RuntimeWarning
                )
                # First try to read as raw data
                raw = mne.io.read_raw_eeglab(file_path, preload=True)
        except TypeError as e:
            # Check if the error is due to epoched data
            if "trials" in str(e).lower() and "epochs" in str(e).lower():
                # Provide graceful error message for epoched data
                raise ValueError(
                    f"The EEGLAB file '{file_path}' contains epoched data, but ICVision currently only supports "
                    f"continuous (raw) EEG data. Please use continuous data for ICA component classification. "
                    f"You can export continuous data from EEGLAB using: File > Export > Data and epochs > "
                    f"Export epoch data, or use Tools > Remove epochs to convert back to continuous data."
                )
            else:
                # Re-raise if it's a different error
                raise
    elif file_extension == ".fif":
        logger.debug("Loading MNE FIF data from: %s", file_path)
        raw = mne.io.read_raw_fif(file_path, preload=True)
    elif file_extension in [".bdf", ".edf"]:
        logger.debug("Loading EDF/BDF data from: %s", file_path)
        raw = mne.io.read_raw_edf(file_path, preload=True)
    elif file_extension == ".vhdr":
        logger.debug("Loading BrainVision data from: %s", file_path)
        raw = mne.io.read_raw_brainvision(file_path, preload=True)
    else:
        raise ValueError(
            "Unsupported file format: {}. Supported formats: .set (EEGLAB), .fif (MNE), .edf, .bdf, .vhdr".format(
                file_extension
            )
        )

    logger.debug(
        "Successfully loaded raw data: %d channels, %d samples, %.1f Hz",
        raw.info["nchan"],
        raw.n_times,
        raw.info["sfreq"],
    )
    return raw


def check_eeglab_ica_availability(set_file_path: Union[str, Path]) -> bool:
    """
    Check if an EEGLAB .set file contains ICA data.

    Args:
        set_file_path: Path to the EEGLAB .set file.

    Returns:
        True if ICA data is available, False otherwise.
    """
    try:
        # Suppress MNE montage warnings for cleaner output
        import warnings

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", message="Not setting positions.*eog channels.*montage", category=RuntimeWarning
            )
            # Attempt to read ICA data from the .set file
            ica = mne.preprocessing.read_ica_eeglab(set_file_path)
        # Additional check to ensure ICA was actually fitted
        if hasattr(ica, "n_components_") and ica.n_components_ > 0:
            return True
        else:
            logger.debug("EEGLAB file exists but contains no fitted ICA components: %s", set_file_path)
            return False
    except Exception as e:
        logger.debug("No ICA data found in EEGLAB file %s: %s", set_file_path, str(e))
        return False


def load_ica_data(ica_input: Union[str, Path, mne.preprocessing.ICA]) -> mne.preprocessing.ICA:
    """
    Load ICA data from file path or return existing ICA object.

    Supports MNE .fif format and EEGLAB .set format for ICA objects.

    Args:
        ica_input: Either a file path (str/Path) or an existing mne.preprocessing.ICA object.

    Returns:
        Loaded mne.preprocessing.ICA object.

    Raises:
        FileNotFoundError: If file path does not exist.
        ValueError: If file format is not supported.
        RuntimeError: If data loading fails.

    Example:
        >>> ica = load_ica_data("data/sub-01_task-rest_ica.fif")
        >>> ica = load_ica_data("data/sub-01_task-rest_eeg.set")  # EEGLAB with ICA
        >>> ica = load_ica_data(existing_ica_object)
    """
    if isinstance(ica_input, mne.preprocessing.ICA):
        logger.info("Using provided mne.preprocessing.ICA object")
        return ica_input

    # Convert to Path object for easier handling
    file_path = Path(ica_input)

    if not file_path.exists():
        raise FileNotFoundError(f"ICA file not found: {file_path}")

    file_extension = file_path.suffix.lower()

    if file_extension == ".fif":
        logger.debug("Loading MNE ICA from: %s", file_path)
        try:
            ica = mne.preprocessing.read_ica(file_path)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load MNE ICA from .fif file '{file_path}'. "
                f"File may be corrupted or contain invalid ICA data. Error: {str(e)}"
            )
    elif file_extension == ".set":
        logger.debug("Loading EEGLAB ICA from: %s", file_path)
        try:
            # Suppress MNE montage warnings for cleaner output
            import warnings

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", message="Not setting positions.*eog channels.*montage", category=RuntimeWarning
                )
                ica = mne.preprocessing.read_ica_eeglab(file_path)
        except Exception as e:
            error_msg = str(e).lower()
            if "ica" in error_msg or "component" in error_msg or "no ica" in error_msg:
                raise RuntimeError(
                    f"No ICA components found in EEGLAB .set file '{file_path}'. "
                    f"Run ICA decomposition in EEGLAB first, or provide separate MNE .fif ICA file."
                )
            else:
                raise RuntimeError(
                    f"Failed to load EEGLAB ICA from .set file '{file_path}'. "
                    f"File may be corrupted or incompatible. Error: {str(e)}"
                )
    else:
        raise ValueError(
            "Unsupported ICA file format: {}. Supported formats: .fif (MNE), .set (EEGLAB)".format(file_extension)
        )

    format_name = "MNE" if file_extension == ".fif" else "EEGLAB"
    logger.debug("Successfully loaded %s ICA: %d components", format_name, ica.n_components_)
    return ica


def validate_inputs(raw: mne.io.Raw, ica: mne.preprocessing.ICA) -> None:
    """
    Validate that raw and ICA data are compatible.

    Args:
        raw: The mne.io.Raw object.
        ica: The mne.preprocessing.ICA object.

    Raises:
        ValueError: If inputs are not compatible.
    """
    # Check if ICA was fitted
    if not hasattr(ica, "n_components_") or ica.n_components_ is None:
        raise ValueError("ICA object appears to not be fitted. Please fit ICA first.")

    # Check basic compatibility (number of channels)
    if len(ica.ch_names) != len(raw.ch_names):
        logger.warning(
            "Channel count mismatch: ICA has %d channels, Raw has %d channels. This may cause issues.",
            len(ica.ch_names),
            len(raw.ch_names),
        )

    # Check for sufficient data length
    if raw.n_times < 1000:  # Arbitrary minimum
        logger.warning(
            "Raw data is very short (%d samples). Results may be unreliable.",
            raw.n_times,
        )

    logger.debug("Input validation passed")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe filesystem usage.

    Args:
        filename: Raw filename to sanitize.

    Returns:
        Sanitized filename safe for filesystem use.
    """
    import re

    # Remove or replace problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(". ")
    # Limit length to reasonable filesystem limits
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    # Ensure it's not empty
    if not sanitized:
        sanitized = "unknown"
    return sanitized


def extract_input_basename(input_path: Union[str, Path]) -> str:
    """
    Extract basename from input file path for use in output naming.

    Args:
        input_path: Path to input file.

    Returns:
        Sanitized basename (without extension) for output naming.
    """
    if input_path is None:
        return "icvision"

    path = Path(input_path)
    # Get filename without extension
    basename = path.stem
    # Sanitize for filesystem safety
    return sanitize_filename(basename)


def create_output_directory(output_dir: Optional[Union[str, Path]], input_basename: Optional[str] = None) -> Path:
    """
    Create output directory for results.

    Args:
        output_dir: Directory path. If None, uses 'autoclean_icvision_results' in current directory.
        input_basename: Basename from input file (unused but kept for API compatibility).

    Returns:
        Path to the created directory.
    """
    if output_dir is None:
        # Always use the same directory name for consistency across multiple files
        dir_name = "autoclean_icvision_results"
        output_dir = Path.cwd() / dir_name
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("Output directory: %s", output_dir)
    return output_dir


def validate_api_key(api_key: Optional[str]) -> str:
    """
    Validate and retrieve OpenAI API key.

    Args:
        api_key: API key string or None to use environment variable.

    Returns:
        Valid API key string.

    Raises:
        ValueError: If no valid API key is found.
    """
    if api_key:
        return api_key

    # Try environment variable
    load_dotenv()
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key

    raise ValueError(
        "No OpenAI API key provided. Either pass api_key parameter or set " "OPENAI_API_KEY environment variable."
    )


def save_results(
    results_df: pd.DataFrame, output_dir: Path, input_basename: Optional[str] = None, filename: Optional[str] = None
) -> Path:
    """
    Save classification results to CSV file.

    Args:
        results_df: DataFrame with classification results.
        output_dir: Output directory.
        input_basename: Basename from input file for default naming.
        filename: Custom filename for the CSV file. If None, uses basename_icvis_results.csv.

    Returns:
        Path to the saved file.
    """
    if filename is None:
        if input_basename is None:
            filename = "icvision_results.csv"
        else:
            filename = f"{input_basename}_icvis_results.csv"

    output_path = output_dir / filename
    if results_df.empty and len(results_df.columns) == 0:
        # Create empty CSV with expected headers for completely empty dataframe
        expected_columns = [
            "component_index",
            "component_name",
            "label",
            "confidence",
            "reason",
            "exclude_vision",
        ]
        empty_df_with_columns = pd.DataFrame(columns=expected_columns)
        empty_df_with_columns.to_csv(output_path, index=False)
    else:
        results_df.to_csv(output_path, index=False)
    logger.debug("Results saved to: %s", output_path)
    return output_path


def format_summary_stats(
    results_df: pd.DataFrame, cost_tracking: Optional[dict] = None, model_name: Optional[str] = None
) -> str:
    """
    Create a formatted summary of classification results.

    Args:
        results_df: DataFrame with classification results.
        cost_tracking: Dictionary with cost tracking information (optional).
        model_name: OpenAI model name used (optional).

    Returns:
        Formatted string summary.
    """
    if results_df.empty:
        summary_lines = [
            "ICVision Classification Summary:",
            "=" * 35,
            "Total components classified: 0",
            "Components marked for exclusion: 0",
            "",
            "Classification breakdown:",
        ]
        for label in COMPONENT_LABELS:
            summary_lines.append(f"- {label.title()}: 0")

        # Add cost information if available
        if cost_tracking and cost_tracking.get("requests_count", 0) > 0:
            summary_lines.extend(
                [
                    "",
                    "OpenAI API Cost Summary:",
                    "=" * 25,
                    f"Total cost: ${cost_tracking['total_cost']:.6f}",
                    f"Model used: {model_name or 'Unknown'}",
                    f"Total requests: {cost_tracking['requests_count']}",
                    f"Input tokens: {cost_tracking['total_input_tokens']:,}",
                    f"Output tokens: {cost_tracking['total_output_tokens']:,}",
                    f"Cached tokens: {cost_tracking['total_cached_tokens']:,} (saved cost)",
                ]
            )

        return "\n".join(summary_lines)

    total_components = len(results_df)

    # Count by label
    label_counts = results_df["label"].value_counts()

    # Count excluded components
    excluded_count = results_df.get("exclude_vision", pd.Series(dtype=bool)).sum()

    summary_lines = [
        "ICVision Classification Summary:",
        "=" * 35,
        f"Total components classified: {total_components}",
        f"Components marked for exclusion: {excluded_count}",
        "",
        "Classification breakdown:",
    ]

    # Show all labels, even if count is 0
    for label in COMPONENT_LABELS:
        count = label_counts.get(label, 0)
        summary_lines.append(f"- {label.title()}: {count}")

    # Add cost information if available
    if cost_tracking and cost_tracking.get("requests_count", 0) > 0:
        summary_lines.extend(
            [
                "",
                "OpenAI API Cost Summary:",
                "=" * 25,
                f"Total cost: ${cost_tracking['total_cost']:.6f}",
                f"Model used: {model_name or 'Unknown'}",
                f"Total requests: {cost_tracking['requests_count']}",
                f"Input tokens: {cost_tracking['total_input_tokens']:,}",
                f"Output tokens: {cost_tracking['total_output_tokens']:,}",
                f"Cached tokens: {cost_tracking['total_cached_tokens']:,} (saved cost)",
            ]
        )

    return "\n".join(summary_lines)


def validate_classification_results(results_df: pd.DataFrame) -> bool:
    """
    Validate that classification results are properly formatted.

    Args:
        results_df: DataFrame with classification results.

    Returns:
        True if results are valid, False otherwise.
    """
    required_cols = {
        "component_index",
        "label",
        "confidence",
        "reason",
        "exclude_vision",
    }

    # Check required columns
    if not required_cols.issubset(results_df.columns):
        missing = required_cols - set(results_df.columns)
        missing_col = next(iter(missing))  # Get first missing column for specific error message
        raise ValueError(f"Missing required column: {missing_col}")

    # Validate 'label' values
    invalid_labels = set(results_df["label"]) - set(COMPONENT_LABELS)
    if invalid_labels:
        logger.error("Invalid labels found in results: %s", invalid_labels)
        invalid_label = next(iter(invalid_labels))  # Get first invalid label
        raise ValueError(f"Invalid label '{invalid_label}' found")

    # Check confidence range and type
    try:
        invalid_confidences = results_df[~results_df["confidence"].between(0, 1)]
        if not invalid_confidences.empty:
            logger.error("Confidence values must be between 0 and 1")
            invalid_conf = invalid_confidences["confidence"].iloc[0]
            if isinstance(invalid_conf, str):
                raise ValueError(f"Confidence score '{invalid_conf}' is not a float")
            else:
                raise ValueError(f"Confidence score {invalid_conf:.2f} is outside the valid range")
    except TypeError:
        # Handle non-numeric confidence values
        for _, conf in results_df["confidence"].items():
            if not isinstance(conf, (int, float)):
                raise ValueError(f"Confidence score '{conf}' is not a float")

    logger.debug("Classification results validation passed")
    return True


def calculate_openai_cost(
    input_tokens: int, output_tokens: int, model_name: str, cached_tokens: int = 0
) -> Dict[str, Any]:
    """
    Calculate OpenAI API costs based on token usage.

    Args:
        input_tokens: Number of input tokens used.
        output_tokens: Number of output tokens generated.
        model_name: OpenAI model name (e.g., "gpt-4.1", "gpt-4.1-mini").
        cached_tokens: Number of cached input tokens (if any).

    Returns:
        Dictionary with cost breakdown: {"input_cost", "output_cost", "total_cost"}
        All costs in USD.
    """
    from .config import OPENAI_PRICING

    # Normalize model name for pricing lookup
    pricing_key = model_name.lower()
    if pricing_key not in OPENAI_PRICING:
        # Try without version suffix for compatibility
        base_model = pricing_key.split("-")[0] + "-" + pricing_key.split("-")[1]
        if base_model in OPENAI_PRICING:
            pricing_key = base_model
        else:
            logger.warning("Unknown model '%s' for cost calculation, using gpt-4.1 pricing", model_name)
            pricing_key = "gpt-4.1"

    pricing = OPENAI_PRICING[pricing_key]

    # Calculate costs (pricing is per 1M tokens)
    regular_input_tokens = max(0, input_tokens - cached_tokens)

    input_cost = (regular_input_tokens * pricing["input"] / 1_000_000) + (
        cached_tokens * pricing["cached_input"] / 1_000_000
    )
    output_cost = output_tokens * pricing["output"] / 1_000_000
    total_cost = input_cost + output_cost

    return {
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6),
        "model": pricing_key,
        "input_tokens": float(input_tokens),
        "output_tokens": float(output_tokens),
        "cached_tokens": float(cached_tokens),
    }


def save_cleaned_raw_data(
    raw_cleaned: mne.io.BaseRaw,
    original_raw_path: Optional[Union[str, Path]],
    output_dir: Path,
    input_basename: Optional[str] = None,
    filename_prefix: Optional[str] = None,
) -> Optional[Path]:
    """
    Save cleaned raw EEG data in the same format as the original input.

    Args:
        raw_cleaned: The cleaned MNE Raw object with artifacts removed.
        original_raw_path: Path to original raw data file (to determine format).
                          None if original was an MNE object.
        output_dir: Directory to save the cleaned data.
        input_basename: Basename from input file for default naming.
        filename_prefix: Custom prefix for the output filename. If None, uses basename_icvis_cleaned.

    Returns:
        Path to saved cleaned data file, or None if saving failed or format not supported.
    """
    # Set default filename prefix based on basename
    if filename_prefix is None:
        if input_basename is None:
            filename_prefix = "icvision_cleaned"
        else:
            filename_prefix = f"{input_basename}_icvis_cleaned"

    if original_raw_path is None:
        logger.info("Original raw data was an MNE object - saving cleaned data as .fif file")
        output_filename = f"{filename_prefix}_raw.fif"
        output_path = output_dir / output_filename
        try:
            raw_cleaned.save(output_path, overwrite=True)
            logger.info("Cleaned raw data saved to: %s", output_path)
            return output_path
        except Exception as e:
            logger.error("Failed to save cleaned raw data to %s: %s", output_path, e)
            return None

    # Determine format from original file
    original_path = Path(original_raw_path)
    file_extension = original_path.suffix.lower()

    if file_extension == ".set":
        # Save as EEGLAB .set/.fdt format
        output_filename = f"{filename_prefix}_raw.set"
        output_path = output_dir / output_filename
        try:
            # Use MNE's EEGLAB export functionality
            raw_cleaned.export(output_path, fmt="eeglab", overwrite=True)
            logger.info("Cleaned raw data saved to EEGLAB format: %s", output_path)
            return output_path
        except Exception as e:
            logger.error("Failed to save cleaned raw data to EEGLAB format %s: %s", output_path, e)
            # Fallback to .fif format
            logger.info("Falling back to .fif format for cleaned raw data")
            output_filename_fif = f"{filename_prefix}_raw.fif"
            output_path_fif = output_dir / output_filename_fif
            try:
                raw_cleaned.save(output_path_fif, overwrite=True)
                logger.info("Cleaned raw data saved to .fif format: %s", output_path_fif)
                return output_path_fif
            except Exception as e_fif:
                logger.error("Failed to save cleaned raw data to .fif format %s: %s", output_path_fif, e_fif)
                return None

    elif file_extension == ".fif":
        # Save as MNE .fif format
        output_filename = f"{filename_prefix}_raw.fif"
        output_path = output_dir / output_filename
        try:
            raw_cleaned.save(output_path, overwrite=True)
            logger.info("Cleaned raw data saved to: %s", output_path)
            return output_path
        except Exception as e:
            logger.error("Failed to save cleaned raw data to %s: %s", output_path, e)
            return None

    else:
        # For other formats, save as .fif (most compatible)
        logger.info("Original format %s not supported for export - saving as .fif", file_extension)
        output_filename = f"{filename_prefix}_raw.fif"
        output_path = output_dir / output_filename
        try:
            raw_cleaned.save(output_path, overwrite=True)
            logger.info("Cleaned raw data saved to .fif format: %s", output_path)
            return output_path
        except Exception as e:
            logger.error("Failed to save cleaned raw data to %s: %s", output_path, e)
            return None

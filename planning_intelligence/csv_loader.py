"""
CSV File Loader
Loads current and previous data files from local CSV files
and returns normalized row dicts ready for the analytics pipeline.

Supports: .csv files

Environment variables (optional):
  CSV_DATA_PATH        Path to CSV files (default: sample_data/)
  CSV_CURRENT_FILE     Current file name (default: planning_data_2000_records.csv)
  CSV_PREVIOUS_FILE    Previous file name (default: planning_data_2000_records.csv)
"""
import io
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Required columns that must exist in the CSV
REQUIRED_COLUMNS = {"LOCID", "PRDID", "GSCEQUIPCAT"}

# SAP column → canonical name mapping
COLUMN_ALIASES = {
    "LOC ID": "LOCID",
    "PRD ID": "PRDID",
    "MATERIAL ID": "PRDID",
    "EQUIPMENT CATEGORY": "GSCEQUIPCAT",
}

# Defaults — override via env vars
DEFAULT_DATA_PATH = "sample_data"
DEFAULT_CURRENT_FILE = "planning_data_10000_records.csv"
DEFAULT_PREVIOUS_FILE = "planning_data_10000_records.csv"


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def load_current_from_csv() -> list:
    """
    Loads current data from CSV file.
    Returns current_rows as list[dict].
    Raises CSVLoaderError on any failure.
    """
    data_path = os.environ.get("CSV_DATA_PATH", DEFAULT_DATA_PATH).strip()
    current_file = os.environ.get("CSV_CURRENT_FILE", DEFAULT_CURRENT_FILE).strip()

    # Resolve the actual path - try multiple strategies
    current_path = None
    
    # Strategy 1: Direct path (relative to current working directory)
    candidate = os.path.join(data_path, current_file)
    if os.path.exists(candidate):
        current_path = candidate
        logger.info(f"Found CSV at (direct path): {candidate}")
    
    # Strategy 2: Relative to this script's directory (planning_intelligence/)
    if not current_path:
        candidate = os.path.join(os.path.dirname(__file__), data_path, current_file)
        if os.path.exists(candidate):
            current_path = candidate
            logger.info(f"Found CSV at (relative to script): {candidate}")
    
    # Strategy 3: Absolute path from workspace root
    if not current_path:
        candidate = os.path.join(os.path.dirname(os.path.dirname(__file__)), data_path, current_file)
        if os.path.exists(candidate):
            current_path = candidate
            logger.info(f"Found CSV at (absolute from root): {candidate}")
    
    # If still not found, raise error with diagnostic info
    if not current_path:
        logger.error(f"CSV file not found. Tried:")
        logger.error(f"  1. {os.path.join(data_path, current_file)}")
        logger.error(f"  2. {os.path.join(os.path.dirname(__file__), data_path, current_file)}")
        logger.error(f"  3. {os.path.join(os.path.dirname(os.path.dirname(__file__)), data_path, current_file)}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Script directory: {os.path.dirname(__file__)}")
        raise CSVLoaderError(
            f"CSV file not found: {current_file}\n"
            f"Tried paths:\n"
            f"  1. {os.path.join(data_path, current_file)}\n"
            f"  2. {os.path.join(os.path.dirname(__file__), data_path, current_file)}\n"
            f"  3. {os.path.join(os.path.dirname(os.path.dirname(__file__)), data_path, current_file)}\n"
            f"Current working directory: {os.getcwd()}"
        )

    logger.info(f"Loading CSV file from: {current_path}")
    logger.info(f"Current file: {current_file}")

    current_df = load_csv_file(current_path, label="current")
    current_df = standardize_columns(current_df)
    validate_required_columns(current_df, label="current")

    logger.info(f"✅ Loaded {len(current_df)} current records")

    return current_df.to_dict(orient="records")


def load_current_previous_from_csv() -> tuple:
    """
    Loads current and previous data files from local CSV files.
    Returns (current_rows, previous_rows) as list[dict].
    Raises CSVLoaderError on any failure.
    
    Note: This function is kept for backward compatibility.
    For new code, use load_current_from_csv() since previous is merged in current.
    """
    data_path = os.environ.get("CSV_DATA_PATH", DEFAULT_DATA_PATH).strip()
    current_file = os.environ.get("CSV_CURRENT_FILE", DEFAULT_CURRENT_FILE).strip()
    previous_file = os.environ.get("CSV_PREVIOUS_FILE", DEFAULT_PREVIOUS_FILE).strip()

    current_path = os.path.join(data_path, current_file)
    previous_path = os.path.join(data_path, previous_file)

    logger.info(f"Loading CSV files from: {data_path}")
    logger.info(f"Current file: {current_file}")
    logger.info(f"Previous file: {previous_file}")

    current_df = load_csv_file(current_path, label="current")
    previous_df = load_csv_file(previous_path, label="previous")

    current_df = standardize_columns(current_df)
    previous_df = standardize_columns(previous_df)

    validate_required_columns(current_df, label="current")
    validate_required_columns(previous_df, label="previous")

    logger.info(f"✅ Loaded {len(current_df)} current records and {len(previous_df)} previous records")

    return current_df.to_dict(orient="records"), previous_df.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Load CSV file
# ---------------------------------------------------------------------------

def load_csv_file(filepath: str, label: str = "file") -> "pd.DataFrame":
    """Loads a CSV file into a pandas DataFrame."""
    try:
        import pandas as pd
    except ImportError:
        raise CSVLoaderError("pandas not installed. Add to requirements.txt.")

    # Check if file exists
    if not os.path.exists(filepath):
        raise CSVLoaderError(
            f"CSV file not found: {filepath}\n"
            f"Please verify:\n"
            f"  1. File exists at the specified path\n"
            f"  2. Path is correct: {filepath}\n"
            f"  3. File is readable\n"
            f"  4. File is not empty"
        )

    try:
        file_size = os.path.getsize(filepath)
        logger.info(f"Loading {label} CSV file: {filepath} ({file_size} bytes)")

        # Try UTF-8 first, fall back to latin-1 for special characters
        try:
            df = pd.read_csv(filepath, dtype=str, encoding='utf-8')
            logger.info(f"Successfully parsed {label} with UTF-8 encoding")
        except UnicodeDecodeError:
            logger.info(f"UTF-8 decode failed for {label}, trying latin-1")
            df = pd.read_csv(filepath, dtype=str, encoding='latin-1')
            logger.info(f"Successfully parsed {label} with latin-1 encoding")

        df = df.fillna("")
        
        if df.empty:
            raise CSVLoaderError(f"CSV file is empty: {filepath}")

        logger.info(f"Loaded {label}: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"Columns in {label}: {list(df.columns)}")

        return df

    except CSVLoaderError:
        raise
    except Exception as e:
        logger.error(f"Failed to parse CSV file ({label}): {e}")
        raise CSVLoaderError(f"Failed to parse CSV file ({label}): {e}")


# ---------------------------------------------------------------------------
# Standardize + validate columns
# ---------------------------------------------------------------------------

def standardize_columns(df):
    """Standardize column names to uppercase and apply aliases."""
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df.rename(columns=COLUMN_ALIASES)


def validate_required_columns(df, label: str = "file"):
    """Validate that all required columns are present."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        logger.error(f"Missing required columns in {label}: {sorted(missing)}")
        logger.error(f"Found columns: {sorted(df.columns.tolist())}")
        raise CSVLoaderError(
            f"Missing required columns in {label}: {sorted(missing)}. "
            f"Found: {sorted(df.columns.tolist())}. "
            f"Required: {sorted(REQUIRED_COLUMNS)}"
        )
    logger.info(f"✅ All required columns present in {label}: {sorted(REQUIRED_COLUMNS)}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class CSVLoaderError(Exception):
    """Raised for any CSV file loading failure."""
    pass

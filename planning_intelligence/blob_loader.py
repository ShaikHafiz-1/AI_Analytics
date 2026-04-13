"""
Azure Blob Storage Loader
Downloads current and previous data files from Azure Blob Storage
and returns normalized row dicts ready for the analytics pipeline.

Supports: .xlsx, .xls, .csv

Required environment variables:
  BLOB_CONNECTION_STRING   Azure Storage connection string
  BLOB_CONTAINER_NAME      Container name (default: planning-data)
  BLOB_CURRENT_FILE        Blob name for current file (default: current.csv)
  BLOB_PREVIOUS_FILE       Blob name for previous file (default: previous.csv)
"""
import io
import os
import logging

logger = logging.getLogger(__name__)

# Required columns that must exist in the Excel sheet
REQUIRED_COLUMNS = {"LOCID", "PRDID", "GSCEQUIPCAT"}

# SAP column → canonical name mapping
COLUMN_ALIASES = {
    "LOC ID": "LOCID",
    "PRD ID": "PRDID",
    "MATERIAL ID": "PRDID",
    "EQUIPMENT CATEGORY": "GSCEQUIPCAT",
}

# Defaults — override via env vars
DEFAULT_CONTAINER = "planning-data"
DEFAULT_CURRENT_BLOB = "current.csv"
DEFAULT_PREVIOUS_BLOB = "previous.csv"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def load_current_previous_from_blob() -> tuple:
    """
    Downloads current and previous data files from Azure Blob Storage.
    Returns (current_rows, previous_rows) as list[dict].
    Raises BlobLoaderError on any failure.
    """
    connection_string = _require_env("BLOB_CONNECTION_STRING")
    container = os.environ.get("BLOB_CONTAINER_NAME", DEFAULT_CONTAINER).strip()
    current_blob = os.environ.get("BLOB_CURRENT_FILE", DEFAULT_CURRENT_BLOB).strip()
    previous_blob = os.environ.get("BLOB_PREVIOUS_FILE", DEFAULT_PREVIOUS_BLOB).strip()

    current_bytes = download_blob(connection_string, container, current_blob)
    previous_bytes = download_blob(connection_string, container, previous_blob)

    current_df = load_file_from_bytes(current_bytes, label="current", filename=current_blob)
    previous_df = load_file_from_bytes(previous_bytes, label="previous", filename=previous_blob)

    current_df = standardize_columns(current_df)
    previous_df = standardize_columns(previous_df)

    validate_required_columns(current_df, label="current")
    validate_required_columns(previous_df, label="previous")

    return current_df.to_dict(orient="records"), previous_df.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Download from Blob
# ---------------------------------------------------------------------------

def download_blob(connection_string: str, container: str, blob_name: str) -> bytes:
    """Downloads a blob and returns its content as bytes."""
    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        raise BlobLoaderError("azure-storage-blob not installed. Add to requirements.txt.")

    try:
        client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = client.get_blob_client(container=container, blob=blob_name)
        data = blob_client.download_blob().readall()
        logger.info(f"Downloaded blob {container}/{blob_name} ({len(data)} bytes)")
        return data
    except Exception as e:
        msg = str(e)
        error_lower = msg.lower()
        
        # Detailed error messages for debugging
        if "blobnotfound" in error_lower or "404" in msg or "does not exist" in error_lower:
            raise BlobLoaderError(
                f"Blob not found: {container}/{blob_name}\n"
                f"Please verify:\n"
                f"  1. Container '{container}' exists in Azure Storage\n"
                f"  2. File '{blob_name}' exists in the container\n"
                f"  3. File is not empty (has data rows)\n"
                f"  4. File has required columns: LOCID, PRDID, GSCEQUIPCAT"
            )
        if "authenticationfailed" in error_lower or "403" in msg or "unauthorized" in error_lower:
            raise BlobLoaderError(
                f"Authentication failed for blob: {container}/{blob_name}\n"
                f"Please verify:\n"
                f"  1. BLOB_CONNECTION_STRING is correct in local.settings.json\n"
                f"  2. Account key hasn't been rotated\n"
                f"  3. Account name is 'planningdatapi'\n"
                f"  4. You have access to the storage account"
            )
        if "connection" in error_lower or "timeout" in error_lower:
            raise BlobLoaderError(
                f"Connection error downloading blob {container}/{blob_name}: {e}\n"
                f"Please verify:\n"
                f"  1. Network connectivity to Azure Storage\n"
                f"  2. Firewall isn't blocking the connection\n"
                f"  3. Azure Storage account is accessible\n"
                f"  4. Try again in a few moments"
            )
        
        raise BlobLoaderError(f"Failed to download blob {container}/{blob_name}: {e}")


# ---------------------------------------------------------------------------
# Load file from bytes (CSV or Excel)
# ---------------------------------------------------------------------------

def load_file_from_bytes(content: bytes, label: str = "file", filename: str = "") -> "pd.DataFrame":
    """Loads CSV or Excel bytes into a pandas DataFrame."""
    try:
        import pandas as pd
    except ImportError:
        raise BlobLoaderError("pandas not installed. Add to requirements.txt.")

    if not content:
        raise BlobLoaderError(f"Empty file content for {label}.")

    fname = filename.lower()
    logger.info(f"Loading {label} ({filename}): {len(content)} bytes")

    try:
        if fname.endswith(".csv"):
            # Try UTF-8 first, fall back to latin-1 for special characters
            try:
                df = pd.read_csv(io.BytesIO(content), dtype=str, encoding='utf-8')
                logger.info(f"Successfully parsed {label} with UTF-8 encoding")
            except UnicodeDecodeError:
                logger.info(f"UTF-8 decode failed for {label}, trying latin-1")
                df = pd.read_csv(io.BytesIO(content), dtype=str, encoding='latin-1')
                logger.info(f"Successfully parsed {label} with latin-1 encoding")
        else:
            # Try openpyxl first (.xlsx), then xlrd (.xls)
            try:
                df = pd.read_excel(io.BytesIO(content), dtype=str, engine='openpyxl')
                logger.info(f"Successfully parsed {label} with openpyxl")
            except Exception as e1:
                logger.info(f"openpyxl failed for {label}: {e1}, trying xlrd")
                df = pd.read_excel(io.BytesIO(content), dtype=str, engine='xlrd')
                logger.info(f"Successfully parsed {label} with xlrd")

        df = df.fillna("")
        if df.empty:
            raise BlobLoaderError(f"File is empty: {label}")
        
        logger.info(f"Loaded {label}: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"Columns in {label}: {list(df.columns)}")
        
        return df
    except BlobLoaderError:
        raise
    except Exception as e:
        logger.error(f"Failed to parse file ({label}): {e}")
        raise BlobLoaderError(f"Failed to parse file ({label}): {e}")


# ---------------------------------------------------------------------------
# Standardize + validate columns
# ---------------------------------------------------------------------------

def standardize_columns(df):
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df.rename(columns=COLUMN_ALIASES)


def validate_required_columns(df, label: str = "file"):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        logger.error(f"Missing required columns in {label}: {sorted(missing)}")
        logger.error(f"Found columns: {sorted(df.columns.tolist())}")
        raise BlobLoaderError(
            f"Missing required columns in {label}: {sorted(missing)}. "
            f"Found: {sorted(df.columns.tolist())}. "
            f"Required: {sorted(REQUIRED_COLUMNS)}"
        )
    logger.info(f"✅ All required columns present in {label}: {sorted(REQUIRED_COLUMNS)}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise BlobLoaderError(f"Missing required environment variable: {name}")
    return val


class BlobLoaderError(Exception):
    """Raised for any Blob Storage ingestion failure."""
    pass

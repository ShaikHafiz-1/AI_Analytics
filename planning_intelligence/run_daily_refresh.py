"""
Daily Refresh Job
Reads CSV/Excel files from Azure Blob Storage,
runs the full analytics pipeline, builds the dashboard response, and saves a snapshot.

Can be triggered:
  1. Manually: python run_daily_refresh.py
  2. Azure Function Timer Trigger (add to function_app.py)
  3. Azure Logic App / Scheduler
"""
import logging
import os
import sys
import json

# Allow running standalone
sys.path.insert(0, os.path.dirname(__file__))

# Load local.settings.json if running standalone (not in Azure Functions)
def _load_local_settings():
    """Load environment variables from local.settings.json for local development."""
    settings_path = os.path.join(os.path.dirname(__file__), "local.settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
                # Load Values section into environment
                for key, value in settings.get("Values", {}).items():
                    if key not in os.environ:
                        os.environ[key] = value
                logging.info(f"Loaded environment variables from {settings_path}")
        except Exception as e:
            logging.warning(f"Could not load local.settings.json: {e}")

# Load settings before importing modules that need them
_load_local_settings()

from normalizer import normalize_rows
from filters import filter_records
from comparator import compare_records
from response_builder import build_response
from snapshot_store import save_snapshot

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def run_daily_refresh(
    location_id: str = None,
    material_group: str = None,
    use_csv: bool = True,
) -> dict:
    """
    Full pipeline — CSV or Blob Storage:
    1. Load current data from CSV files or Azure Blob Storage
    2. Normalize → Filter
    3. Build dashboard response
    4. Save snapshot
    
    Note: Previous data is merged into current, so only one CSV file is loaded.
    
    Args:
        location_id: Optional location filter
        material_group: Optional material group filter
        use_csv: If True, load from CSV files; if False, load from Blob Storage
    
    Returns:
        The dashboard response dict.
    """
    data_source = "CSV files" if use_csv else "Blob Storage"
    logger.info(f"Starting daily planning refresh from {data_source}...")

    # Step 1: Load data from CSV or Blob (only current, previous is merged in)
    try:
        if use_csv:
            from csv_loader import load_current_from_csv
            current_rows = load_current_from_csv()
            logger.info(f"Loaded {len(current_rows)} current rows from CSV.")
        else:
            from blob_loader import load_current_previous_from_blob
            current_rows, _ = load_current_previous_from_blob()
            logger.info(f"Loaded {len(current_rows)} current rows from Blob Storage.")
    except Exception as e:
        logger.error(f"Data load failed: {e}")
        raise

    # Step 2: Normalize
    current_records = normalize_rows(current_rows, is_current=True)

    # Step 3: Filter (if specified)
    current_filtered = filter_records(current_records, location_id, material_group)

    # Step 4: Build dashboard response (convert PlanningRecord objects to ComparedRecord objects)
    # Since we don't have previous data, create ComparedRecord objects from current records
    from models import ComparedRecord
    compared = []
    for rec in current_filtered:
        # rec is a PlanningRecord object
        compared.append(ComparedRecord(
            location_id=rec.location_id,
            material_id=rec.material_id,
            material_group=rec.material_group,
            supplier_current=rec.supplier,
            supplier_previous=None,
            forecast_qty_current=rec.forecast_qty,
            forecast_qty_previous=None,
            roj_current=rec.roj,
            roj_previous=None,
            bod_current=rec.bod,
            bod_previous=None,
            ff_current=rec.ff,
            ff_previous=None,
            roc_region=rec.roc_region,
            dc_site=rec.dc_site,
            metro=rec.metro,
            country=rec.country,
            supplier_date=rec.supplier_date,
            planning_exception=rec.planning_exception,
            roj_reason_code=rec.roj_reason_code,
            automation_reason=rec.automation_reason,
            last_modified_by=rec.last_modified_by,
            last_modified_date=rec.last_modified_date,
            qty_changed=rec.fcst_delta_qty != 0 if rec.fcst_delta_qty else False,
            roj_changed=rec.nbd_delta_days != 0 if rec.nbd_delta_days else False,
            supplier_changed=rec.is_supplier_date_missing,
            design_changed=False,
            qty_delta=rec.fcst_delta_qty,
            change_type='Changed' if (rec.fcst_delta_qty or rec.nbd_delta_days or rec.is_supplier_date_missing) else 'Unchanged',
            risk_level='High' if rec.risk_flag == '1' else 'Normal',
            is_new_demand=rec.is_new_demand,
            is_cancelled=rec.is_cancelled,
            risk_flag=rec.risk_flag,
            fcst_delta_qty=rec.fcst_delta_qty,
            nbd_delta_days=rec.nbd_delta_days,
            is_supplier_date_missing=rec.is_supplier_date_missing,
        ))
    
    result = build_response(compared, [], location_id, material_group, data_mode="cached")

    # Step 5: Save snapshot
    save_snapshot(result)
    logger.info("Daily refresh complete. Snapshot saved.")

    return result


# ---------------------------------------------------------------------------
# Timer trigger (add to function_app.py if needed)
# ---------------------------------------------------------------------------

def get_timer_trigger_function():
    """
    Returns an Azure Function timer trigger handler.
    Register in function_app.py:
        app.schedule(schedule="0 0 6 * * *")(daily_refresh_trigger)
    """
    import azure.functions as func

    def daily_refresh_trigger(timer: func.TimerRequest) -> None:
        logger.info("Timer trigger fired — running daily refresh.")
        try:
            run_daily_refresh()
        except Exception as e:
            logger.error(f"Daily refresh failed: {e}")

    return daily_refresh_trigger


# ---------------------------------------------------------------------------
# Manual run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = run_daily_refresh()
    print(f"Refresh complete. Health: {result.get('planningHealth')}, "
          f"Changed: {result.get('changedRecordCount')}/{result.get('totalRecords')}")

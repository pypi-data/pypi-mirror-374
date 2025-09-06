from datetime import datetime
from ipulse_shared_base_ftredge import RecordsSamplingType

def build_firestore_record_from_sourced_records(record_type: str, record: dict, dt: datetime) -> dict:
    match record_type:
        case "eod_adjc":  # Uses AutoStrEnum string value
            return {
                "date": dt,
                "adjc": record["adj_close"],
            }

        case "eod_ohlcva":  # Uses AutoStrEnum string value
            return {
                "date": dt,
                "open":   record["open"],
                "high":   record["high"],
                "low":    record["low"],
                "close":  record["close"],
                "adj_close":   record["adj_close"],
                "volume": record["volume"],
            }

        case _:
            raise ValueError(f"Unsupported record type: {record_type}")

def build_firestore_record_from_bigquery_data(record_type: str, record: dict, dt: datetime) -> dict:
    """
    Build firestore record from BigQuery fact table data.
    This is similar to build_firestore_record_from_sourced_records but handles BQ field names.
    """
    match record_type:
        case "eod_adjc":
            return {
                "date": dt,
                "adjc": record.get("adj_close"),
            }

        case "eod_ohlcva":
            return {
                "date": dt,
                "open": record.get("open"),
                "high": record.get("high"),
                "low": record.get("low"),
                "close": record.get("close"),
                "adjc": record.get("adj_close"),
                "volume": record.get("volume"),
            }

        case "eod_ohlcv":
            return {
                "date": dt,
                "open": record.get("open"),
                "high": record.get("high"),
                "low": record.get("low"),
                "close": record.get("close"),
                "volume": record.get("volume"),
            }

        case "eod_adjc_volume":
            return {
                "date": dt,
                "adjc": record.get("adj_close"),
                "volume": record.get("volume"),
            }

        case _:
            raise ValueError(f"Unsupported record type: {record_type}")

def get_bigquery_select_fields_for_record_type(record_type: str) -> str:
    """
    Get the appropriate SELECT fields for BigQuery based on record type.
    """
    # Always include date_id for all record types
    base_fields = ["date_id"]
    
    match record_type:
        case "eod_adjc":
            return ", ".join(base_fields + ["adj_close"])
            
        case "eod_ohlcva":
            return ", ".join(base_fields + ["open", "high", "low", "close", "adj_close", "volume"])

        case "eod_ohlcv":
            return ", ".join(base_fields + ["open", "high", "low", "close", "volume"])

        case "eod_adjc_volume":
            return ", ".join(base_fields + ["adj_close", "volume"])
            
        case _:
            # Default to OHLCVA if unsupported type
            return ", ".join(base_fields + ["open", "high", "low", "close", "adj_close", "volume"])
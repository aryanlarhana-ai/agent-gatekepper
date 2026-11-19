import pandas as pd
from .base_agent import BaseAgent


class DataQualityAgent(BaseAgent):
    name = "Data Quality"

    def calculate(self, payload):
        df = payload["data"]
        required = {"order_id", "customer_id", "order_amount", "has_id_proof",
                    "refund_requested", "previous_refunds", "stock_available"}
        missing = sorted(required - set(df.columns))
        cleaned = df.drop_duplicates()
        cleaned["order_amount"] = pd.to_numeric(cleaned["order_amount"], errors="coerce")
        missing_values = int(cleaned.isna().sum().sum())
        return {
            "missing_columns": missing,
            "missing_values": missing_values,
            "duplicate_rows_removed": int(len(df) - len(cleaned)),
            "valid_rows": int(len(cleaned)),
            "clean_data": cleaned,
        }

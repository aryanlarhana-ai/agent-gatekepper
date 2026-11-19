from .base_agent import BaseAgent


class OrderRiskAgent(BaseAgent):
    name = "Order Risk"

    def calculate(self, payload):
        df = payload["data"]
        missing_id = int((~df["has_id_proof"].astype(bool)).sum())
        high_value = int((df["order_amount"] > 5000).sum())
        repeat_refund = int((df["previous_refunds"] >= 3).sum())
        return {
            "missing_id_orders": missing_id,
            "high_value_orders": high_value,
            "repeat_refund_customers": repeat_refund,
        }

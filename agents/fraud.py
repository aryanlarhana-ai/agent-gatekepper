from .base_agent import BaseAgent


class FraudAgent(BaseAgent):
    name = "Fraud"

    def calculate(self, payload):
        df = payload["data"]
        suspected = df[(df["customer_id"] == "CUST_007") |
                       ((df["previous_refunds"] >= 3) & df["refund_requested"].astype(bool))]
        return {
            "suspected_fraud_orders": int(len(suspected)),
            "order_ids": suspected["order_id"].head(20).tolist(),
        }

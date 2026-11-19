from .base_agent import BaseAgent


class ExecutiveAgent(BaseAgent):
    name = "Executive Decision"

    def calculate(self, payload):
        outputs = payload["agent_outputs"]
        risk = outputs["Order Risk"]["key_results"]
        fraud = outputs["Fraud"]["key_results"]
        finance = outputs["Finance"]["key_results"]
        inventory = outputs["Inventory"]["key_results"]

        recommendations = []
        if risk["missing_id_orders"]:
            recommendations.append({"title": "Block missing-ID orders", "priority": "Critical",
                                    "description": f"{risk['missing_id_orders']} orders lack verified ID.",
                                    "expected_impact": "Reduced unauthorized execution"})
        if fraud["suspected_fraud_orders"]:
            recommendations.append({"title": "Review repeat-refund activity", "priority": "High",
                                    "description": f"{fraud['suspected_fraud_orders']} suspected fraud orders.",
                                    "expected_impact": "Lower refund abuse"})
        if inventory["out_of_stock_orders"]:
            recommendations.append({"title": "Stop out-of-stock fulfilment", "priority": "High",
                                    "description": f"{inventory['out_of_stock_orders']} orders reference unavailable stock.",
                                    "expected_impact": "Fewer cancellations"})
        if finance["gross_risk_exposure"]:
            recommendations.append({"title": "Apply step-up approval", "priority": "Medium",
                                    "description": f"Gross exposed value is Rs. {finance['gross_risk_exposure']:,.2f}.",
                                    "expected_impact": "Controlled high-value exposure"})

        return {"recommendations": recommendations,
                "conflicts": ["Finance recommends controlled exposure; operations wants faster fulfilment."]
                             if inventory["out_of_stock_orders"] else [],
                "assumptions": ["Rs. 5000 threshold", "3-refund fraud threshold", "No real payments or refunds"]}

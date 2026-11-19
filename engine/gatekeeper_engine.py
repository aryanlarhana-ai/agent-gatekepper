"""
GATEKEEPER DETERMINISTIC CALCULATION ENGINE
Amazon India Agent Gatekeeper (MBA Edition)
Author: Aryan Thakur (PGD202566017)
Company: Amazon India

ARCHITECTURAL PRINCIPLE:
Python does ALL calculations, mathematical comparisons, and rule evaluations.
Gemini only interprets the results into natural language explanations.
"""

from datetime import datetime
from typing import Dict, Any, List

# The 7 Authorized Agents and their status
AUTHORIZED_AGENTS = {
    "Agent-Kavita": {"status": "ACTIVE", "role": "Order Processing", "revoked_at": None},
    "Agent-Vikram": {"status": "ACTIVE", "role": "Replenishment Automation", "revoked_at": None},
    "Agent-Suresh": {"status": "REVOKED", "role": "Customer Support", "revoked_at": "2026-11-17T14:30:00+05:30"},
    "Agent-Priya": {"status": "ACTIVE", "role": "Refund Processing", "revoked_at": None},
    "Agent-Aarav": {"status": "ACTIVE", "role": "Returns & Logistics", "revoked_at": None},
    "Agent-Rahul": {"status": "ACTIVE", "role": "Inquiry & Tracking", "revoked_at": None},
    "Agent-Ananya": {"status": "ACTIVE", "role": "Dispute Management", "revoked_at": None},
}

# In-memory daily transaction counter for Rule 7 velocity checking
DAILY_AGENT_MONEY_ACTIONS = {}

def get_agents_list() -> List[Dict[str, Any]]:
    return [
        {"name": k, **v} for k, v in AUTHORIZED_AGENTS.items()
    ]

def revoke_agent(agent_name: str) -> Dict[str, Any]:
    if agent_name in AUTHORIZED_AGENTS:
        now_iso = datetime.now().isoformat()
        AUTHORIZED_AGENTS[agent_name]["status"] = "REVOKED"
        AUTHORIZED_AGENTS[agent_name]["revoked_at"] = now_iso
        return {"agent_name": agent_name, "status": "REVOKED", "revoked_at": now_iso}
    raise ValueError(f"Agent '{agent_name}' not found.")

def reactivate_agent(agent_name: str) -> Dict[str, Any]:
    if agent_name in AUTHORIZED_AGENTS:
        AUTHORIZED_AGENTS[agent_name]["status"] = "ACTIVE"
        AUTHORIZED_AGENTS[agent_name]["revoked_at"] = None
        return {"agent_name": agent_name, "status": "ACTIVE"}
    raise ValueError(f"Agent '{agent_name}' not found.")

def evaluate_request(
    agent_name: str,
    customer_id: str,
    action: str,
    order_amount: float,
    has_id_proof: bool = True,
    previous_refunds: int = 0,
    stock_available: bool = True,
    order_id: str = "ADHOC"
) -> Dict[str, Any]:
    """
    Core deterministic policy calculation function.
    Every rule outcome is calculated mathematically and logically in Python.
    """
    num_amount = float(order_amount) if order_amount is not None else 0.0
    action_clean = action.strip().lower()
    money_actions = ["place order", "return", "refund"]
    
    # -------------------------------------------------------------
    # 1. AGENT IDENTITY CHECK (Rules 1 & 2)
    # -------------------------------------------------------------
    matched_agent = AUTHORIZED_AGENTS.get(agent_name)
    
    if not matched_agent:
        return {
            "decision": "BLOCK",
            "rule_code": "RULE_2",
            "rule_name": "Unknown Agent = BLOCK",
            "reason": f"Agent '{agent_name}' is not registered in Amazon India Gatekeeper. Access denied.",
            "calculations": {
                "agent_verified": False,
                "agent_revoked": False,
                "order_amount": num_amount,
                "has_id_proof": has_id_proof
            },
            "requires_customer_action": False,
            "timestamp": datetime.now().isoformat()
        }
        
    if matched_agent["status"] == "REVOKED":
        return {
            "decision": "BLOCK",
            "rule_code": "RULE_1",
            "rule_name": "Revoked Agent = BLOCK",
            "reason": f"Agent '{agent_name}' was REVOKED on {matched_agent.get('revoked_at')}. All actions are strictly blocked.",
            "calculations": {
                "agent_verified": True,
                "agent_revoked": True,
                "revoked_at": matched_agent.get("revoked_at"),
                "order_amount": num_amount,
                "has_id_proof": has_id_proof
            },
            "requires_customer_action": False,
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------------------
    # 2. INVENTORY & STOCK CHECK
    # -------------------------------------------------------------
    if not stock_available and action_clean == "place order":
        return {
            "decision": "BLOCK",
            "rule_code": "RULE_STOCK_OUT",
            "rule_name": "Stock Unavailable = BLOCK",
            "reason": "Requested product is out of stock in Amazon India fulfillment centers.",
            "calculations": {
                "stock_available": False,
                "order_amount": num_amount
            },
            "requires_customer_action": False,
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------------------
    # 3. ID PROOF REQUIREMENT (CRITICAL MBA RULE)
    # -------------------------------------------------------------
    if not has_id_proof:
        return {
            "decision": "BLOCK",
            "rule_code": "RULE_ID_MISSING",
            "rule_name": "ID Proof Missing = BLOCK",
            "reason": f"Mandatory government KYC / ID proof is missing for customer '{customer_id}'. High-risk transaction blocked.",
            "calculations": {
                "has_id_proof": False,
                "order_amount": num_amount,
                "threshold": 5000.0,
                "id_required": True
            },
            "requires_customer_action": False,
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------------------
    # 4. FRAUD DETECTION (CUST_007 or Repeat Refunds)
    # -------------------------------------------------------------
    is_repeat_refund_offender = (customer_id == "CUST_007") or (previous_refunds >= 3 and action_clean in ["return", "refund"])
    if is_repeat_refund_offender:
        return {
            "decision": "BLOCK",
            "rule_code": "RULE_FRAUD_REPEAT",
            "rule_name": "Repeat Refund Abuse = BLOCK (FRAUD)",
            "reason": f"Customer '{customer_id}' has {previous_refunds} previous refund claims. Automated refund blocked due to fraud risk scoring.",
            "calculations": {
                "customer_id": customer_id,
                "previous_refunds": previous_refunds,
                "fraud_threshold": 3,
                "is_fraud_suspect": True
            },
            "requires_customer_action": False,
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------------------
    # 5. READ-ONLY INQUIRY (Rule 3)
    # -------------------------------------------------------------
    if action_clean == "view order":
        return {
            "decision": "ALLOW",
            "rule_code": "RULE_3",
            "rule_name": "View Order = ALLOW",
            "reason": f"Non-financial inquiry: Viewing order details permitted for verified agent '{agent_name}'.",
            "calculations": {
                "is_financial": False,
                "order_amount": 0.0
            },
            "requires_customer_action": False,
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------------------
    # 6. DAILY VELOCITY LIMIT (Rule 7)
    # -------------------------------------------------------------
    if action_clean in money_actions:
        today_key = f"{agent_name}_{datetime.now().strftime('%Y-%m-%d')}"
        daily_count = DAILY_AGENT_MONEY_ACTIONS.get(today_key, 0)
        
        if daily_count >= 3:
            return {
                "decision": "ASK CUSTOMER",
                "rule_code": "RULE_7",
                "rule_name": "More than 3 Money Actions/Day = ASK CUSTOMER",
                "reason": f"Agent '{agent_name}' has already executed {daily_count} financial actions today. Step-up approval required.",
                "calculations": {
                    "daily_count": daily_count,
                    "velocity_limit": 3,
                    "limit_exceeded": True,
                    "order_amount": num_amount
                },
                "requires_customer_action": True,
                "timestamp": datetime.now().isoformat()
            }

    # -------------------------------------------------------------
    # 7. FINANCIAL REVERSALS: RETURN / REFUND (Rule 6)
    # -------------------------------------------------------------
    if action_clean in ["return", "refund"]:
        return {
            "decision": "ASK CUSTOMER",
            "rule_code": "RULE_6",
            "rule_name": "Return or Refund = ASK CUSTOMER",
            "reason": f"Financial reversal ({action_clean.upper()} of ₹{num_amount:,.2f}) requires explicit customer consent and signature verification.",
            "calculations": {
                "action": action_clean,
                "order_amount": num_amount,
                "reversal_policy": "MANDATORY_CONFIRMATION"
            },
            "requires_customer_action": True,
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------------------
    # 8. ORDER AMOUNT THRESHOLDS (Rules 4 & 5)
    # -------------------------------------------------------------
    if action_clean == "place order":
        if num_amount > 5000.0:
            return {
                "decision": "ASK CUSTOMER",
                "rule_code": "RULE_5",
                "rule_name": "Place Order > Rs 5000 = ASK CUSTOMER",
                "reason": f"Order amount of ₹{num_amount:,.2f} exceeds the automated ₹5,000 ceiling. Customer OTP / authorization required.",
                "calculations": {
                    "order_amount": num_amount,
                    "threshold": 5000.0,
                    "amount_exceeds_threshold": True,
                    "difference": num_amount - 5000.0
                },
                "requires_customer_action": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Rule 4: <= 5000 with ID proof
            # Record velocity
            today_key = f"{agent_name}_{datetime.now().strftime('%Y-%m-%d')}"
            DAILY_AGENT_MONEY_ACTIONS[today_key] = DAILY_AGENT_MONEY_ACTIONS.get(today_key, 0) + 1
            
            return {
                "decision": "ALLOW",
                "rule_code": "RULE_4",
                "rule_name": "Place Order <= Rs 5000 = ALLOW",
                "reason": f"Order amount of ₹{num_amount:,.2f} is within the allowable limit of ₹5,000 and ID proof is verified.",
                "calculations": {
                    "order_amount": num_amount,
                    "threshold": 5000.0,
                    "amount_exceeds_threshold": False,
                    "has_id_proof": True
                },
                "requires_customer_action": False,
                "timestamp": datetime.now().isoformat()
            }

    # Fallback safe decision
    return {
        "decision": "ASK CUSTOMER",
        "rule_code": "RULE_FALLBACK",
        "rule_name": "Unspecified Action = ASK CUSTOMER",
        "reason": f"Unrecognized action '{action}'. Escalated to customer review.",
        "calculations": {"order_amount": num_amount},
        "requires_customer_action": True,
        "timestamp": datetime.now().isoformat()
    }

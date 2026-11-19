"""
GEMINI INTERPRETER MODULE
Amazon India Agent Gatekeeper (MBA Edition)
Author: Aryan Thakur (PGD202566017)
Company: Amazon India

ARCHITECTURAL PRINCIPLE:
Python does all math, boolean evaluation, and rule determination.
Gemini's role is STRICTLY interpretive:
1. Translating calculated policy decisions into human-readable customer notices.
2. Generating compliance summaries for the Approval Centre.
3. Formulating risk rationales for MBA auditing.
Gemini NEVER calculates amounts or changes rule outcomes.
"""

import os
import json
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def interpret_decision(evaluation_result: Dict[str, Any], order_context: Dict[str, Any] = None) -> Dict[str, str]:
    """
    Interprets the pre-calculated decision from gatekeeper_engine.
    Does zero arithmetic.
    """
    decision = evaluation_result.get("decision", "ASK CUSTOMER")
    rule_code = evaluation_result.get("rule_code", "UNKNOWN")
    rule_name = evaluation_result.get("rule_name", "")
    reason = evaluation_result.get("reason", "")
    calcs = evaluation_result.get("calculations", {})
    
    amount = calcs.get("order_amount", 0.0)
    has_id = calcs.get("has_id_proof", True)
    
    # Check if Gemini API is available
    api_key = os.environ.get("GEMINI_API_KEY")
    ai_generated_note = None
    
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""
You are the Compliance AI for Amazon India's Agent Gatekeeper.
The deterministic Python engine has ALREADY calculated the decision.
DO NOT recalculate or change the decision. ONLY explain it clearly to an MBA auditor.

Decision: {decision}
Rule Applied: {rule_code} - {rule_name}
Reason: {reason}
Order Amount: Rs. {amount}
ID Proof Attached: {has_id}

Provide:
1. An executive summary sentence.
2. A customer-facing notification message.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            ai_generated_note = response.text.strip()
        except Exception as e:
            ai_generated_note = f"[Gemini Interpretation Engine: Offline Mode] {reason}"
            
    # Deterministic natural language templates (Interpretation only)
    if not ai_generated_note:
        if decision == "BLOCK":
            executive_summary = (
                f"Perimeter Security Rejection: Transaction flagged under {rule_code} ({rule_name}). "
                f"System prevented unauthorized execution. Risk mitigated: "
                f"{'Absence of verified customer KYC ID proof.' if not has_id else reason}"
            )
            customer_notice = (
                f"Dear Customer, your recent transaction of ₹{amount:,.2f} could not be completed automatically. "
                "Reason: Security and identity compliance verification required. Please contact Amazon India Support."
            )
        elif decision == "ASK CUSTOMER":
            executive_summary = (
                f"High-Value / Velocity Policy Step-Up: Request triggered {rule_code} ({rule_name}). "
                f"Autonomous execution paused pending customer OTP / 2-Factor Authentication."
            )
            customer_notice = (
                f"Amazon Alert: An agent has initiated a request for ₹{amount:,.2f}. "
                "To approve this purchase, please review the notification in your Amazon Shopping app or enter the OTP."
            )
        else: # APPROVE / ALLOW
            executive_summary = (
                f"Autonomous Policy Match: Order approved automatically under {rule_code} ({rule_name}). "
                f"Amount ₹{amount:,.2f} complies with low-value threshold (<= ₹5,000) and verified identity standards."
            )
            customer_notice = (
                f"Your order of ₹{amount:,.2f} has been placed successfully by your authorized Amazon Assistant."
            )
            
        ai_generated_note = f"{executive_summary}\n\n[Customer SMS Draft]: {customer_notice}"
        
    return {
        "interpretation_type": "NATURAL_LANGUAGE_AUDIT_EXPLANATION",
        "gemini_summary": ai_generated_note,
        "policy_rule_referenced": f"{rule_code}: {rule_name}",
        "engine_decision": decision
    }

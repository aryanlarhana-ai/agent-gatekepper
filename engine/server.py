"""
FASTAPI SERVER FOR AGENT GATEKEEPER (MBA EDITION)
Amazon India Agent Gatekeeper
Author: Aryan Thakur (PGD202566017)
Company: Amazon India
"""

import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add engine directory to path
sys.path.insert(0, os.path.dirname(__file__))

from db import (
    init_db, get_all_orders, get_order_by_id, 
    update_approval_status, reset_all_data, SIMULATION_MODE
)
from gatekeeper_engine import (
    get_agents_list, evaluate_request, revoke_agent, reactivate_agent
)
from gemini_interpreter import interpret_decision

app = FastAPI(
    title="Amazon India Agent Gatekeeper API",
    description="MBA Policy Engine & Approval Centre for Autonomous Agent Governance",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("[SERVER] Agent Gatekeeper backend started. Mode: SYNTHETIC SIMULATION.")

# Request Schemas
class EvaluateOrderRequest(BaseModel):
    agent_name: str
    customer_id: str
    action: str = "place order"
    order_amount: float
    has_id_proof: bool = True
    previous_refunds: int = 0
    stock_available: bool = True
    order_id: Optional[str] = "ADHOC"

class ApprovalActionRequest(BaseModel):
    order_id: str
    action: str  # 'APPROVE', 'REJECT', 'RESET'
    reviewer: Optional[str] = "Aryan Thakur"
    notes: Optional[str] = ""

class AgentRevokeRequest(BaseModel):
    agent_name: str

# -------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "system": "Agent Gatekeeper for Amazon India",
        "student": "Aryan Thakur",
        "enrolment": "PGD202566017",
        "simulation_mode": SIMULATION_MODE,
        "disclaimer": "SYNTHETIC DEMONSTRATION DATA ONLY - NO REAL FUNDS ACCESSED"
    }

@app.get("/api/orders")
def fetch_orders(limit: int = 200):
    """Returns the synthetic orders from the database."""
    orders = get_all_orders(limit)
    return {"total": len(orders), "orders": orders}

@app.get("/api/orders/{order_id}")
def fetch_order(order_id: str):
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/agents")
def fetch_agents():
    """Returns the 7 agents and their current active/revoked status."""
    return {"agents": get_agents_list()}

@app.post("/api/agents/revoke")
def api_revoke_agent(req: AgentRevokeRequest):
    try:
        res = revoke_agent(req.agent_name)
        return {"status": "SUCCESS", "agent": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/agents/reactivate")
def api_reactivate_agent(req: AgentRevokeRequest):
    try:
        res = reactivate_agent(req.agent_name)
        return {"status": "SUCCESS", "agent": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/evaluate")
def api_evaluate(req: EvaluateOrderRequest):
    """
    Evaluates order using pure Python engine calculations.
    Then enriches with Gemini interpretation.
    """
    # 1. Pure Python calculation
    calculation_result = evaluate_request(
        agent_name=req.agent_name,
        customer_id=req.customer_id,
        action=req.action,
        order_amount=req.order_amount,
        has_id_proof=req.has_id_proof,
        previous_refunds=req.previous_refunds,
        stock_available=req.stock_available,
        order_id=req.order_id
    )
    
    # 2. Gemini interpretation (natural language only, no calculation)
    interpretation = interpret_decision(calculation_result)
    
    return {
        "evaluation": calculation_result,
        "gemini_interpretation": interpretation,
        "safety_guarantee": "MOCK SIMULATION - NO REAL TRANSACTION EXECUTED"
    }

@app.get("/api/approval/queue")
def fetch_approval_queue():
    """Fetches items in the Approval Centre."""
    orders = get_all_orders(limit=200)
    pending = [o for o in orders if o["approval_status"] == "PENDING_REVIEW"]
    approved = [o for o in orders if "APPROVED" in o["approval_status"]]
    rejected = [o for o in orders if "REJECTED" in o["approval_status"]]
    blocked = [o for o in orders if o["approval_status"] == "BLOCKED"]
    
    return {
        "total": len(orders),
        "pending_count": len(pending),
        "approved_count": len(approved),
        "rejected_count": len(rejected),
        "blocked_count": len(blocked),
        "orders": orders
    }

@app.post("/api/approval/action")
def api_approval_action(req: ApprovalActionRequest):
    """
    Approve, Reject, or Reset an order in SQLite.
    App must NEVER do real refund/payment.
    """
    try:
        result = update_approval_status(
            order_id=req.order_id,
            action=req.action.upper(),
            reviewer=req.reviewer or "Aryan Thakur",
            notes=req.notes or ""
        )
        return {"status": "SUCCESS", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/approval/reset-all")
def api_reset_all():
    """Resets all 200 orders back to original synthetic state."""
    res = reset_all_data()
    return res

@app.get("/api/stats")
def api_stats():
    orders = get_all_orders(limit=200)
    agents = get_agents_list()
    
    return {
        "total_orders": len(orders),
        "active_agents": len([a for a in agents if a["status"] == "ACTIVE"]),
        "revoked_agents": len([a for a in agents if a["status"] == "REVOKED"]),
        "pending_reviews": len([o for o in orders if o["approval_status"] == "PENDING_REVIEW"]),
        "auto_approved": len([o for o in orders if o["approval_status"] == "AUTO_APPROVED"]),
        "blocked_orders": len([o for o in orders if "BLOCK" in o["policy_decision"]]),
        "ask_customer_orders": len([o for o in orders if o["policy_decision"] == "ASK CUSTOMER"])
    }

# Serve root index.html
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
INDEX_FILE = os.path.join(ROOT_DIR, "index.html")

@app.get("/")
def serve_root():
    if os.path.exists(INDEX_FILE):
        return FileResponse(INDEX_FILE)
    return {"message": "Agent Gatekeeper API running. index.html not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)

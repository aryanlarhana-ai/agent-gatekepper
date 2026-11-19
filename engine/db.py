"""
APPROVAL CENTRE DATABASE & MOCK SAFETY ENGINE
Amazon India Agent Gatekeeper (MBA Edition)
Author: Aryan Thakur (PGD202566017)
Company: Amazon India

HARD SAFETY PROTOCOL:
This system is strictly for academic and demonstration purposes.
It contains NO payment gateway credentials and NEVER calls live bank/refund APIs.
All state transitions are mock updates recorded in local SQLite.
"""

import os
import sqlite3
import csv
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "gatekeeper_approval.db")
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic_amazon_orders.csv")

# HARD SAFETY INVARIANT
SIMULATION_MODE = True
NEVER_DO_REAL_PAYMENT_OR_REFUND = True

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS approval_queue (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        product TEXT NOT NULL,
        order_amount REAL NOT NULL,
        has_id_proof INTEGER NOT NULL,
        refund_requested INTEGER NOT NULL,
        previous_refunds INTEGER NOT NULL,
        stock_available INTEGER NOT NULL,
        policy_decision TEXT NOT NULL,
        approval_status TEXT NOT NULL,
        reviewer TEXT,
        reviewer_notes TEXT,
        reviewed_at TEXT,
        created_at TEXT NOT NULL,
        is_simulation INTEGER DEFAULT 1
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        order_id TEXT,
        customer_id TEXT,
        agent_id TEXT,
        action TEXT,
        order_amount REAL,
        policy_decision TEXT,
        rule_code TEXT,
        reason TEXT,
        gemini_interpretation TEXT,
        is_simulation INTEGER DEFAULT 1
    );
    """)
    
    conn.commit()
    
    # Check if approval_queue is empty, if so populate from CSV
    cursor.execute("SELECT COUNT(*) FROM approval_queue")
    count = cursor.fetchone()[0]
    
    if count == 0 and os.path.exists(CSV_PATH):
        seed_from_csv(conn)
        
    conn.close()

def seed_from_csv(conn=None):
    close_at_end = False
    if conn is None:
        conn = get_connection()
        close_at_end = True
        
    cursor = conn.cursor()
    cursor.execute("DELETE FROM approval_queue")
    
    now_iso = datetime.now().isoformat()
    
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = [r for r in reader if r and not r[0].startswith("#")]
        
    header = rows[0]
    data_rows = rows[1:]
    
    for r in data_rows:
        order_id = r[0]
        customer_id = r[1]
        product = r[2]
        order_amount = float(r[3])
        has_id_proof = 1 if r[4].strip().lower() == "true" else 0
        refund_requested = 1 if r[5].strip().lower() == "true" else 0
        previous_refunds = int(r[6])
        stock_available = 1 if r[7].strip().lower() == "true" else 0
        expected_decision = r[8].strip()
        
        # Initial approval status
        if "BLOCK" in expected_decision:
            initial_status = "BLOCKED"
        elif expected_decision == "ASK CUSTOMER":
            initial_status = "PENDING_REVIEW"
        else:
            initial_status = "AUTO_APPROVED"
            
        cursor.execute("""
        INSERT INTO approval_queue (
            order_id, customer_id, product, order_amount, has_id_proof,
            refund_requested, previous_refunds, stock_available,
            policy_decision, approval_status, reviewer, reviewer_notes,
            reviewed_at, created_at, is_simulation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            order_id, customer_id, product, order_amount, has_id_proof,
            refund_requested, previous_refunds, stock_available,
            expected_decision, initial_status, None, None, None, now_iso
        ))
        
    conn.commit()
    if close_at_end:
        conn.close()
    print("[DB] Initialized approval queue with synthetic orders.")

def get_all_orders(limit=200):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approval_queue ORDER BY order_id ASC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_order_by_id(order_id):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approval_queue WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_approval_status(order_id, action, reviewer="Aryan Thakur", notes=""):
    """
    Approve, Reject, or Reset an order in the Approval Centre.
    SAFETY: Does NOT trigger any bank or refund transaction.
    """
    assert NEVER_DO_REAL_PAYMENT_OR_REFUND is True, "Safety Violation: Real payments strictly disallowed."
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    now_iso = datetime.now().isoformat()
    
    if action == "APPROVE":
        new_status = "APPROVED_BY_ADMIN"
        log_reason = f"Approved in Approval Centre by {reviewer}. (Simulated Action - No real funds moved)"
    elif action == "REJECT":
        new_status = "REJECTED_BY_ADMIN"
        log_reason = f"Rejected in Approval Centre by {reviewer}."
    elif action == "RESET":
        # Check original policy decision
        cursor.execute("SELECT policy_decision FROM approval_queue WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        decision = row["policy_decision"] if row else "ASK CUSTOMER"
        new_status = "PENDING_REVIEW" if decision == "ASK CUSTOMER" else ("BLOCKED" if "BLOCK" in decision else "AUTO_APPROVED")
        reviewer = None
        notes = "Reset to original synthetic state."
        now_iso = None
        log_reason = "Order status reset."
    else:
        conn.close()
        raise ValueError(f"Unknown approval action: {action}")
        
    cursor.execute("""
    UPDATE approval_queue 
    SET approval_status = ?, reviewer = ?, reviewer_notes = ?, reviewed_at = ?
    WHERE order_id = ?
    """, (new_status, reviewer, notes, now_iso, order_id))
    
    # Log to audit table
    cursor.execute("""
    INSERT INTO audit_logs (
        timestamp, order_id, action, policy_decision, rule_code, reason, is_simulation
    ) VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (
        datetime.now().isoformat(), order_id, f"APPROVAL_CENTRE_{action}",
        new_status, "APPROVAL_ACTION", log_reason
    ))
    
    conn.commit()
    conn.close()
    
    return {"order_id": order_id, "new_status": new_status, "updated_at": now_iso}

def reset_all_data():
    """Resets entire SQLite database back to the synthetic CSV baseline."""
    seed_from_csv()
    return {"status": "SUCCESS", "message": "All orders reset to synthetic baseline."}

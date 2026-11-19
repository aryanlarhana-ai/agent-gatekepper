"""
SYNTHETIC DEMONSTRATION DATA GENERATOR
Amazon India Agent Gatekeeper (MBA Edition)
Author: Aryan Thakur (PGD202566017)
Company: Amazon India

Generates 200 synthetic Amazon orders with injected policy edge cases:
- ORD 1-20: ID missing + high amount = BLOCK
- ORD 21-40: ID present + amount > 5000 = ASK CUSTOMER
- ORD 41-60: CUST_007 repeat refunds = Fraud
- ORD 61-200: Realistic operational distribution
"""

import csv
import os
import random

random.seed(20261119)

PRODUCTS = [
    "Echo Dot (5th Gen)",
    "Fire TV Stick 4K",
    "Kindle Paperwhite",
    "boAt Rockerz 450",
    "OnePlus Nord CE 3 Lite",
    "Samsung Galaxy M34",
    "Prestige Iris Mixer Grinder",
    "Puma Men Running Shoes",
    "Noise ColorFit Pulse 2",
    "Milton Thermosteel Flask",
    "Sony WH-1000XM5",
    "Apple iPad 10th Gen",
    "HP 15s Ryzen 5",
    "Philips Air Fryer",
    "Wildcraft Backpack"
]

def generate_orders():
    orders = []
    
    # -------------------------------------------------------------
    # 1. ORD 1-20: ID missing (False) + high amount (>5000) = BLOCK
    # -------------------------------------------------------------
    for i in range(1, 21):
        order_id = f"ORD_{i:03d}"
        cust_id = f"CUST_{(i % 15) + 1:03d}"
        product = PRODUCTS[(i - 1) % len(PRODUCTS)]
        # High amount between 6000 and 22000
        order_amount = round(random.uniform(6000, 22000), 2)
        has_id_proof = False
        refund_requested = False
        previous_refunds = random.randint(0, 1)
        stock_available = True
        
        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "product": product,
            "order_amount": order_amount,
            "has_id_proof": has_id_proof,
            "refund_requested": refund_requested,
            "previous_refunds": previous_refunds,
            "stock_available": stock_available,
            "expected_decision": "BLOCK",
            "injection_note": "ORD 1-20: ID missing + high amount = BLOCK"
        })
        
    # -------------------------------------------------------------
    # 2. ORD 21-40: ID present (True) + amount > 5000 = ASK CUSTOMER
    # -------------------------------------------------------------
    for i in range(21, 41):
        order_id = f"ORD_{i:03d}"
        cust_id = f"CUST_{(i % 20) + 1:03d}"
        product = PRODUCTS[(i - 1) % len(PRODUCTS)]
        # Amount strictly greater than 5000
        order_amount = round(random.uniform(5200, 28000), 2)
        has_id_proof = True
        refund_requested = False
        previous_refunds = random.randint(0, 1)
        stock_available = True
        
        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "product": product,
            "order_amount": order_amount,
            "has_id_proof": has_id_proof,
            "refund_requested": refund_requested,
            "previous_refunds": previous_refunds,
            "stock_available": stock_available,
            "expected_decision": "ASK CUSTOMER",
            "injection_note": "ORD 21-40: ID present + >5000 = ASK CUSTOMER"
        })
        
    # -------------------------------------------------------------
    # 3. ORD 41-60: CUST_007 repeat refunds = Fraud
    # -------------------------------------------------------------
    for i in range(41, 61):
        order_id = f"ORD_{i:03d}"
        cust_id = "CUST_007"  # Repeat offender
        product = PRODUCTS[(i - 1) % len(PRODUCTS)]
        order_amount = round(random.uniform(1200, 7500), 2)
        has_id_proof = True
        refund_requested = True
        # Repeat refund count >= 3
        previous_refunds = random.randint(4, 9)
        stock_available = True
        
        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "product": product,
            "order_amount": order_amount,
            "has_id_proof": has_id_proof,
            "refund_requested": refund_requested,
            "previous_refunds": previous_refunds,
            "stock_available": stock_available,
            "expected_decision": "BLOCK (FRAUD)",
            "injection_note": "ORD 41-60: CUST_007 repeat refunds = Fraud"
        })
        
    # -------------------------------------------------------------
    # 4. ORD 61-200: Realistic operational distribution
    # -------------------------------------------------------------
    for i in range(61, 201):
        order_id = f"ORD_{i:03d}"
        cust_id = f"CUST_{(i % 45) + 1:03d}"
        product = PRODUCTS[(i - 1) % len(PRODUCTS)]
        
        # Sub-distribution: mostly normal approve <= 5000 with ID
        if i <= 150:
            order_amount = round(random.uniform(299, 4999), 2)
            has_id_proof = True
            refund_requested = False
            previous_refunds = random.choice([0, 0, 1])
            stock_available = True
            expected = "APPROVE"
            note = "Standard order <= 5000 with valid ID"
        elif i <= 170:
            # Low amount refunds
            order_amount = round(random.uniform(499, 3500), 2)
            has_id_proof = True
            refund_requested = True
            previous_refunds = random.choice([0, 1])
            stock_available = True
            expected = "ASK CUSTOMER"
            note = "Standard refund request (Rule 6)"
        elif i <= 185:
            # High amount orders with ID
            order_amount = round(random.uniform(5500, 15000), 2)
            has_id_proof = True
            refund_requested = False
            previous_refunds = 0
            stock_available = True
            expected = "ASK CUSTOMER"
            note = "High amount > 5000 (Rule 5)"
        else:
            # Occasional missing ID or out of stock edge cases
            order_amount = round(random.uniform(500, 4500), 2)
            has_id_proof = (i % 2 == 0)
            refund_requested = False
            previous_refunds = 0
            stock_available = (i % 3 != 0)
            expected = "BLOCK" if not has_id_proof else ("BLOCK (OUT OF STOCK)" if not stock_available else "APPROVE")
            note = "Edge case distribution"
            
        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "product": product,
            "order_amount": order_amount,
            "has_id_proof": has_id_proof,
            "refund_requested": refund_requested,
            "previous_refunds": previous_refunds,
            "stock_available": stock_available,
            "expected_decision": expected,
            "injection_note": note
        })
        
    return orders

def save_csv(orders, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fieldnames = [
        "order_id",
        "customer_id",
        "product",
        "order_amount",
        "has_id_proof",
        "refund_requested",
        "previous_refunds",
        "stock_available",
        "expected_decision",
        "injection_note"
    ]
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        # Write Top Synthetic Demonstration Data Banner Label
        f.write("# SYNTHETIC DEMONSTRATION DATA - FOR MBA ACADEMIC EVALUATION ONLY\n")
        f.write("# Generated for: Aryan Thakur (PGD202566017) | Company: Amazon India\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(orders)
        
    print(f"[SUCCESS] Successfully generated {len(orders)} synthetic orders at: {output_path}")

if __name__ == "__main__":
    target_path = os.path.join(os.path.dirname(__file__), "synthetic_amazon_orders.csv")
    generated = generate_orders()
    save_csv(generated, target_path)

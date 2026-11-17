# PROMPTS & AI INTERACTION LOG

**Project Title:** Agent Gatekeeper for Amazon India  
**Student / Developer:** Aryan Thakur  
**Enrolment Number:** PGD202566017  
**Organization / Domain:** Amazon India  
**Date:** November 2026  

---

## 1. Overview & Prompt Engineering Methodology

This document details the complete prompt engineering lifecycle employed to design, develop, test, and document the **Agent Gatekeeper for Amazon India** single-page web application. 

The prompt engineering approach followed the **C-R-E-A-T-E** framework:
- **Context:** Establishing the operational domain (Amazon India autonomous agent governance).
- **Role:** Directing the model as an enterprise software architect and security engineer.
- **Explicit Constraints:** Mandating zero external dependencies, strict client-side `localStorage` persistence, Amazon India brand identity (`#FF9900`, `#131921`, `#FFD814`), and specific rule definitions.
- **Actionable Steps:** Step-by-step modular specification (registration, revocation with timestamp, evaluation form, decision banner, audit log).
- **Testability:** Requiring 1-click test scenarios for all 7 rules.
- **Evaluation:** Strict verification of edge cases (e.g., Rule 7 daily velocity limits vs. Rule 4 amount limits).

---

## 2. Core Prompt Trajectory

### Phase 1: Initial Specification & Core System Requirements

#### Prompt 1.1: Master Requirement Prompt
```text
Create a single page web app called Agent Gatekeeper for Amazon India.
Show my name Aryan Thakur and enrolment PGD202566017 on top.
It should have:
- Register Agent form
- Revoke Agent button with date and time saved
- Request form: customer name, agent name, action dropdown - view order, place order, return, refund, amount
- Show decision ALLOW, ASK CUSTOMER or BLOCK with rule number
- Audit log table with date-time, request, decision, rule
Use these 7 rules:
- Rule 1 Revoked agent = BLOCK
- Rule 2 Unknown agent = BLOCK
- Rule 3 view order = ALLOW
- Rule 4 place order Rs 5000 or less = ALLOW
- Rule 5 place order more than Rs 5000 = ASK CUSTOMER
- Rule 6 return or refund = ASK CUSTOMER
- Rule 7 More than 3 money actions in a day = ASK CUSTOMER
Make it simple, in orange and white Amazon style. Save everything in localStorage so audit log does not disappear on refresh.
```

**Intent & Rationale:**  
Establishes the foundational scope, UI aesthetics, governance rules, and persistence constraints.

---

### Phase 2: Architectural & Policy Engine Design Prompts

#### Prompt 2.1: Policy Precedence & Rule Engine Formulation
```text
Design the decision pipeline for the 7 gatekeeper rules ensuring mathematical and logical rigor:
1. Revocation check (Rule 1) must take absolute precedence over any registered action.
2. Unregistered identity check (Rule 2) must execute before action classification.
3. Non-financial inquiry action 'view order' (Rule 3) must immediately resolve to ALLOW without requiring transaction amount.
4. For financial actions ('place order', 'return', 'refund'):
   - Define a velocity counter that computes how many money actions the specific agent has logged on the current calendar date (today).
   - If previous count >= 3, the current transaction is the 4th+ action of the day, triggering Rule 7 (ASK CUSTOMER).
   - If velocity limit (< 3) is intact:
     * 'place order' <= Rs 5000 -> Rule 4 (ALLOW)
     * 'place order' > Rs 5000 -> Rule 5 (ASK CUSTOMER)
     * 'return' or 'refund' -> Rule 6 (ASK CUSTOMER)
Document this hierarchy clearly in code comments and UI tooltips.
```

**Outcome:**  
Eliminates ambiguity between Rule 4 and Rule 7. For example, if an agent places four orders of ₹1,000 on the same day, orders 1–3 are `ALLOW` (Rule 4), while order 4 is escalated to `ASK CUSTOMER` (Rule 7).

---

### Phase 3: UI/UX & Amazon India Brand Identity Prompts

#### Prompt 3.1: Visual Hierarchy and Design System Prompt
```text
Implement an Amazon India (Amazon.in) design system in clean, responsive CSS:
- Primary Navbar: Amazon Dark Slate (#131921) with Amazon logo and orange '.in' superscript.
- Sub-navbar: Amazon Navy (#232F3E) with live telemetry metric chips.
- Accent Colors: Amazon Smile Orange (#FF9900), Action Orange (#E47911), Primary Button Yellow (#FFD814), Hover (#F7CA00).
- Student Header: Prominently display 'Aryan Thakur' and 'PGD202566017' with an administrative badge.
- Cards: Crisp white containers (#FFFFFF) with subtle border (#D5D9D9) and soft box shadows.
- Badges:
  * ALLOW: Forest Green (#067D62) with soft green background (#E7F4EE)
  * ASK CUSTOMER: Warm Amber (#C45500) with soft amber background (#FFF4EB)
  * BLOCK: Crimson Red (#BA0933) with soft red background (#FDF0F0)
- Currency: Format all monetary amounts in Indian Rupees (₹ / INR).
```

**Outcome:**  
Provides an authentic corporate dashboard aesthetic consistent with Amazon India's internal developer tooling.

---

### Phase 4: State Management & Persistence Prompts

#### Prompt 4.1: Robust LocalStorage & Data Schema Prompt
```text
Design the client-side persistence schema using localStorage:
1. Keys:
   - 'amazon_gatekeeper_agents_v2': Array of Agent objects { id, name, status: 'ACTIVE'|'REVOKED', registeredAt, revokedAt }
   - 'amazon_gatekeeper_audit_log_v2': Array of AuditRecord objects { id, timestamp, customerName, agentName, action, amount, decision, ruleNumber, ruleTitle, reason }
2. Requirement:
   - On initial launch or empty state, auto-seed realistic sample data (2 active agents, 1 revoked agent, 2 audit logs) so the instructor can test immediately without setup.
   - Provide a 'Reset Everything' button and a 'Clear Audit Log' button with confirmation dialogs.
   - Provide an 'Export CSV' button to export the audit trail.
```

**Outcome:**  
Guarantees zero data loss upon page refresh, while providing clear reset and export workflows.

---

### Phase 5: Test Automation & Demonstration Presets

#### Prompt 5.1: 1-Click Verification Presets
```text
Add a quick-test toolbar with 7 preset buttons corresponding to Rules 1 through 7:
- Button 'Rule 1 (Revoked)': Selects a revoked agent, action 'place order', amount 2500 -> Expects BLOCK (Rule 1).
- Button 'Rule 2 (Unknown)': Selects custom agent 'UntrustedBot_77', action 'place order', amount 1500 -> Expects BLOCK (Rule 2).
- Button 'Rule 3 (View Order)': Selects active agent, action 'view order' -> Expects ALLOW (Rule 3).
- Button 'Rule 4 (Order <= 5k)': Selects active agent with < 3 actions today, action 'place order', amount 3499 -> Expects ALLOW (Rule 4).
- Button 'Rule 5 (Order > 5k)': Selects active agent, action 'place order', amount 18999 -> Expects ASK CUSTOMER (Rule 5).
- Button 'Rule 6 (Return/Refund)': Selects active agent, action 'refund', amount 2100 -> Expects ASK CUSTOMER (Rule 6).
- Button 'Rule 7 (>3 Daily Actions)': Injects 3 prior money actions for 'Agent-VelocityTester' today, then submits a 4th order of 1200 -> Expects ASK CUSTOMER (Rule 7).
Each button must auto-populate the form, execute the policy engine, display the result banner, and log to the audit table.
```

**Outcome:**  
Enables instant, repeatable demonstration of all seven policies without manual data entry.

---

### Phase 6: Documentation & Reporting Prompts

#### Prompt 6.1: Project Report Generation Prompt
```text
Create PROMPTS.md and REPORT.md for my project.
Name: Aryan Thakur
Enrolment: PGD202566017
Company: Amazon India
Project: Agent Gatekeeper for Amazon India
Requirements for REPORT.md:
- Executive Summary and Industrial Motivation in E-commerce Agent Governance
- Problem Statement & Objectives
- Architecture (Frontend, State Management, Policy Engine)
- Complete Specification and Logical Hierarchy of the 7 Rules
- Test Verification Matrix (Inputs, Expected, Actual Results)
- Security, Compliance (RBI / Customer Protection), and Ethical AI Alignment
- Conclusion & Future Enhancements
```

---

## 3. Summary of Key Decisions & Lessons Learned

| Topic | Design Consideration | Prompt Solution |
|---|---|---|
| **Rule Collision** | Conflict between Rule 4 ($\le$ ₹5,000) and Rule 7 ($> 3$ daily actions). | Evaluated Rule 7 before Rule 4 in the financial pipeline. A 4th transaction of ₹500 is safely flagged as `ASK CUSTOMER`. |
| **Revocation Tracking** | Requirement to save date and time upon revocation. | Added `revokedAt: new Date().toISOString()` to the Agent schema and displayed formatted timestamp in both the table and decision banners. |
| **Testing Unknown Agents** | HTML select dropdowns cannot normally accept unlisted names. | Implemented a checkbox toggle: "Type Unknown Agent" swapping select with an input field to cleanly test Rule 2. |
| **Browser Compatibility** | Standalone single-page web app without Node/npm runtime overhead. | Single-file architecture (`index.html`) containing embedded CSS and modular Vanilla JavaScript that runs directly via `file:///` in any browser. |

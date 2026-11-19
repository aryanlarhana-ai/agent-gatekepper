# Agent Design Diagram

```text
                    ┌────────────────────┐
                    │   CSV / Upload     │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Data Quality     │
                    │ validates and cleans
                    └─────────┬──────────┘
                              │
             ┌────────────────┴────────────────┐
             │                                 │
      ┌──────▼──────┐                  ┌───────▼──────┐
      │ Order Risk  │                  │   Revenue    │
      └──────┬──────┘                  └───────┬──────┘
             └────────────────┬────────────────┘
                              │
             ┌────────────────▼────────────────┐
             │ Fraud → Inventory → Finance      │
             │ (sequential specialist hand-offs)│
             └────────────────┬────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │ Executive Decision │
                    │ ranks/conflict     │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ Human Approval     │
                    │ SQLite audit trail  │
                    └────────────────────┘
```

The Order Risk and Revenue agents run in parallel after data quality.

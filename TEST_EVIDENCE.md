# Test Evidence

Run:

```powershell
py -m pytest tests -q
```

Verified results:
- 12 tests passed.
- Three hand-calculated threshold cases passed.
- The 200-row synthetic dataset and injected ranges passed.
- Revoked and unknown agent checks passed.
- SQLite Approve, Reject and Reset transitions passed.
- Safety invariant passed.
- Multi-agent orchestrator and Excel/PDF report generation passed.
- A dirty numeric value is converted safely and reported.

## Independent hand checks

| Case | Calculation | Expected | Actual |
|---|---|---|---|
| Missing ID, Rs. 3000 | Missing-ID rule overrides amount | BLOCK | BLOCK |
| Verified ID, Rs. 6500 | 6500 > 5000 | ASK CUSTOMER | ASK CUSTOMER |
| Verified ID, Rs. 2000 | 2000 <= 5000 | ALLOW | ALLOW |

No API key was required for the full run.

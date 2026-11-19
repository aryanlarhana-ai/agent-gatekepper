# Answer Key

| Injected problem | Rows | Deterministic result |
|---|---:|---|
| Missing ID + high value | ORD_001-ORD_020 | BLOCK |
| Verified ID + high value | ORD_021-ORD_040 | ASK CUSTOMER |
| Repeat refund abuse | ORD_041-ORD_060 | BLOCK (FRAUD) |
| Standard orders | ORD_061-ORD_150 | ALLOW when ID is valid and stock exists |
| Standard refunds | ORD_151-ORD_170 | ASK CUSTOMER |
| High-value edge orders | ORD_171-ORD_185 | ASK CUSTOMER |
| Dirty stock/ID edge cases | ORD_186-ORD_200 | BLOCK or ALLOW according to the applicable rule |

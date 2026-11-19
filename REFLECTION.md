# Reflection

AI helped accelerate the project by producing the modular agent structure, Streamlit interface, reports and documentation. It was also useful for converting the original policy prototype into a more complete submission and for identifying missing assignment components. However, I did not treat generated code or AI narratives as proof. I checked the deterministic threshold calculations, expected policy decisions, database transitions and report files with tests and direct commands.

The most important safeguard was keeping all monetary and policy decisions in Python rather than in the language model. Gemini is optional and is used only to interpret pre-calculated results. The system also contains an explicit simulation flag and no external payment or refund integration. This means the approval centre records decisions only, while a real implementation would require separately configured, authorized integrations.

Some AI-generated claims initially overstated how much had been implemented, so the project documentation and tests had to be checked against the actual files. The synthetic dataset is useful for demonstration, but it does not represent a real Amazon customer base or real transaction history.

My own verification confirmed 12 passing tests, successful report generation and a reachable Streamlit endpoint. The remaining work that would require live business access is real identity-provider integration, real inventory sources, payment gateway controls and a production authentication system. Those integrations are intentionally excluded from this academic simulation.

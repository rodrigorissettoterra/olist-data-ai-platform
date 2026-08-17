# Data Quality

**MVP status:** Core contracts implemented; dedicated framework deferred.

The executable MVP does not use a separate OSS Data Quality platform.

Current quality controls are implemented through ingestion metadata, deterministic transformations and integration tests, including:

- source SHA-256 and row counts;
- expected Bronze/Silver/Gold/Metrics schemas;
- unique grain for `gold.fact_orders`;
- KPI consistency checks;
- persisted model artifact checks;
- API and agent integration checks.

A dedicated Data Quality framework, profiling reports, alerting and richer failure policies remain part of the target architecture.

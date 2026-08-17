# Machine Learning

**MVP status:** Implemented.

Primary use case: `delivery_delay_risk`.

The model uses XGBoost in a scikit-learn pipeline with:

- point-in-time feature selection;
- temporal 70/15/15 train/validation/test split;
- threshold selection on validation only;
- local MLflow tracking with SQLite;
- persisted model bundle for FastAPI inference.

Final test metrics:

| Metric | Value |
|---|---:|
| ROC AUC | 0.7257 |
| PR AUC | 0.1627 |
| Precision | 0.1438 |
| Recall | 0.5956 |
| F1 | 0.2316 |
| Threshold | 0.41 |

Train:

```powershell
.\.venv\Scripts\python.exe .\ml\src\olist_ml\train_delay_model.py
```

Dedicated model monitoring and production model-registry workflows remain target-architecture capabilities.

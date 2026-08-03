# Contributing

## Development setup

```bash
python -m pip install -e ".[dev]"
python -m signalroom.training
ruff check .
pytest --cov=signalroom --cov-fail-under=85
```

Model or policy changes must regenerate the artifacts, update the model card
when evaluation changes, and test both ranking and capacity constraints. Keep
predictive risk, treatment effect, and business policy as separate concepts in
code and documentation.

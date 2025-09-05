## Contributing

Thank you for contributing to SUP! Please:

- Use `pre-commit` hooks (Black, Ruff, Isort, Pyupgrade, MyPy where applicable)
- Write tests (pytest + Hypothesis) and keep coverage healthy
- Include clear commit messages and small focused PRs
- Discuss larger changes via an RFC (see RFCs section)

Setup:

```bash
pip install -r requirements-dev.txt  # or use pipx/venv
pre-commit install
pytest -q
```



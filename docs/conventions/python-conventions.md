# Convenções Python

**Status:** Approved v1.0

- Python >= 3.12.
- PEP 8.
- Ruff para lint/format.
- line length: 88.
- type hints em código de produção.
- docstrings Google-style quando úteis.
- imports: standard library, third-party, internos.
- preferir imports absolutos.
- evitar `sys.path` hacks.
- evitar estado global.
- configuração operacional via env/config objects.
- nada de password/token hardcoded.
- nada de `except Exception: pass`.
- logging em vez de `print()` para componentes operacionais.
- aleatoriedade relevante deve usar seed controlada.
- testes nomeados `test_<expected_behavior>`.

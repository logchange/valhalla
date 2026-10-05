# Valhalla

## Testy
System Python nie ma zależności ani `pytest`, a `python3 -m venv` nie działa (brak `ensurepip`). Używaj `uv` (za proxy z własnym CA potrzebne `--system-certs`):

```
uv venv <dir>/venv
VIRTUAL_ENV=<dir>/venv uv pip install --system-certs -r requirements.txt
<dir>/venv/bin/python -m pytest -q test
```

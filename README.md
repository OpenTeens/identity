# Identity Backend

## Install Deps

```bash
uv sync
```

## Run

```bash
uv run uvicorn main:app --port 35271
```

## Export Requirements

这个不用跑 QAQ 只是用 `uv` 生成 `requirements.txt`

```bash
uv export --format requirements-txt > requirements.txt
```

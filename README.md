# Identity Backend

## Install Deps

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --port 35271
```

## Export Requirements

这个不用跑 QAQ 只是我们用 poetry 的生成 `requirements.txt`

```bash
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

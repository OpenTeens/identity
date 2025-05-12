# Identity Backend

## Install UV

This project uses [UV](https://docs.astral.sh/) as the package manager. You have to [install it first](https://docs.astral.sh/uv/getting-started/installation/), if you don't have it already.

```bash
# Linux / MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Install Deps

```bash
uv sync
```

## Run

```bash
uv run task dev
```

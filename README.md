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
uv run task dev # development
uv run task serve # production
```

## Migrations

在开发的过程中，我们可能会多次修改数据库 model，这个时候我们需要生成 migration 文件。并对数据库进行迁移。

修改模型后先运行：

```bash
uv run alembic revision --autogenerate -m "your message"
```

`alembic/versions` 下面生成的文件和模型修改一起 commit 上去

然后运行一次迁移命令，如果是拉取了最新的代码，也要运行一次迁移命令：

```bash
uv run alembic upgrade head
```

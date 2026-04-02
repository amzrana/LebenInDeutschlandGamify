# Developing

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install ruff pytest
```

## Running

```bash
lid-trainer
lid-trainer --state Bayern
lid-trainer --port 8080
```

## Code Quality

```bash
ruff format .
ruff check .
ruff check --fix .
```

## Tests

```bash
pytest
```

## Project Structure

```
src/lid_trainer/
├── __init__.py        # Package metadata
├── cli.py             # Entry point (launches web UI)
├── web.py             # Flask web application
├── questions.py       # Question bank loader
└── data/
    └── questions.json # 460 questions from BAMF PDF
```

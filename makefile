# at the top (optional but nice)
export PYTHONPATH := $(PWD)

PY := python
PIP := $(PY) -m pip

ingest:
	$(PY) -m pipelines.ingest_norgate

features:
	$(PY) -m pipelines.build_features

scores:
	$(PY) -m pipelines.daily_scores

daily: ingest features scores

backtest:
	$(PY) -m pipelines.backtest_job

prepare-golden:
	$(PY) -m tests.prepare_golden

mock-ingest:
	$(PY) -m pipelines.mock_ingest

api:
	$(PY) -m uvicorn apps.backend.main:app --reload --host 0.0.0.0 --port 8000

dev:
	./scripts/dev.sh

dev-real:
	./scripts/dev.sh --real

dev-no-open:
	./scripts/dev.sh --no-open



precommit-test:
	pre-commit run --all-files

env-update:
	conda env update -n vectorbtpro -f environment.yaml --prune

# Repo visibility helpers
repo-public:
	./scripts/visibility-gh.zsh Kevinchen-sd/AIT public

repo-private:
	./scripts/visibility-gh.zsh Kevinchen-sd/AIT private

# Safe Project Template

A minimal template for small teams (≤2 devs) who want to keep code on GitHub while keeping secrets strictly local.

## Quickstart

1) **Create a private GitHub repo** (recommended)
- Via GitHub UI (easiest) or with GitHub CLI:
  ```bash
  gh repo create <your-repo-name> --private --source . --remote origin --push
  ```

2) **Initialize git locally**
```bash
git init
git config --global init.defaultBranch main
git add .
git commit -m "chore: bootstrap project from template"
```

3) **Install pre-commit hooks** (to catch mistakes & accidental secrets)
```bash
# Requires Python installed
pip install pre-commit
pre-commit install
# (Optional but recommended) Initialize a detect-secrets baseline the first time:
pip install detect-secrets
detect-secrets scan > .secrets.baseline
git add .secrets.baseline
git commit -m "chore: add detect-secrets baseline"
```

4) **Create your local secret file (.env)**
```bash
cp .env.example .env
# edit .env to fill in real values; this file is already gitignored
```

5) **Run the sample app** (Python example)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # (if you add one later)
python src/app.py
```

## Daily flow (2-dev agile)
- Create a short-lived branch for each task:
  ```bash
  git checkout -b feat/short-description
  # ...edit...
  pre-commit run --all-files
  git add -A
  git commit -m "feat: short description"
  git push -u origin HEAD
  ```
- Open a PR. Teammate reviews; squash-merge to `main`.
- Before new work:
  ```bash
  git checkout main
  git pull --rebase origin main
  ```

## Secrets policy
- **Never** commit secrets. Keep them in `.env` (gitignored) or your OS keychain.
- Share structure via `.env.example`, never real values.
- If a secret ever leaks, **rotate it immediately**, then clean history with BFG or git-filter-repo.

## Layout
See the repo tree below.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-based To-Do List application (CRUD tasks). Part of a software quality / automated testing course (QLTA). The codebase is intentionally "dirty" — it is the subject of quality and testing exercises.

## Development Commands

```bash
# Run the development server
pipenv run python manage.py runserver

# Apply migrations (re-create db.sqlite3 after cloning)
pipenv run python manage.py migrate

# Run all tests
pipenv run python manage.py test tasks

# Run a single test method
pipenv run python manage.py test tasks.tests.MyTestClass.my_test_method

# Lint (must pass before any commit / build)
pipenv run ruff check .

# Coverage report
pipenv run coverage run manage.py test tasks
pipenv run coverage report
pipenv run coverage html   # → htmlcov/index.html
```

### Build & versioning
```bash
# Bump version, run ruff, commit, tag, and generate a zip archive
./build.sh version=X.Y.Z
```
`build.sh` enforces `ruff check .` before doing anything, then updates `APP_VERSION` in `todo/settings.py`, commits, tags, and creates `todolist-X.Y.Z.zip` via `git archive`.

### Tox (multi-Django matrix)
```bash
pipenv run tox
```
Runs `python manage.py test` against Django 3.2 / 4.2 / 5.2 (see `tox.ini`).

## Architecture

```
manage.py              # Django entry point
todo/
  settings.py          # APP_VERSION lives here; SQLite DB path
  urls.py              # Mounts admin + tasks.urls at root
tasks/
  models.py            # Task: title (CharField), complete (BooleanField), created (DateTimeField)
  forms.py             # TaskForm (ModelForm wrapping Task)
  views.py             # index / updateTask / deleteTask — function-based views
  urls.py              # Routes: / → index, /update_task/<pk>/, /delete_task/<pk>/
  templates/tasks/     # list.html, update_task.html, delete.html, style.css
  fixtures/
    dataset.json       # 3 sample tasks for loaddata tests
  tests.py             # Growing test suite (see below)
  migrations/
    0001_initial.py
pyproject.toml         # Ruff config: line-length=120, rules E/F/I, target py312
tox.ini                # Django 3.2/4.2/5.2 test matrix
```

### Key design points
- `APP_VERSION` in `todo/settings.py` is injected into the template context by `index` and displayed on the homepage.
- All views redirect to `/` after POST. `updateTask` renders its form on GET without redirecting.
- `db.sqlite3` is gitignored — recreate with `pipenv run python manage.py migrate`.
- Commit messages follow **Conventional Commits** (`feat:`, `fix:`, `test:`, `chore:`, etc.).
- Versioning is **SemVer**; tags are managed by `build.sh`.

### Test classes (tasks/tests.py)
| Class | What it covers |
|---|---|
| `SmokeTests` | Trivial always-passes smoke test |
| `UrlSmokeTests` | GET 200 for `/`, `/update_task/<pk>/`, `/delete_task/<pk>/` |
| `UrlCrudBehaviorTests` | POST update redirects + DB change; POST delete redirects + row removed |
| `DatasetImportTests` | `loaddata dataset.json` creates 3 expected Task rows |

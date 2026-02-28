# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-based To-Do List application (CRUD tasks). Part of a software quality / automated testing course (QLTA). The codebase is intentionally "dirty" — it is the subject of quality and testing exercises.

## Development Commands

```bash
# Run the app using Pipenv
pipenv run python manage.py runserver

# Run the development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Run tests
python manage.py test tasks

# Run a single test case
python manage.py test tasks.tests.MyTestClass.my_test_method

# Create new migrations after model changes
python manage.py makemigrations
```

### Build & versioning
```bash
# Bump version, commit, tag, and generate a zip archive
./build.sh version=X.Y.Z
```
`build.sh` updates `APP_VERSION` in `todo/settings.py`, commits, tags, then runs `git archive`.

## Architecture

```
manage.py          # Django entry point
todo/              # Project config package
  settings.py      # APP_VERSION lives here; DB is SQLite (db.sqlite3, gitignored)
  urls.py          # Mounts admin + tasks.urls at root
tasks/             # The single Django app
  models.py        # Task model: title (CharField), complete (BooleanField), created (DateTimeField)
  forms.py         # TaskForm (ModelForm wrapping Task)
  views.py         # index / updateTask / deleteTask — function-based views
  urls.py          # Routes: / → index, /update_task/<pk>/, /delete_task/<pk>/
  templates/tasks/ # list.html, update_task.html, delete.html, style.css
  tests.py         # Empty — this is the starting point for testing exercises
  migrations/      # 0001_initial.py only
```

### Key design points
- `APP_VERSION` from `todo/settings.py` is injected into the template context in `index` and displayed on the homepage.
- All views redirect to `/` after POST. `updateTask` renders its form on GET without redirecting.
- `tasks/views.py` uses wildcard imports (`from .models import *`, `from .forms import *`).
- The database is SQLite; `db.sqlite3` is gitignored but committed historically — re-create it with `python manage.py migrate`.

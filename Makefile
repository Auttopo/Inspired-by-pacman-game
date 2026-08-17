ARGS= config.json
PROGRAM= src/pac-man.py
MFILE= src
TRACE= .install_trace
PYTHON= uv run python
LINT_EXCLUDES= uv_lock,.venv
LINT_EXCLUDES_MYPY= "(uv_lock|\.venv)"


all : run

run : $(TRACE)
	$(PYTHON) $(PROGRAM) $(ARGS)

install $(TRACE) : pyproject.toml Makefile
	uv sync ; \
	UV_SKIP_WHEEL_FILENAME_CHECK=1 uv pip install mazegenerator-00001-py3-none-any.whl ; \
	touch .install_trace

upgrade :
	pip install --upgrade pip ; \
	pip install uv

debug :
	$(PYTHON) -m pdb $(PROGRAM) $(ARGS)

clean :
	$(RM) -r __pycache__
	$(RM) -r $(MFILE)/__pycache__
	$(RM) -r $(MFILE)/*/__pycache__
	$(RM) -r $(MFILE)/*/*/__pycache__
	$(RM) -r .mypy_cache

fclean :
	$(RM) -r __pycache__
	$(RM) -r $(MFILE)/__pycache__
	$(RM) -r $(MFILE)/*/__pycache__
	$(RM) -r $(MFILE)/*/*/__pycache__
	$(RM) -r .mypy_cache
	$(RM) .install_trace
	$(RM) -r .venv
	uv cache prune

lint :
	$(PYTHON) -m flake8 . --exclude $(LINT_EXCLUDES) ; \
	$(PYTHON) -m mypy . --exclude $(LINT_EXCLUDES_MYPY) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict :
	$(PYTHON) -m flake8 . --exclude $(LINT_EXCLUDES) ; \
	$(PYTHON) -m mypy . --exclude $(LINT_EXCLUDES_MYPY) --strict

.PHONY : all run install upgrade debug clean fclean lint lint-strict

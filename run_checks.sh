#! /usr/bin/env bash
printf "\n\n##########  RUNNING PYTEST  ##########\n\n"
python -m pytest --cov=src/dotg --cov-fail-under=95 --cov-report term-missing
printf "\n\n##########  RUNNING BLACK  ##########\n\n"
python -m black --check --diff -l 89 src/dotg/
printf "\n\n##########  RUNNING PYLINT  ##########\n\n"
python -m pylint src/dotg --rcfile=.config/.pylintrc
printf "\n\n##########  RUNNING MYPY  ##########\n\n"
python -m mypy src/dotg --config-file .config/mypy.ini
printf "\n\n#########  COMPLETED CHECKS  ##########\n"
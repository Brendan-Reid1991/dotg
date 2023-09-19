#! /usr/bin/env bash
python3 -m pytest --cov-report term-missing:skip-covered --cov=dotg tests/
python3 -m pytest --cov-report json:cov.json --cov=dotg tests/

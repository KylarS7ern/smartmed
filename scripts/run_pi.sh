#!/usr/bin/env bash
set -e

cd /home/smartmedispender/projects/smartmed
source .venv/bin/activate
export PYTHONPATH=src

python -m smartmed.main
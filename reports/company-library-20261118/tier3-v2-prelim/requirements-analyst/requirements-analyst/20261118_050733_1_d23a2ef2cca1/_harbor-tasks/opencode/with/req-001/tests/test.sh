#!/bin/bash
set -euo pipefail
tests_dir="${HARBOR_TESTS_DIR:-/tests}"
evaluator_dir="${tests_dir}/skill_evaluator"
python3 -I "${evaluator_dir}/eval.py"

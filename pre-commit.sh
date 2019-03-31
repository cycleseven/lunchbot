#!/usr/bin/env bash

# Ensure hooks are run in virtualenv
if [[ "$VIRTUAL_ENV" == "" ]]
then
  source venv/bin/activate
  echo "Activated virtualenv"
fi

yarn lint-staged && pytest

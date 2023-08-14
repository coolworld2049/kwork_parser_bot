#! /usr/bin/env bash

set -eou pipefail

python -m prisma_cleanup

prisma generate

prisma db push

python main.py
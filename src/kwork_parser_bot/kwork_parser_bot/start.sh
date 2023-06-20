#!/usr/bin/env bash

set -euo pipefail

. ./prestart.sh

python kwork_parser_bot/main.py

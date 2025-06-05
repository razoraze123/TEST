#!/usr/bin/env bash
set -euo pipefail
pyinstaller --onefile --name woocommerce-scraper cli.py

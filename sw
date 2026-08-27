#!/data/data/com.termux/files/usr/bin/bash
# Shadow-SetUp CLI wrapper
exec python3 "$(dirname "$(readlink -f "$0")")/shadow/cli.py" "$@"

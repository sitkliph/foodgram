#!/bin/sh
set -e

find /static -mindepth 1 -exec rm -rf {} +
cp -r /app/build/. /static/

exec "$@"
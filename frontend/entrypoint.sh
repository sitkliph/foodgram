#!/bin/sh
set -e

rm -rf /static/*
cp -r /app/build/. /static/

exec "$@"
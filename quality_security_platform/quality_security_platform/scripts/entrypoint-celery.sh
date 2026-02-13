#!/bin/bash
set -e
until nc -z redis 6379; do echo "Waiting for Redis..."; sleep 1; done
exec "$@"

#!/bin/bash
set -e
until nc -z redis 6379; do echo "等待 Redis..."; sleep 1; done
exec "$@"

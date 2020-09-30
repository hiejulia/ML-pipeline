#!/usr/bin/env bash

set -euo pipefail


CLUSTER="$1"
APP_NAME="${2:-"$APP_NAME"}"
CURDIR="$(dirname "$0")"
# k8s create secret 
exec kubectl --context "$CLUSTER" create secret generic "${APP_NAME}" --from-env-file="$CURDIR/secrets.env"

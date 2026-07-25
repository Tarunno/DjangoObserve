#!/bin/sh
set -eu

TEMPLATE=/etc/prometheus/prometheus.yml.template
OUTPUT=/tmp/prometheus.yml

DJANGO_METRICS_TARGET="${DJANGO_METRICS_TARGET:-host.docker.internal:8000}"
DJANGO_METRICS_PATH="${DJANGO_METRICS_PATH:-/metrics}"
DJANGO_APP_LABEL="${DJANGO_APP_LABEL:-django}"

# Escape sed replacement specials in target/path/label values.
escape_sed() {
  printf '%s' "$1" | sed -e 's/[\\/&]/\\&/g'
}

TARGET_ESC=$(escape_sed "$DJANGO_METRICS_TARGET")
PATH_ESC=$(escape_sed "$DJANGO_METRICS_PATH")
LABEL_ESC=$(escape_sed "$DJANGO_APP_LABEL")

sed \
  -e "s/__DJANGO_METRICS_TARGET__/${TARGET_ESC}/g" \
  -e "s/__DJANGO_METRICS_PATH__/${PATH_ESC}/g" \
  -e "s/__DJANGO_APP_LABEL__/${LABEL_ESC}/g" \
  "$TEMPLATE" > "$OUTPUT"

exec /bin/prometheus \
  --config.file="$OUTPUT" \
  --storage.tsdb.path=/prometheus \
  --storage.tsdb.retention.time="${PROMETHEUS_RETENTION:-15d}" \
  --storage.tsdb.retention.size="${PROMETHEUS_RETENTION_SIZE:-10GB}" \
  --web.enable-lifecycle \
  --web.external-url="${PROMETHEUS_EXTERNAL_URL:-http://localhost:9090}"

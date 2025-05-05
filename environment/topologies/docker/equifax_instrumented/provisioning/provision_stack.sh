#!/bin/bash
set -euo pipefail

echo "[INFO] Waiting for Elasticsearch..."
until curl -s http://localhost:9200 | grep -q "cluster_name"; do
  echo "[WAIT] Elasticsearch unavailable..."
  sleep 5
done
echo "[OK] Elasticsearch ready"

echo "[INFO] Waiting for Kibana..."
MAX_WAIT=90
WAIT=0
until status=$(curl -s http://localhost:5601/api/status 2>/dev/null | jq -r '.status.overall.level' 2>/dev/null); do
  echo "[WAIT] Kibana unavailable (no JSON)... ($WAIT/$MAX_WAIT)"
  sleep 5
  WAIT=$((WAIT + 5))
  [[ "$WAIT" -ge "$MAX_WAIT" ]] && echo "[ERROR] Kibana not ready after $MAX_WAIT seconds" && exit 1
done

until [[ "$status" == "available" ]]; do
  echo "[WAIT] Kibana not ready... ($WAIT/$MAX_WAIT)"
  sleep 5
  WAIT=$((WAIT + 5))
  [[ "$WAIT" -ge "$MAX_WAIT" ]] && echo "[ERROR] Kibana not ready after $MAX_WAIT seconds" && exit 1
  status=$(curl -s http://localhost:5601/api/status 2>/dev/null | jq -r '.status.overall.level' 2>/dev/null)
done
echo "[OK] Kibana ready"

echo "[INFO] Verifying Elastic Agent logs..."
curl -s http://localhost:9200/_cat/indices?v | grep -E 'metricbeat|filebeat' || echo "[WARN] No agent logs found"

create_view() {
  local name=$1
  local id=$2
  local pattern=$3

  if curl -s -f "http://localhost:5601/api/saved_objects/index-pattern/${id}" -H 'kbn-xsrf: true' > /dev/null; then
    echo "[SKIP] View '$name' already exists (by ID)"
    return
  fi

  if curl -s "http://localhost:5601/api/saved_objects/_find?type=index-pattern&per_page=1000" \
    | jq -r '.saved_objects[].attributes.title' | grep -Fxq "${pattern}"; then
    echo "[SKIP] View '$name' already exists (by pattern)"
    return
  fi

  echo "[INFO] Creating: $name"
  response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:5601/api/data_views/data_view \
    -H 'kbn-xsrf: true' -H 'Content-Type: application/json' \
    -d "{\"data_view\":{\"title\":\"$pattern\",\"name\":\"$name\",\"id\":\"$id\"}}")

  body=$(echo "$response" | head -n -1)
  code=$(echo "$response" | tail -n1)

  if [ "$code" == "200" ]; then
    echo "[OK] View '$name' created"
  else
    echo "[ERROR] Failed to create '$name' (HTTP $code)"
    echo "[DEBUG] Response: $body"
  fi
}

create_view "Logs - Filebeat" dv_logs_filebeat ".ds-logs-elastic_agent.filebeat-*"
create_view "Logs - Metricbeat" dv_logs_metricbeat ".ds-logs-elastic_agent.metricbeat-*"
create_view "Metrics - Agent" dv_metrics_agent ".ds-metrics-elastic_agent.*"

echo "[SUCCESS] Stack provisioned and data views validated"

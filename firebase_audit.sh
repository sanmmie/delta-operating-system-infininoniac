#!/usr/bin/env bash
# firebase_audit.sh
# Usage: ./firebase_audit.sh PROJECT_ID
set -euo pipefail
PROJECT=$1
OUT="firebase_audit_${PROJECT}_$(date -u +%Y%m%dT%H%M%SZ).json"
tmpdir=$(mktemp -d)
echo "Writing report to $OUT"

# helper to run commands gracefully
run() {
  desc="$1"; shift
  echo "RUN: $desc" >&2
  if out=$("$@" 2>&1); then
    echo "$out" > "$tmpdir/$(echo $desc|tr ' /' '__').json" || true
  else
    echo "{\"error\": \"failed to run: $desc\"}" > "$tmpdir/$(echo $desc|tr ' /' '__').json"
  fi
}

run "enabled_apis" gcloud services list --project="$PROJECT" --enabled --format=json
run "iam_policy" gcloud projects get-iam-policy "$PROJECT" --format=json
run "firebase_apps" firebase --project="$PROJECT" apps:list --json || echo "{}" > "$tmpdir/firebase_apps.json"
run "hosting_sites" gcloud firebase hosting:sites:list --project="$PROJECT" --format=json || echo "{}" > "$tmpdir/hosting_sites.json"
run "cloud_functions" gcloud functions list --project="$PROJECT" --format=json || echo "[]" > "$tmpdir/cloud_functions.json"
run "cloud_run" gcloud run services list --project="$PROJECT" --format=json || echo "[]" > "$tmpdir/cloud_run.json"
run "firestore_indexes" gcloud firestore indexes list --project="$PROJECT" --format=json || echo "[]" > "$tmpdir/firestore_indexes.json"
run "storage_buckets" gsutil ls -p "$PROJECT" -L || gsutil ls -p "$PROJECT" > "$tmpdir/storage_buckets.json" || echo "[]" > "$tmpdir/storage_buckets.json"
run "billing" gcloud beta billing projects describe "$PROJECT" --format=json || echo "{}" > "$tmpdir/billing.json"
run "auth_providers" firebase --project="$PROJECT" auth:providers || echo "{}" > "$tmpdir/auth_providers.json"
run "firestore_rules" firebase --project="$PROJECT" firestore:rules:get || echo "{}" > "$tmpdir/firestore_rules.json"
run "storage_rules" firebase --project="$PROJECT" storage:rules:get || echo "{}" > "$tmpdir/storage_rules.json"
run "quota_firestone" gcloud alpha services quota get --project="$PROJECT" --service=firestore.googleapis.com || echo "{}" > "$tmpdir/quota_firestore.json"

# assemble into single JSON
echo "{" > "$OUT"
first=true
for f in "$tmpdir"/*.json; do
  name=$(basename "$f" .json)
  if [ "$first" = true ]; then first=false; else echo "," >> "$OUT"; fi
  echo -n "\"$name\": " >> "$OUT"
  cat "$f" >> "$OUT"
done
echo "}" >> "$OUT"

echo "Report complete: $OUT"

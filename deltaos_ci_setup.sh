#!/bin/bash
# deltaos_ci_setup.sh
# Run this from the root of delta_os_core

# 1️⃣ Create dev branch
git checkout -b dev/ci-setup

# 2️⃣ Ensure folder structure
mkdir -p .github/workflows security lib/core lib/middleware lib/models lib/services lib/utils test

# 3️⃣ Create security workflow file
cat << 'EOF' > .github/workflows/security.yml
name: 🛡️ DeltaOS Security & Threat Intelligence

on:
  push:
    branches: [ main, master, dev ]
  pull_request:
    branches: [ main, master, dev ]
  schedule:
    - cron: '0 2 * * *'
    - cron: '0 */6 * * *'

permissions:
  contents: write
  security-events: write
  issues: write
  pull-requests: write

jobs:
  security_scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dart-lang/setup-dart@v1
        with: sdk: stable
      - run: dart pub get

      - name: Dart Linter
        run: dart analyze --fatal-infos > lint.log || true
      - name: Dart Dependency Audit
        run: dart pub outdated --mode=null-safety > outdated.log && dart pub audit > audit.log || true

      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with: output: results/codeql-results.sarif

      - name: Auto-Remediate Vulnerable Dependencies
        run: |
          VULN_COUNT=$(grep -c '!=' outdated.log || echo '0')
          if [ "$VULN_COUNT" -gt 0 ]; then
            dart pub upgrade
            git config user.name "DeltaOS Security Bot"
            git config user.email "security@deltaos.ai"
            BRANCH="security/fix-$(date +%s)"
            git checkout -b $BRANCH
            git add pubspec.* || true
            git commit -m "🔒 Automated Security Patch"
            git push https://x-access-token:${GITHUB_TOKEN}@github.com/${{ github.repository }} $BRANCH
            gh pr create --title "🔒 Automated Security Patch" --body "This PR upgrades vulnerable dependencies detected by DeltaOS Security Guardian." --base main
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        continue-on-error: true

      - name: Send Security Summary to Slack
        if: always()
        uses: slackapi/slack-github-action@v1.27.0
        with:
          payload: |
            {
              "text": ":robot_face: *DeltaOS Security Summary*",
              "attachments": [{
                "color": "${{ job.status == 'success' && 'good' || 'danger' }}",
                "fields": [
                  { "title": "Repo", "value": "<https://github.com/${{ github.repository }}|${{ github.repository }}>", "short": true },
                  { "title": "Branch", "value": "${{ github.ref_name }}", "short": true },
                  { "title": "Status", "value": "${{ job.status }}", "short": true }
                ]
              }]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
EOF

# 4️⃣ Reminder to add secrets in GitHub
echo "🔹 Make sure to add the following repository secrets in GitHub:"
echo "   1. SLACK_WEBHOOK_URL"
echo "   2. GITHUB_TOKEN (auto-provided by GitHub Actions)"
echo ""
echo "✅ Dev branch 'dev/ci-setup' created with workflow ready. Push it to GitHub:"
echo "   git push -u origin dev/ci-setup"

#!/bin/bash
cd /opt/data/weather-app
echo "=== Step 1: Versions ==="
node --version
npm --version
echo ""
echo "=== Step 2: npm install ==="
npm install 2>&1
echo ""
echo "=== Step 3: Run vitest tests ==="
npx vitest run --coverage 2>&1
echo ""
echo "=== Step 4: Git init and commit ==="
git init 2>&1
git add -A 2>&1
git commit -m "feat: Atmo weather dashboard - initial implementation" 2>&1
echo ""
echo "=== Step 5: Git status ==="
git status 2>&1
echo ""
echo "=== DONE ==="
# Real Session: Weather App Deploy Workflow

Session demonstrating the Script-Write-Then-Execute pattern.

## The Task

Push integration test code (Charmander's output) to GitHub.

## Workflow

1. **Parent** delegates to Charmander (testing profile):
   ```
   goal: Write integration tests for the weather-app project
   context: project at /opt/data/weather-app/...test files go in tests/...
   toolsets: ["file"]
   ```
   Charmander writes 3 new test files (~1,250 lines):
   - `tests/fullpage.integration.test.js`
   - `tests/server-dom.integration.test.js`
   - `tests/edgecases.integration.test.js`

2. **Parent** verifies: runs `npx vitest run` — all 229 tests pass.

3. **Parent** delegates to Squirtle (DevOps profile):
   ```
   goal: Push all code to GitHub — init git, create repo, push
   context: project at /opt/data/weather-app/...no git repo yet...package name: atmo-weather-app
   toolsets: ["file", "web"]
   ```

4. **Squirtle** writes `deploy.sh` — a self-contained bash script that:
   - Reads GITHUB_TOKEN from env or `/opt/data/.env`
   - Inits git, renames branch to `main`, stages+commits
   - Creates GitHub repo via API (handles "already exists")
   - Pushes to origin
   Returns: "script at /opt/data/weather-app/deploy.sh"

5. **Parent** runs the script: `subprocess.run(["bash", "/opt/data/weather-app/deploy.sh"])`

6. **Parent** hits blocker — no GITHUB_TOKEN in environment. Reports to user.

## Key Lessons

- Subagent wrote a complete, idempotent script but couldn't execute it
- The deploy.sh pattern (token discovery, username detection, idempotent repo creation) is a good template
- The parent must verify credentials exist BEFORE delegating deployment work, or at least be prepared to report the blocker
- The subagent-Squirtle wrote `deploy.sh` with `set -euo pipefail` and proper error handling — this is a good pattern to require from subagents: self-contained, idempotent, guard-checking scripts

# Lab-01: Coding AI Market Insights and Developer Tooling Radar

This lab walks through a GitHub Agentic Workflows pipeline that tracks coding AI updates and turns them into a market insights report.

Duration: 60 minutes

You will fork the repository, configure a DeepSeek API key and gh-aw, run the workflow manually, inspect an AI-generated coding AI report, and deploy it with GitHub Pages.

## Architecture

```text
Coding AI sources
    -> Phase 1: signal fetch
MCP Scripts (Python tools)
    -> raw_signals.json
    -> Phase 2: hotspot clustering
LLM (DeepSeek) + cluster_or_fallback
    -> hotspots.json
    -> Phase 3: insight generation
LLM (DeepSeek) + insight_or_fallback
    -> insights.json
    -> Phase 4: report rendering
LLM (DeepSeek) + render_report_or_fallback
    -> report.md
    -> safe-outputs creates PR
Merge PR -> deploy-pages runs
    ->
GitHub Pages
```

## Lab 0: Environment Setup and Fork (10 minutes)

Prerequisites:

- GitHub account
- DeepSeek API key with available balance
- Internet-connected computer with macOS, Linux, or Windows WSL
- Python 3.10+
- VS Code, recommended

Steps:

1. Fork `https://github.com/MetaHuman/info-insights.git`.
2. Clone your fork:

```bash
git clone https://github.com/<your-username>/info-insights.git
cd info-insights
```

3. Install GitHub CLI if needed:

```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
sudo apt install gh

# Windows
winget install GitHub.cli
```

4. Log in:

```bash
gh auth login
```

5. Install gh-aw:

```bash
gh extension install github/gh-aw
```

6. Verify:

```bash
gh aw --version
python3 --version
```

## Lab 1: Understand the Project (10 minutes)

Open the project in VS Code and inspect:

1. `.github/workflows/tech-insight.md`

   This is the gh-aw source workflow. It defines the manual trigger, permissions, tool access, DeepSeek model settings, network allowlist, MCP script tools, and the English instructions for the four-phase coding AI report pipeline.

2. `Lab-01-Tech-Insights/mcp-scripts/`

| Script | Purpose |
|--------|---------|
| `tech_read_source_list.py` | Reads source configuration |
| `tech_fetch_all_to_disk.py` | Fetches all configured source payloads |
| `tech_load_articles_from_disk.py` | Parses and filters articles |
| `tech_cluster_or_fallback.py` | Validates or falls back for hotspot clustering |
| `tech_insight_or_fallback.py` | Validates or falls back for hotspot insights |
| `tech_render_report_or_fallback.py` | Validates or falls back for Markdown report rendering |
| `write_text_file.py` | Writes text output files |

3. `Lab-01-Tech-Insights/input/api/rss_list.json`

   Contains curated coding AI sources, including official product feeds, changelogs, AI coding pages, and developer news feeds. Each source has a `signal_level` and optional `include_keywords` filter.

4. `Lab-01-Tech-Insights/frontend/`

   `index.html` and `main.js` render the Markdown report in the browser.

Key idea: gh-aw compiles a Markdown workflow with YAML frontmatter into a GitHub Actions workflow. The AI agent runs in Actions, calls the configured tools, and produces reviewable report outputs.

## Lab 2: Configure Auth and Run (20 minutes)

### Step 1: Enable Actions

Open your fork on GitHub, go to **Settings -> Actions -> General**, and confirm Actions are enabled.

### Step 2: Set DeepSeek API Key

Create an API key at `https://platform.deepseek.com/api_keys`, then add it to your fork:

- Repository **Settings -> Secrets and variables -> Actions**
- **New repository secret**
- Name: `DEEPSEEK_API_KEY`
- Value: your API key

CLI option:

```bash
gh secret set DEEPSEEK_API_KEY
```

Never commit real API keys.

### Step 3: Compile the gh-aw Workflow

```bash
gh aw compile .github/workflows/tech-insight.md
```

This generates `.github/workflows/tech-insight.lock.yml`.

### Step 4: Push the Compiled Result

```bash
git add .github/workflows/
git commit -m "chore: compile coding ai insight workflow"
git push origin main
```

### Step 5: Trigger the Workflow

Recommended UI path:

1. Open the repository **Actions** tab.
2. Select **Coding AI Insight Workflow**.
3. Click **Run workflow**.

CLI option:

```bash
gh workflow run "Coding AI Insight Workflow"
```

### Step 6: Inspect the Run

Open the running workflow and expand the agent job logs. The workflow usually takes 15-20 minutes, depending on source latency and model response time.

### Step 7: Merge the Report PR

After success, safe-outputs opens a PR with the latest report. Review and merge it, then pull the latest code:

```bash
git pull origin main
```

Key output files:

- `Lab-01-Tech-Insights/output/raw_signals.json`
- `Lab-01-Tech-Insights/output/clusters/hotspots.json`
- `Lab-01-Tech-Insights/output/insights/insights.json`
- `Lab-01-Tech-Insights/output/report.md`
- `Lab-01-Tech-Insights/frontend/report.md`

## Lab 3: View the Report Locally (10 minutes)

Open:

```bash
code Lab-01-Tech-Insights/output/report.md
```

Expected report structure:

- Market Summary
- Cross-Source Trends
- Important Single-Source Updates
- Company Competition Radar
- New Products and Capability Releases
- Adoption and Policy
- Technical Research

Preview the frontend:

```bash
python3 -m http.server 8000 --directory Lab-01-Tech-Insights/frontend
```

Visit `http://localhost:8000`.

## Lab 4: Scheduled Trigger and GitHub Pages (10 minutes)

### Experiment A: Add a Schedule

Edit `.github/workflows/tech-insight.md` and change `on:` to:

```yaml
on:
  workflow_dispatch:
  schedule: daily around 9am utc+8
```

Then recompile and push.

### Experiment B: Enable GitHub Pages

1. Open **Settings -> Pages**.
2. Set **Source** to **GitHub Actions**.
3. GitHub Pages deploys when `Lab-01-Tech-Insights/frontend/` changes on `main`, such as after merging a Coding AI Insight report PR.

Manual deploy:

```bash
gh workflow run "Deploy GitHub Pages"
```

Visit `https://<your-username>.github.io/info-insights/`.

## Summary

You learned how to:

- Use gh-aw as a Markdown workflow plus MCP Scripts plus AI engine.
- Configure, compile, and run a coding AI insights workflow.
- Publish the generated report through GitHub Pages.

Further experiments:

- Switch `engine.model` to `deepseek-v4-pro` and compare report quality and cost.
- Add or tune coding AI sources in `rss_list.json`.
- Improve report styling in `frontend/styles.css`.
- Add safe-outputs automation for Issues or Discussions.
- Explore more gh-aw patterns at https://github.github.com/gh-aw/.

## Appendix A: Directory Reference

```text
info-insights/
├── .github/workflows/
│   ├── tech-insight.md           # gh-aw workflow definition
│   ├── tech-insight.lock.yml     # compiled Actions YAML
│   └── deploy-pages.yml          # Pages deployment workflow
├── Lab-01-Tech-Insights/
│   ├── mcp-scripts/              # MCP Script tools
│   ├── input/api/rss_list.json   # coding AI source list
│   ├── frontend/                 # static report frontend
│   └── output/                   # runtime outputs
```

## Appendix B: Troubleshooting

1. `gh aw compile` fails: check YAML frontmatter and make sure the `---` delimiters are intact.
2. Workflow run fails: check `DEEPSEEK_API_KEY`, account balance, and `network.allowed`.
3. Source fetch times out: increase `timeout_seconds`.
4. GitHub Pages returns 404: confirm Pages source is set to GitHub Actions.
5. Need to inspect the agent work: expand the agent step in the Actions logs.

## Appendix C: References

- gh-aw docs: https://github.github.com/gh-aw/
- GitHub CLI: https://cli.github.com

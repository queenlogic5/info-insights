# Coding AI Tech Insights

A GitHub Agentic Workflows and DeepSeek API pipeline for tracking coding AI, developer tools, coding agents, AI-native IDEs, model updates for software engineering, and enterprise governance.

The project fetches coding-AI-focused RSS and web sources, clusters hot topics, generates market insights, renders a Markdown report, and publishes the latest report through GitHub Pages.

## Workflow

```text
Coding AI sources
  -> fetch and clean
  -> DeepSeek hotspot clustering
  -> DeepSeek insight generation
  -> Markdown report
  -> Pull Request
  -> GitHub Pages
```

The workflow uses `deepseek-v4-flash` through gh-aw BYOK configuration against DeepSeek's OpenAI-compatible API. A GitHub Copilot subscription is not required for the model call.

## Project Structure

```text
.
├── .github/workflows/
│   ├── tech-insight.md          # gh-aw workflow source
│   ├── tech-insight.lock.yml    # compiled GitHub Actions workflow
│   └── deploy-pages.yml         # GitHub Pages deployment
└── Lab-01-Tech-Insights/
    ├── input/api/               # coding AI source configuration
    ├── mcp-scripts/             # fetch, cluster, insight, and report tools
    ├── output/                  # pipeline outputs
    ├── frontend/                # static report viewer
    ├── run_local_pipeline.py    # deterministic local diagnostic runner
    └── README.md                # lab tutorial
```

## Requirements

- GitHub account
- DeepSeek API key with available balance
- GitHub CLI `gh`
- gh-aw extension
- Python 3.10+

Install and check gh-aw:

```bash
gh extension install github/gh-aw
gh aw --version
```

## Configure DeepSeek API Key

In your GitHub repository, add a repository secret under **Settings -> Secrets and variables -> Actions**:

```text
Name:  DEEPSEEK_API_KEY
Value: your DeepSeek API key
```

You can also set it with GitHub CLI:

```bash
gh secret set DEEPSEEK_API_KEY
```

Do not commit real API keys to code, `.env.example`, docs, or workflow files.

## Allow Actions to Create Pull Requests

The Coding AI Insight workflow uses safe-outputs to create report PRs. Before the first run, enable the matching repository permission:

1. Open repository **Settings**.
2. Choose **Actions -> General**.
3. Scroll to **Workflow permissions**.
4. Enable **Allow GitHub Actions to create and approve pull requests**.
5. Save the setting.

With GitHub CLI:

```bash
gh api \
  --method PUT \
  repos/OWNER/REPO/actions/permissions/workflow \
  -f default_workflow_permissions=read \
  -F can_approve_pull_request_reviews=true
```

Replace `OWNER/REPO` with your repository, for example `MetaHuman/info-insights`.

## Compile and Run the Workflow

From the repository root:

```bash
gh aw compile .github/workflows/tech-insight.md
gh workflow run "Coding AI Insight Workflow"
```

You can also run it from the GitHub repository **Actions** page by choosing **Coding AI Insight Workflow**.

When the workflow completes, it creates a pull request containing the latest report. Main outputs:

- `Lab-01-Tech-Insights/output/raw_signals.json`
- `Lab-01-Tech-Insights/output/clusters/hotspots.json`
- `Lab-01-Tech-Insights/output/insights/insights.json`
- `Lab-01-Tech-Insights/output/report.md`
- `Lab-01-Tech-Insights/frontend/report.md`

## Local Diagnostic Run

The local script uses deterministic fallback behavior and does not call DeepSeek:

```bash
python Lab-01-Tech-Insights/run_local_pipeline.py
```

Preview the static frontend:

```bash
python -m http.server 8000 --directory Lab-01-Tech-Insights/frontend
```

Then visit `http://localhost:8000`.

## More

See [Lab-01-Tech-Insights/README.md](Lab-01-Tech-Insights/README.md) for the complete lab tutorial.

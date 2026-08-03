---
name: Coding AI Insight Workflow
on:
  workflow_dispatch:
strict: false
permissions:
  contents: read
engine:
  id: copilot
  model: deepseek-v4-flash
  env:
    COPILOT_PROVIDER_BASE_URL: https://api.deepseek.com
    COPILOT_PROVIDER_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
    COPILOT_PROVIDER_TYPE: openai
    COPILOT_PROVIDER_WIRE_API: completions
tools:
  bash: [":*"]
  edit:
timeout-minutes: 45
network:
  allowed:
    - defaults
    - python
    - "api.deepseek.com"
    - "openai.com"
    - "github.blog"
    - "raw.githubusercontent.com"
    - "www.anthropic.com"
    - "www.cursor.com"
    - "huggingface.co"
    - "www.infoq.com"
    - "techcrunch.com"
    - "www.theverge.com"
    - "simonwillison.net"
safe-outputs:
  create-pull-request:
    title-prefix: "[coding-ai-insight] "
    labels: [automation, coding-ai-insight]
mcp-scripts:
  tech-read-source-list:
    description: "Read RSS source list configuration"
    inputs:
      source_list_path:
        type: string
        required: true
    run: |
      cd "$GITHUB_WORKSPACE"
      echo "{\"source_list_path\": \"$INPUT_SOURCE_LIST_PATH\"}" | python3 Lab-01-Tech-Insights/mcp-scripts/tech_read_source_list.py
  tech-fetch-all-to-disk:
    description: "Fetch all sources to disk in parallel"
    inputs:
      source_list_path:
        type: string
        required: true
      signals_dir:
        type: string
        required: true
      timeout_seconds:
        type: number
        default: 15
      max_chars:
        type: number
        default: 200000
      max_items_per_source:
        type: number
        default: 25
    timeout: 300
    run: |
      cd "$GITHUB_WORKSPACE"
      python3 -c "
      import json, sys
      sys.path.insert(0, 'Lab-01-Tech-Insights/mcp-scripts')
      from tech_insight_tools import tech_fetch_all_to_disk
      result = tech_fetch_all_to_disk(
          source_list_path='$INPUT_SOURCE_LIST_PATH',
          signals_dir='$INPUT_SIGNALS_DIR',
          timeout_seconds=int('${INPUT_TIMEOUT_SECONDS:-15}'),
          max_chars=int('${INPUT_MAX_CHARS:-200000}'),
          max_items_per_source=int('${INPUT_MAX_ITEMS_PER_SOURCE:-25}')
      )
      print(json.dumps(result, ensure_ascii=False, default=str))
      "
  tech-load-articles-from-disk:
    description: "Load and filter valid articles from disk"
    inputs:
      signals_dir:
        type: string
        required: true
      source_list_path:
        type: string
        required: true
      max_items_per_source:
        type: number
        default: 25
      time_window_hours:
        type: number
        default: 24
    run: |
      cd "$GITHUB_WORKSPACE"
      python3 -c "
      import json, sys
      sys.path.insert(0, 'Lab-01-Tech-Insights/mcp-scripts')
      from tech_insight_tools import tech_load_articles_from_disk
      result = tech_load_articles_from_disk(
          signals_dir='$INPUT_SIGNALS_DIR',
          source_list_path='$INPUT_SOURCE_LIST_PATH',
          max_items_per_source=int('${INPUT_MAX_ITEMS_PER_SOURCE:-25}'),
          time_window_hours=int('${INPUT_TIME_WINDOW_HOURS:-24}')
      )
      print(json.dumps(result, ensure_ascii=False, default=str))
      "
  tech-cluster-or-fallback:
    description: "Validate and fallback clustering results"
    inputs:
      raw_signals_json:
        type: string
        required: true
      clusters_json:
        type: string
        required: true
      top_k:
        type: number
        default: 12
    run: |
      cd "$GITHUB_WORKSPACE"
      echo "{\"raw_signals_json\": $(echo $INPUT_RAW_SIGNALS_JSON | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"clusters_json\": $(echo $INPUT_CLUSTERS_JSON | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"top_k\": ${INPUT_TOP_K:-12}}" | python3 Lab-01-Tech-Insights/mcp-scripts/tech_cluster_or_fallback.py
  tech-insight-or-fallback:
    description: "Validate and fallback insight results"
    inputs:
      clusters_json:
        type: string
        required: true
      insights_json:
        type: string
        required: true
    run: |
      cd "$GITHUB_WORKSPACE"
      echo "{\"clusters_json\": $(echo $INPUT_CLUSTERS_JSON | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"insights_json\": $(echo $INPUT_INSIGHTS_JSON | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))') }" | python3 Lab-01-Tech-Insights/mcp-scripts/tech_insight_or_fallback.py
  tech-render-report-or-fallback:
    description: "Validate and fallback report rendering"
    inputs:
      clusters_json:
        type: string
        required: true
      insights_json:
        type: string
        required: true
      draft_markdown:
        type: string
        required: true
    run: |
      cd "$GITHUB_WORKSPACE"
      echo "{\"clusters_json\": $(echo $INPUT_CLUSTERS_JSON | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"insights_json\": $(echo $INPUT_INSIGHTS_JSON | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"draft_markdown\": $(echo $INPUT_DRAFT_MARKDOWN | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')}" | python3 Lab-01-Tech-Insights/mcp-scripts/tech_render_report_or_fallback.py
  write-text-file:
    description: "Write text content to a file"
    inputs:
      path:
        type: string
        required: true
      text:
        type: string
        required: true
      overwrite:
        type: boolean
        default: true
    run: |
      cd "$GITHUB_WORKSPACE"
      echo "{\"path\": \"$INPUT_PATH\", \"text\": $(echo $INPUT_TEXT | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"overwrite\": ${INPUT_OVERWRITE:-true}}" | python3 Lab-01-Tech-Insights/mcp-scripts/write_text_file.py
---

# Coding AI Market Insights Workflow

Goal: run the Lab-01 coding AI insights pipeline from repository-relative paths. Aggregate market, product, and developer-workflow updates about coding AI assistants, coding agents, AI-native IDEs, code review automation, model updates for software engineering, MCP/tool-use ecosystems, and enterprise governance. The workflow is manual only; do not add `schedule` or any other trigger.

Default configuration:

- `source_list_path`: `Lab-01-Tech-Insights/input/api/rss_list.json`
- `signals_dir`: `Lab-01-Tech-Insights/output/signals`
- `output_dir`: `Lab-01-Tech-Insights/output`
- `time_window_hours`: `24`
- `top_k`: `12`
- `max_items_per_source`: `25`
- `timeout_seconds`: `15`
- `max_chars`: `200000`

Execution constraints:

- Use repository-relative paths throughout; do not write absolute paths.
- Focus only on coding AI and developer-tooling updates: coding assistants, repository agents, AI IDEs, code review, software engineering workflows, model releases relevant to code, MCP/tool use, security, governance, and enterprise adoption.
- All model-facing prompts and generated reports must be in English.
- Key intermediate artifacts must be written to disk: `raw_signals.json`, `clusters/hotspots.json`, `insights/insights.json`, and `report.md`.
- In addition to writing `Lab-01-Tech-Insights/output/report.md`, write the same Markdown to `Lab-01-Tech-Insights/frontend/report.md` for the static frontend.

## Phase 1: Fetch and Load Raw Signals

1. Call `tech.read_source_list(source_list_path)` and confirm the source list is usable.
2. Call `tech.fetch_all_to_disk(source_list_path, signals_dir, timeout_seconds=15, max_chars=200000, max_items_per_source=25)` to fetch all sources into `signals_dir`.
3. Call `tech.load_articles_from_disk(signals_dir, source_list_path, max_items_per_source=25, time_window_hours=24)` to produce raw signals JSON.
4. Use the `edit` tool to write the raw signals JSON to `Lab-01-Tech-Insights/output/raw_signals.json`.
5. Briefly report the source list path, fetch directory, time window, and raw signal output path.
6. If any tool reports fallback behavior, mention it.

## Phase 2: Cluster Trends and High-Signal Updates

1. Based on Phase 1 raw signals, construct the clustering request from this English prompt, replacing placeholders with actual values and JSON:

```text
You are a coding AI market clustering agent.
Task: aggregate article signals from the past {Local.TimeWindowHours} hours into actionable coding AI themes and updates.

## Input (strict JSON)
{MessageText(Local.RawSignals)}

## Clustering principles
- First use structured metadata buckets: signal_level, source_type, platform, tracks, and source company.
- Then merge related items by topic using title, summary, URL domain, vendor/product names, and technical theme.
- Identify relevant vendors/products when possible, such as OpenAI Codex, GitHub Copilot, Claude Code, Cursor, Hugging Face, Sourcegraph Cody, Windsurf, JetBrains AI, VS Code, MCP, or model families. Store them in coverage.companies for compatibility with the downstream schema.
- Keep two output categories:
  1) cross_source_trends: multi-source themes with strong coverage
  2) high_signal_singles: single-source but important updates from official sources, changelogs, product releases, model releases, security/governance updates, or engineering case studies

## Hard constraints
- Output strict JSON only; no code fences or explanation.
- Each hotspot must include samples; trends should include at least 3 samples when available, singles may include 1-2.
- Return at most {Local.TopK} hotspots.

## Output format (strict JSON)
{"hotspots": [{"hotspot_id": "H01", "title": "...", "summary": "...", "category": "trend|single", "overall_heat_score": 0, "coverage": {"source_count": 0, "companies": [], "platforms": []}, "should_chase": "yes|no", "chase_rationale": [], "samples": [{"platform": "...", "title": "...", "url": "...", "published_at": "...", "company": "...", "signal_level": "..."}]}]}
```

2. Pass the model-generated cluster candidate to `tech.cluster_or_fallback(raw_signals_json, clusters_json, top_k=12)` for validation and fallback.
3. Use the `edit` tool to write the final cluster JSON to `Lab-01-Tech-Insights/output/clusters/hotspots.json`.
4. Summarize the main `cross_source_trends` and `high_signal_singles`.
5. If fallback was used, mention it.

## Phase 3: Generate Hotspot Insights

1. Based on Phase 2 clusters, construct the insight request from this English prompt, replacing placeholders with actual JSON:

```text
You are a coding AI market insights agent.
Task: for each hotspot, explain what changed, why it matters, who is impacted, what to do next, and what risks to watch. Analyze from the perspective of software engineering teams, developer experience leaders, platform/security teams, and tool buyers.

## Input: hotspot clusters (strict JSON)
{MessageText(Local.HotspotClusters)}

## Output (strict JSON)
{"insights": [{"hotspot_id": "H01", "title": "...", "what_changed": "...", "why_it_matters": "...", "who_is_impacted": [], "next_actions": [], "risk_notes": [], "references": []}]}
```

2. Pass the model-generated insight candidate to `tech.insight_or_fallback(clusters_json, insights_json)` for validation and fallback.
3. Use the `edit` tool to write the final insight JSON to `Lab-01-Tech-Insights/output/insights/insights.json`.
4. Cover the four dimensions: what changed, why it matters, who is impacted, and what to do next.
5. If fallback was used, mention it.

## Phase 4: Generate and Submit Markdown Report

1. Based on Phase 2 clusters and Phase 3 insights, construct the report request from this English prompt, replacing placeholders with actual JSON:

```text
You are a coding AI market report writer.
Generate a polished English Markdown report from the clusters and insights. Keep the same format as the sample frontend report and include:

- Market Summary: key updates from the past 24 hours
- Cross-Source Trends: multi-source coding AI themes
- Important Single-Source Updates: official or high-signal single-source updates
- Company Competition Radar: vendor/product activity grouped by company or tool
- New Products and Capability Releases: model, agent, IDE, review, MCP, or workflow capabilities
- Adoption and Policy: enterprise adoption, governance, privacy, security, and procurement signals
- Technical Research: model capability, evaluation, security, sandboxing, code quality, and engineering practice

## Input: clusters (JSON)
{MessageText(Local.HotspotClusters)}

## Input: insights (JSON)
{MessageText(Local.HotspotInsights)}

Output Markdown only. Do not use a code block.
```

2. Pass the model-generated Markdown draft to `tech.render_report_or_fallback(clusters_json, insights_json, draft_markdown)` for validation and fallback.
3. Use the `edit` tool to write the final Markdown to `Lab-01-Tech-Insights/output/report.md`.
4. Use the `edit` tool to write the same Markdown to `Lab-01-Tech-Insights/frontend/report.md`.
5. Use safe-outputs `create-pull-request` to submit a PR containing `Lab-01-Tech-Insights/output/report.md` and `Lab-01-Tech-Insights/frontend/report.md`. The PR title should include the date and a short report summary. Do not introduce a manual git workflow.
6. Final summary must include the report output path, frontend sync path, and PR number.
7. If fallback was used, mention it.

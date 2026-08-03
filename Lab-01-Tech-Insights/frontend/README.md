# Frontend (GitHub Pages)

This is a minimal static report viewer. It renders `report.md` as readable HTML in the browser.

## Local Preview

Run this from the repository root:

```bash
python3 -m http.server 8000 --directory Lab-01-Tech-Insights/frontend
```

Then open `http://localhost:8000`.

Opening `index.html` directly may fail in some browsers because `fetch(report.md)` can be blocked by local-file cross-origin rules.

## Usage

- Default rendered file: `report.md` in the same directory as `index.html`

## Deploy to GitHub Pages

This repository deploys with GitHub Pages and does not need a separate cloud service.

1. Open the repository **Settings -> Pages**.
2. Set **Source** to **GitHub Actions**.
3. Run the `Deploy GitHub Pages` workflow.

`deploy-pages.yml` also deploys automatically when files under `Lab-01-Tech-Insights/frontend/` change on `main`.

The Coding AI Insight workflow writes the latest Markdown report to `Lab-01-Tech-Insights/frontend/report.md`, which triggers a Pages refresh after the report PR is merged.

# Prerequisites

Software and accounts required to run the coding AI insights lab.

## Accounts

| Account | Purpose | Labs |
|---------|---------|------|
| GitHub | Host the gh-aw workflow and GitHub Actions runs | Lab-01 |
| DeepSeek with API balance | Provide the API key and model calls for the workflow | Lab-01 |

## Software

| Software | Minimum Version | Labs | Install |
|----------|-----------------|------|---------|
| Git | 2.x | All | https://git-scm.com |
| GitHub CLI (`gh`) | 2.x | All | https://cli.github.com |
| gh-aw extension | latest | Lab-01 | `gh extension install github/gh-aw` |
| Python | 3.11+ | All | https://www.python.org |
| Node.js | 24+ | All | https://nodejs.org |
| VS Code | latest | All, recommended | https://code.visualstudio.com |

## Quick Verification

```bash
git --version          # >= 2.x
gh --version           # >= 2.x
gh aw --version        # installed
python3 --version      # >= 3.11
node --version         # >= 24
code --version         # installed, optional
```

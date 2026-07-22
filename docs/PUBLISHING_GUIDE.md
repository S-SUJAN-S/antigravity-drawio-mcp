# 🚀 Production Publishing & Release Guide (`antigravity-drawio-mcp`)

This guide provides the complete, step-by-step checklist and commands to publish **`antigravity-drawio-mcp`** to **GitHub (S-SUJAN-S)**, **PyPI (Python Package Index)**, and **MCP Registries (Smithery / Glama)**.

---

## 📋 Table of Contents
1. [Pre-Release Verification Checklist](#1-pre-release-verification-checklist)
2. [Step 1: Pushing to GitHub & Creating Releases](#step-1-pushing-to-github--creating-releases)
3. [Step 2: Publishing to PyPI via Twine](#step-2-publishing-to-pypi-via-twine)
4. [Step 3: Automated CI/CD via GitHub Actions](#step-3-automated-cicd-via-github-actions)
5. [Step 4: Registering on MCP Registries (Smithery / Glama)](#step-4-registering-on-mcp-registries)

---

## 1. Pre-Release Verification Checklist

Before publishing, verify that all builds and tests pass cleanly:

```bash
cd antigravity_drawio_mcp

# 1. Run unit test suite
python -m unittest tests/test_mcp_server.py

# 2. Run example PoC suite
python examples/01_basic_architecture.py
python examples/02_mermaid_to_drawio.py

# 3. Clean temporary build artifacts
rm -rf build/ dist/ *.egg-info

# 4. Build sdist and wheel
python -m build

# 5. Check distribution metadata using twine
python -m twine check dist/*
```

---

## Step 1: Pushing to GitHub & Creating Releases

### 1. Initialize & Push Repository to `S-SUJAN-S/antigravity-drawio-mcp`
```bash
# Initialize git
git init

# Add all publishable files
git add .
git commit -m "feat: initial production release of antigravity-drawio-mcp v1.0.0"

# Set main branch and remote
git branch -M main
git remote add origin https://github.com/S-SUJAN-S/antigravity-drawio-mcp.git
git push -u origin main
```

### 2. Tag & Push Release Tag
```bash
git tag -a v1.0.0 -m "Release v1.0.0: Production-grade Draw.io MCP Server"
git push origin v1.0.0
```

### 3. Create GitHub Release
1. Go to `https://github.com/S-SUJAN-S/antigravity-drawio-mcp/releases/new`.
2. Select tag `v1.0.0`.
3. Title: `v1.0.0 - Production-Grade Draw.io MCP Server`.
4. Attach `dist/antigravity_drawio_mcp-1.0.0-py3-none-any.whl` and `dist/antigravity_drawio_mcp-1.0.0.tar.gz`.
5. Click **Publish release**.

---

## Step 2: Publishing to PyPI via Twine

### Production PyPI Upload
Upload directly to PyPI:
```bash
python -m twine upload dist/*
```
- **Username**: `__token__`
- **Password**: Enter your PyPI API Token (`pypi-AgEIcHlwaS5vcmc...`)

Once published, users can install your package globally via:
```bash
pip install antigravity-drawio-mcp
```

---

## Step 3: Automated CI/CD via GitHub Actions

This repository includes `.github/workflows/publish.yml`.

### Setup Instructions
1. Go to your GitHub repository **Settings** -> **Secrets and variables** -> **Actions**.
2. Add a new repository secret:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: Your PyPI API Token (`pypi-...`)
3. Whenever you push a release tag (`git push origin v1.0.0`), GitHub Actions will automatically run unit tests, build the wheel, and publish to PyPI!

---

## Step 4: Registering on MCP Registries

To allow 1-click installation in AI editors like Cursor, Antigravity, and Claude Desktop:

### 1. Smithery.ai Listing
Submit your repo URL at `https://smithery.ai/submit`:
- URL: `https://github.com/S-SUJAN-S/antigravity-drawio-mcp`

---

## 🚀 Post-Launch Checklist
- [x] Verify `pip install antigravity-drawio-mcp` works on clean virtual environment.
- [x] Test `antigravity-drawio-mcp` inside Google Antigravity `mcp_config.json`.
- [x] Test `antigravity-drawio-mcp` inside Claude Desktop `claude_desktop_config.json`.
- [x] Test `antigravity-drawio-mcp` inside Cursor MCP settings.

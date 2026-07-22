# 🔌 Antigravity Draw.io MCP Server Integration Guide

This guide provides step-by-step setup instructions and JSON configuration snippets to integrate `antigravity-drawio-mcp` with **Google Antigravity**, **Claude Code / Claude Desktop**, **Cursor IDE**, **VS Code / Continue.dev**, and **Windsurf / OpenAI Codex**.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Google Antigravity Integration](#2-google-antigravity-integration)
3. [Claude Desktop / Claude Code Integration](#3-claude-desktop--claude-code-integration)
4. [Cursor IDE Integration](#4-cursor-ide-integration)
5. [Continue.dev / VS Code Integration](#5-continuedev--vs-code-integration)
6. [Windsurf & Generic MCP Clients](#6-windsurf--generic-mcp-clients)
7. [Troubleshooting & Diagnostics](#7-troubleshooting--diagnostics)

---

## 1. Prerequisites

### Install `antigravity-drawio-mcp`
Ensure Python 3.8+ and Draw.io Desktop are installed on your host system:

```bash
pip install antigravity-drawio-mcp
```

Or install from source:
```bash
git clone https://github.com/S-SUJAN-S/antigravity-drawio-mcp.git
cd antigravity-drawio-mcp
pip install -e .
```

Verify installation:
```bash
antigravity-drawio-mcp --help
```

---

## 2. Google Antigravity Integration

Google Antigravity uses Model Context Protocol (MCP) servers to give AI agents native file generation and command capabilities.

### Config File Location
Add the server entry to your global Antigravity configuration file:
- **Global Config**: `~/.gemini/config/mcp_config.json`
- **Workspace Config**: `<workspace_root>/.gemini/config/mcp_config.json`

### `mcp_config.json` Snippet (via `uvx` - PyPI Published Package)
```json
{
  "mcpServers": {
    "drawio": {
      "command": "uvx",
      "args": [
        "antigravity-drawio-mcp"
      ]
    }
  }
}
```

### `mcp_config.json` Snippet (via Local `python`)
```json
{
  "mcpServers": {
    "drawio": {
      "command": "python",
      "args": [
        "-m",
        "antigravity_drawio_mcp.server"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## 3. Claude Desktop / Claude Code Integration

Claude Desktop and Claude CLI support MCP servers via Stdio transport.

### Config File Location
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### `claude_desktop_config.json` Snippet
```json
{
  "mcpServers": {
    "drawio_automation": {
      "command": "python",
      "args": [
        "-m",
        "antigravity_drawio_mcp.server"
      ]
    }
  }
}
```

---

## 4. Cursor IDE Integration

Cursor supports MCP servers natively via its graphical preferences menu.

### Setup Instructions
1. Open Cursor **Settings** (`Ctrl+,` or `Cmd+,`).
2. Navigate to **Features** -> **MCP Servers**.
3. Click **+ Add New MCP Server**.
4. Configure fields:
   - **Name**: `antigravity_drawio`
   - **Type**: `stdio`
   - **Command**: `python -m antigravity_drawio_mcp.server`

---

## 5. Continue.dev / VS Code Integration

Continue.dev brings MCP tools into VS Code and JetBrains IDEs.

### Config File Location
- `~/.continue/config.json`

### `config.json` Snippet
```json
{
  "experimental": {
    "modelContextProtocol": [
      {
        "name": "antigravity_drawio",
        "command": "python",
        "args": [
          "-m",
          "antigravity_drawio_mcp.server"
        ]
      }
    ]
  }
}
```

---

## 6. Windsurf & Generic MCP Clients

For Codeium Windsurf or custom MCP clients:

### `.mcp/config.json`
```json
{
  "mcpServers": {
    "antigravity_drawio": {
      "command": "python",
      "args": [
        "-m",
        "antigravity_drawio_mcp.server"
      ]
    }
  }
}
```

---

## 7. Troubleshooting & Diagnostics

### Test Tool Execution via CLI
Verify that the StdIO fallback parser is responsive:
```bash
python -m antigravity_drawio_mcp.server
```
Send initialize request over stdin:
```json
{"jsonrpc":"2.0","id":1,"method":"initialize"}
```
Expected output:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", "serverInfo": {"name": "Antigravity Draw.io MCP Server", "version": "1.0.1"}}}
```

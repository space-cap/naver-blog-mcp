# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Communication Guidelines

**IMPORTANT**: Always respond in Korean (한글) when communicating with users in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server implementation for Naver Blog integration. The project uses Python 3.13 and the `mcp[cli]` package (v1.20.0+).

## Development Setup

This project uses `uv` for Python package management:

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows

# Run the main script
python main.py
```

## Project Structure

- `main.py` - Main entry point (currently a placeholder)
- `pyproject.toml` - Project dependencies and metadata
- `uv.lock` - Locked dependency versions managed by uv

## Architecture Notes

The project is in its initial setup phase. Once implemented, this will be an MCP server that should:
- Implement MCP protocol handlers for Naver Blog operations
- Follow the MCP SDK patterns from the `mcp` package
- Likely expose tools/resources/prompts through the MCP interface

When implementing MCP server functionality:
- Use the `mcp.server` module for server setup
- Define tools using `@server.tool()` decorators
- Define resources using `@server.resource()` decorators
- Handle async operations properly as MCP servers are typically async

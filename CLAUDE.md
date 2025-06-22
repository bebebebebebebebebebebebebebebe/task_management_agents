# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conversation Guidelines
- 常に日本語で会話する

## Commands

### Development
- **Install dependencies**: `uv sync`
- **Run tests**: `pytest` (configured with coverage reporting)
- **Lint code**: `ruff check src tests`
- **Format code**: `ruff format src tests`
- **Run single test**: `pytest tests/path/to/test_*.py::TestClass::test_method`

### Application Entry Points
- **Business requirement agent**: `biz-requirement-agent` (via pyproject.toml script)
- **Task management agents**: `task-management-agents` (via pyproject.toml script)

## Architecture

### Core Framework
This project uses **LangGraph** for building AI agent workflows with state management. All agents extend the `AgentGraphBuilder` abstract base class located in `src/agents/core/agent_builder.py`.

### Agent Structure
- **State Management**: Uses Pydantic models for type-safe state handling
- **Graph Building**: Each agent implements `build_graph()` returning a `CompiledGraph`
- **Visualization**: Built-in `draw_mermaid_graph()` method for workflow visualization

### Business Requirement Agent
Located in `src/agents/biz_requirement/`, this agent follows a multi-phase workflow:
1. **Introduction**: Initial user greeting and setup
2. **Interview**: Interactive requirements gathering using predefined question templates
3. **Outline Generation**: Dynamic document structure creation
4. **Detail Generation**: Parallel content generation for each section
5. **Document Integration**: Final markdown document assembly

Key features:
- Non-technical user-friendly question templates in `QUESTION_TEMPLATES`
- Mandatory vs optional requirement fields (`MANDATORY`/`OPTIONAL`)
- Specialized schemas for business requirements in `schemas.py`
- Output documents saved to `outputs/` directory

### Configuration
- Environment variables managed through `src/common/config.py` using Pydantic Settings
- Supports Google GenAI, OpenAI, LangSmith, and Tavily API keys
- JSON logging format via `src/utils/logger.py`

### MCP (Model Context Protocol) Integration
- **MCP Configuration**: `.mcp.json` file configures MCP servers for enhanced functionality
- **LangSmith MCP Server**: Provides tracing, monitoring, and dataset management capabilities
  - Command: `uvx langsmith-mcp-server`
  - Requires `LANGSMITH_API_KEY` environment variable
- **GitHub MCP Server**: Enables direct GitHub operations via Docker
  - Command: `docker run ghcr.io/github/github-mcp-server`
  - Requires `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable
  - **IMPORTANT**: All GitHub operations (PR creation, issue management, repository operations, etc.) should use the GitHub MCP Server instead of CLI commands
- **LangSmith Integration**: Automatic trace logging and project monitoring for agent workflows

### Testing
- Uses pytest with async support and coverage reporting
- Tests located in `tests/` directory matching source structure
- Test configuration in `pyproject.toml` includes `pythonpath = "./src"`

### Code Style
- Ruff for linting and formatting (line length: 135)
- Single quotes preferred for strings
- Space indentation
- Specific lint rules configured (excludes F401, E501, S101)

## Development Philosophy

### Test-Driven Development (TDD)
- 原則としてテスト駆動開発（TDD）で進める
- 期待される入出力に基づき、まずテストを作成する
- 実装コードは書かず、テストのみを用意する
- テストを実行し、失敗を確認する
- テストが正しいことを確認できた段階でコミットする
- その後、テストをパスさせる実装を進める
- 実装中はテストを変更せず、コードを修正し続ける
- すべてのテストが通過するまで繰り返す

### Pre-commit Requirements
- **MANDATORY**: コミット前に必ずテストとリントを実行する
  - `pytest` - すべてのテストが通過することを確認
  - `ruff check src tests` - リント検査をパス
  - `ruff format src tests` - コードフォーマットを適用
- テストまたはリントが失敗した場合は、修正してから再実行
- すべてのチェックが通過した後にのみコミットを行う

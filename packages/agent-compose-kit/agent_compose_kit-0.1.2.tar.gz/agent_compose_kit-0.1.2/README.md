Template Agent Builder (Core)
================================

![CI](https://github.com/DeadMeme5441/agent-compose-kit/actions/workflows/ci.yml/badge.svg)
![Publish](https://github.com/DeadMeme5441/agent-compose-kit/actions/workflows/publish.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/agent-compose-kit.svg)](https://pypi.org/project/agent-compose-kit/)
[![Python Versions](https://img.shields.io/pypi/pyversions/agent-compose-kit.svg)](https://pypi.org/project/agent-compose-kit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Core Python library for YAML-driven construction of agent systems using Google ADK. This package provides configuration models, service factories, agent and tool builders, registries, runtime utilities, and a thin server wrapper. It is designed to be consumed by external clients (CLI or web) that handle end-user interaction. No CLI or TUI is included in this repo.

Features
- Config schema (Pydantic) with environment interpolation and provider defaults.
- Services (conservative defaults):
  - Sessions: in-memory (default), Redis, Mongo, Database (SQLAlchemy URL).
  - Artifacts: in-memory (default), Local folder, S3, GCS.
  - Memory: in-memory (default), Vertex AI (falls back to in-memory if missing params).
- Agents: direct model IDs (Gemini/Vertex) or LiteLLM models (OpenAI, Anthropic, Ollama, vLLM), function tools, sub-agent wiring.
- Workflows: sequential, parallel, loop composition.
- Runtime: map YAML runtime to ADK RunConfig; build ADK Runner instances.
- Public API for external CLIs: system/session helpers, run helpers, env-based path helpers.

Design notes
- Conservative by default: when required service parameters are not provided, factories fall back to in-memory implementations (never attempt network/local resources silently).
- Provider defaults: `model_providers` merge into LiteLLM configs (e.g., OpenAI keys, API base) without overwriting explicit values.

Tools
- Function tools: `{type: function, ref: "module:callable", name?}`. The callable must be Python; for cross-language tools use MCP/OpenAPI below.
- MCP toolsets: connect to MCP servers via stdio/SSE/HTTP and expose their tools to agents.
- OpenAPI toolsets: generate `RestApiTool`s from an OpenAPI spec (inline/path); agents can call REST APIs directly.
- Shared toolsets: define once under `toolsets:` and reference from agents with `{use: name}`.

YAML Examples (Tools)
```yaml
toolsets:
  # Reusable MCP toolset via stdio (requires `mcp` package installed)
  fs_tools:
    type: mcp
    mode: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "./sandbox"]
    tool_filter: [list_directory, read_file]

agents:
  - name: planner
    model: gemini-2.0-flash
    instruction: Use tools when appropriate.
    tools:
      # Function tool (Python callable)
      - {type: function, ref: tests.helpers:sample_tool, name: add}
      # Reuse shared toolset
      - {use: fs_tools}

  - name: api_caller
    model: gemini-2.0-flash
    instruction: Use REST API tools.
    tools:
      - type: openapi
        spec:
          path: ./specs/petstore.yaml  # or inline: "{...}" (json/yaml)
        spec_type: yaml  # json|yaml; inferred from path extension when omitted
        tool_filter: []
```

Requirements
- Python 3.12+
- Optional extras at runtime depending on backends:
  - google-adk, adk-extra-services, litellm
  - For MCP stdio mode: `mcp` package (and any server requirements)

Install (dev)
- uv sync

Quickstart (Programmatic)
```python
from pathlib import Path
from agent_compose_kit.config.models import load_config_file
from agent_compose_kit.services.factory import build_session_service, build_artifact_service, build_memory_service
from agent_compose_kit.agents.builder import build_agents
from agent_compose_kit.runtime.supervisor import build_plan, build_run_config

cfg = load_config_file(Path("configs/app.yaml"))
print(build_plan(cfg))

artifact_svc = build_artifact_service(cfg.artifact_service)
session_svc = build_session_service(cfg.session_service)
memory_svc = build_memory_service(cfg.memory_service)

agents = build_agents(cfg.agents, provider_defaults=cfg.model_providers)
root = agents[cfg.workflow.nodes[0]] if (cfg.workflow and cfg.workflow.nodes) else agents[cfg.agents[0].name]

from google.adk.runners import Runner
runner = Runner(app_name="template-agent-builder", agent=root, artifact_service=artifact_svc, session_service=session_svc, memory_service=memory_svc)
rc = build_run_config(cfg)
# Use runner in your application according to ADK docs
```

Registries (Tools & Agents)
- Define reusable tools and agents in your config, then build registries:
```python
from pathlib import Path
from agent_compose_kit.config.models import load_config_file
from agent_compose_kit.tools.builders import build_tool_registry_from_config
from agent_compose_kit.agents.builders_registry import build_agent_registry_from_config

cfg = load_config_file(Path("configs/app.yaml"))
tool_reg = build_tool_registry_from_config(cfg, base_dir=".")
agent_reg = build_agent_registry_from_config(cfg, base_dir=".", provider_defaults=cfg.model_providers, tool_registry=tool_reg)

root = agent_reg.get("parent")  # or agent_reg.get_group("core")[0]
```

Public API (for external CLI)
- Build a system and run a message:
```python
from pathlib import Path
from agent_compose_kit.api.public import SystemManager, SessionManager, run_text, event_to_minimal_json

sm = SystemManager(base_dir=Path("./systems/my_system"))
cfg = sm.load("config.yaml")
runner, _resources = sm.build_runner(cfg)

import asyncio

async def main():
    sess = await SessionManager(runner).get_or_create(user_id="u1")
    async for ev in run_text(runner=runner, user_id="u1", session_id=sess.id, text="hello"):
        print(event_to_minimal_json(ev))

asyncio.run(main())
```

Environment variables (optional)
- `AGENT_SYS_DIR`: root directory where systems live (default `./systems`).
- `AGENT_OUTPUTS_DIR`: root directory for outputs/artifacts (default `./outputs`).
- `AGENT_SESSIONS_URI`: default sessions storage URI (default `sqlite:///./sessions.db`).

Serve as API (ADK FastAPI)
- Generate an ADK wrapper module so `adk run`/`adk web` can load your root agent:
```python
from pathlib import Path
from agent_compose_kit.serve.scaffold import write_adk_wrapper, write_fastapi_app_py, write_docker_scaffold

agents_dir = Path("./agents"); agents_dir.mkdir(exist_ok=True)
write_adk_wrapper(agents_dir=agents_dir, system_name="my_system", config_path=Path("configs/app.yaml"), package_import="src", copy_config=True)
write_fastapi_app_py(output_dir=Path("."), agents_dir=agents_dir)
```
- Run the API locally:
  - `uvicorn app:app --host 0.0.0.0 --port 8000`
  - Or use ADK directly: `adk run agents/my_system` (interactive) or start FastAPI via ADK CLI.
- Containerize (optional):
  - `write_docker_scaffold(output_dir=Path("."), dist_name="agent-compose-kit")`
  - `docker build -t my-system . && docker run -p 8000:8000 my-system`

YAML Example
```yaml
services:
  session_service: {type: in_memory}
  artifact_service: {type: local_folder, base_path: ./artifacts_storage}

agents:
  - name: planner
    model: gemini-2.0-flash
    instruction: You are a helpful planner.
    tools: []

workflow:
  type: sequential
  nodes: [planner]

runtime:
  streaming_mode: NONE
  max_llm_calls: 200
```

Testing
- Run all tests: `uv run --with pytest pytest -q`
- Current coverage includes config/env interpolation, service factories (with in-memory fallbacks), function tool loading, workflow composition, and RunConfig mapping.
- Cloud-backed integrations (e.g., GCS) are skipped unless credentials are configured.

Development
- Lint: `uv run --with ruff ruff check .`
- Format: `uv run --with ruff ruff format .`
- Tests: `uv run --with pytest pytest -q`

Project Structure
- `src/config/models.py` — Pydantic models, env interpolation, example writer.
- `src/services/factory.py` — session/artifact/memory service builders.
- `src/agents/builder.py` — model resolution (string/LiteLLM), function tools, sub-agent wiring.
- `src/tools/loader.py` — unified loader for function/MCP/OpenAPI tools and shared toolsets.
- `src/tools/registry.py` — global ToolRegistry (ids, groups, caching, close_all).
- `src/agents/registry.py` — global AgentRegistry (ids, groups, sub-agent wiring).
- `src/agents/builders_registry.py` — helpers to build AgentRegistry from AppConfig.
- `src/tools/builders.py` — helpers to build ToolRegistry from AppConfig.
- `src/registry/fs.py` — filesystem helpers for saving/loading systems.
 - `src/api/public.py` — public API for external CLIs (SystemManager, SessionManager, run helpers).
 - `src/paths.py` — path/env helpers (AGENT_SYS_DIR, AGENT_OUTPUTS_DIR, AGENT_SESSIONS_URI).

Schema & Registry
- Export AppConfig JSON schema programmatically:
  - `from agent_compose_kit.config.models import export_app_config_schema`
- Save/load system configs:
  - `from agent_compose_kit.registry.fs import save_system, load_system, list_systems, list_versions, promote`
- `src/runtime/supervisor.py` — plan summary, Runner construction, RunConfig mapping.
- `templates/app.yaml` — example config template.

Roadmap
- See `FULL_IMPLEMENTATION_PLAN.md` for detailed milestones (MCP/OpenAPI toolsets, JSON Schema export, registry helpers, observability hooks).

License
MIT

Publishing plan (summary)
- Finalize metadata in `pyproject.toml`: project name, description, license, classifiers, homepage/repo URLs, keywords.
- Optional extras: define `[project.optional-dependencies]` for `web` (fastapi, uvicorn), `tools` (mcp, openapi), and `dev` (ruff, pytest).
- Versioning: adopt SemVer; tag releases in VCS (e.g., v0.1.0).
- Build: `python -m build` (ensure `build` in dev deps) or `uv build`.
- Publish: `twine upload dist/*` (or GitHub Actions workflow for publish-on-tag).
- Docs: keep README as long_description; ensure `README.md` renders on PyPI.
- CI: add GitHub Actions for lint/test on PR; optional publish job on tag.

# USF Agents SDK (Python)

Production-grade, OpenAI-compatible agents SDK for planning, tool execution, and multi‑agent orchestration on the official USF Agent APIs. Built for developers who need control, visibility, and reliability across simple to complex use cases.

- Docs: https://agents-docs.us.inc
- PyPI: https://pypi.org/project/usf-agents/

--------------------------------------------------------------------------------

## Overview

USF Agents is a lightweight multi-agent orchestration SDK that streamlines:
- Planning → tool execution → final answers with predictable policies
- Tool schema definition from docstrings or YAML (no verbose JSON required)
- Sub-agent composition (manager + sub‑agents) in a few lines
- Tracing and visualization for full execution transparency

Who is it for:
- Developers needing a simple, controllable agent runtime with OpenAI-compatible APIs
- Teams that value observability (tracing), predictability, and minimal boilerplate

--------------------------------------------------------------------------------

## Key Features

- Docstring/YAML-driven tool schemas with validation
- `@tool` decorator for defaults or explicit schema
- Batch tool registration and module discovery
- Auto Execution Modes: `disable` | `auto` | `agent` | `tool`
- Multi-agent orchestration (manager + sub-agents)
- Tracing and visualization (Mermaid/Graphviz/JSON)

For details, see the docs:
- Tools overview: https://agents-docs.us.inc/docs/tools/overview
- Decorator: https://agents-docs.us.inc/docs/tools/decorator
- Docstrings: https://agents-docs.us.inc/docs/tools/docstrings
- Explicit schema: https://agents-docs.us.inc/docs/tools/explicit-schema
- Type mapping: https://agents-docs.us.inc/docs/tools/type-mapping
- Batch registration: https://agents-docs.us.inc/docs/tools/batch-registration
- Multi-agent overview: https://agents-docs.us.inc/docs/multi-agent/overview
- Auto Execution Modes: https://agents-docs.us.inc/docs/auto-execution-modes
- Tracing & Visualization: https://agents-docs.us.inc/docs/tracing-visualization

--------------------------------------------------------------------------------

## Advantages

- Developer-friendly: fewer lines, strong defaults, and explicit controls
- Compatibility: works with OpenAI-compatible APIs and multiple providers
- Extensibility: simple tool creation, sub-agent orchestration, registry flows
- Observability: built-in tracing and visualization utilities
- Operational simplicity: minimal setup, predictable behavior, streaming support

--------------------------------------------------------------------------------

## Installation & Requirements

Follow the installation steps as in the docs: https://agents-docs.us.inc/docs/installation

Requirements
- Python 3.9+
- USF API key (set as an environment variable `USF_API_KEY`)

Install the SDK
- pip (recommended):
```bash
pip install usf-agents
```

- uv:
```bash
uv add usf-agents
```

- poetry:
```bash
poetry add usf-agents
```

- pdm:
```bash
pdm add usf-agents
```

Set your API key
- macOS/Linux:
```bash
export USF_API_KEY=YOUR_KEY
```

- Windows PowerShell:
```powershell
$env:USF_API_KEY="YOUR_KEY"
```

- Windows cmd:
```bat
set USF_API_KEY=YOUR_KEY
```

Optional: Virtual environment
```bash
python -m venv .venv
```

- macOS/Linux:
```bash
source .venv/bin/activate
```

- Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

Verify installation
```bash
pip show usf-agents
```

--------------------------------------------------------------------------------

## Examples

Below are exactly two minimal, copy/paste runnable examples. For comprehensive guides and advanced patterns, use the documentation links in the next section.

Example 1 — Minimal agent (hello world)
```python
import os, asyncio
from usf_agents import USFAgent

async def main():
    agent = USFAgent({"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"})
    async for chunk in agent.run("Say 'hello world'"):
        if chunk.get("type") == "final_answer":
            print("Final:", chunk.get("content"))
            break

asyncio.run(main())
```

Example 2 — Minimal tool with @tool
```python
import os, asyncio
from usf_agents.multi_agent.base import ManagerAgent
from usf_agents.runtime.decorators import tool

@tool(name="calc_sum", description="Sum a list of integers")
def calc_sum(numbers: list[int]) -> int:
    return sum(numbers)

async def main():
    mgr = ManagerAgent({
        "id": "mgr",
        "agent_type": "manager",
        "usf_config": {"api_key": os.getenv("USF_API_KEY")}
    })
    # Register the decorated function as a tool (name inherited from decorator)
    mgr.add_function_tool("calc_sum", calc_sum)
    final = await mgr.run_auto(
        [{"role": "user", "content": "Use calc_sum for 10,20,30"}],
        mode="auto"
    )
    print("Final:", final)

asyncio.run(main())
```

## Multi-Agent Delegation (contract)

ManagerAgent exposes sub-agents as tools and can delegate explicitly. The delegate API is intentionally strict to keep the contract simple and predictable.

- Signature (simplified):
  - await mgr.delegate(sub_id, task, policy='inherit_manager_policy', context_param=None, ...)
- Task rules:
  - task must be either a string (preferred) or a dict containing only {'task': '<str>'}.
  - Any extra fields (e.g., 'input', 'metadata', or nested 'context_param') in the task payload are rejected.
- Context passing rules (based on the target sub-agent’s context_mode):
  - NONE: context_param is disallowed.
  - CONTEXT_PARAM: context_param is required and must be a non-empty dict.
  - ALWAYS_FULL / AGENT_DECIDED: context_param is optional; if provided, it must be a dict.

Migration examples
- Bad (will error):
```python
await mgr.delegate("coder", {"task": "function", "input": {"signature": "total_cost(prices: list[float]) -> float"}})
```
- Good:
```python
await mgr.delegate(
    "coder",
    "Implement function: total_cost(prices: list[float]) -> float",
    context_param={"audience": "engineering", "coding_style": "pep8"}  # required for CONTEXT_PARAM mode
)
```

Aliases and description overrides (sub-agent tools)
- add_sub_agent(sub, spec_overrides=None, alias=None)
  - alias sets the composed tool function name for the sub-agent (defaults to agent_{slug(name)} when not provided).
  - spec_overrides can provide a description override for the composed tool surface.
  - If neither the sub-agent nor overrides define a description, composition will raise (by design).

Minimal manager/sub-agent example
```python
import os, asyncio
from usf_agents.multi_agent.base import ManagerAgent, SubAgent

async def main():
    api_key = os.getenv("USF_API_KEY")
    mgr = ManagerAgent({"name": "mgr", "agent_type": "manager", "usf_config": {"api_key": api_key}})

    coder = SubAgent({
        "name": "coder",
        "agent_type": "sub",
        "context_mode": "CONTEXT_PARAM",
        "description": "Generates or refactors code from natural-language specifications.",
        "task_placeholder": "Describe the coding task",
        "usf_config": {"api_key": api_key},
    })
    mgr.add_sub_agent(coder, alias="agent_coder")  # optional alias

    result = await mgr.delegate(
        "coder",
        "Implement function: total_cost(prices: list[float]) -> float",
        context_param={"audience": "engineering", "coding_style": "pep8"}  # required for CONTEXT_PARAM
    )
    print("Delegate result:", result.get("success"), result.get("content"))

asyncio.run(main())
```

--------------------------------------------------------------------------------

## Complete Documentation

Start here
- Intro: https://agents-docs.us.inc/docs/intro
- Installation: https://agents-docs.us.inc/docs/installation

Configuration & execution
- Configuration: https://agents-docs.us.inc/docs/configuration
- Auto Execution Modes: https://agents-docs.us.inc/docs/auto-execution-modes
- Final Response Instruction Controls: https://agents-docs.us.inc/docs/final-response-instruction
- Workflows: https://agents-docs.us.inc/docs/workflows
- Tracing & Visualization: https://agents-docs.us.inc/docs/tracing-visualization

Tools
- Overview: https://agents-docs.us.inc/docs/tools/overview
- Decorator: https://agents-docs.us.inc/docs/tools/decorator
- Docstrings: https://agents-docs.us.inc/docs/tools/docstrings
- Explicit schema: https://agents-docs.us.inc/docs/tools/explicit-schema
- Type mapping: https://agents-docs.us.inc/docs/tools/type-mapping
- Batch registration: https://agents-docs.us.inc/docs/tools/batch-registration

Multi-Agent
- Overview: https://agents-docs.us.inc/docs/multi-agent/overview
- Delegation: https://agents-docs.us.inc/docs/multi-agent/delegation
- Context modes: https://agents-docs.us.inc/docs/multi-agent/context-modes
- Per-sub final response: https://agents-docs.us.inc/docs/multi-agent/per-sub-final-response
- Skip planning when no tools: https://agents-docs.us.inc/docs/multi-agent/skip-planning-no-tools

Registry & troubleshooting
- Registry: https://agents-docs.us.inc/docs/registry
- Troubleshooting / FAQ: https://agents-docs.us.inc/docs/troubleshooting-faq

Jupyter notebook guides
- Currency Converter: https://agents-docs.us.inc/docs/jupyter-notebooks/currency-converter
- Customer Support Triage: https://agents-docs.us.inc/docs/jupyter-notebooks/customer-support-triage
- Email Drafting Assistant: https://agents-docs.us.inc/docs/jupyter-notebooks/email-drafting-assistant
- Planner-Worker Delegation: https://agents-docs.us.inc/docs/jupyter-notebooks/planner-worker-delegation
- Strict JSON Output: https://agents-docs.us.inc/docs/jupyter-notebooks/strict-json-output

--------------------------------------------------------------------------------

## License

License: USF Agents SDK License  
See: ./LICENSE

Summary
- Permitted Use: anyone may use this software for any purpose.
- Restricted Activities: no modification of the code; no commercial use; no creation of competitive products.
- Attribution: retain this license notice and attribute UltraSafe AI Team.

--------------------------------------------------------------------------------

© 2025 UltraSafe AI Team

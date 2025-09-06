import json
import pytest

from usf_agents.multi_agent.base import SubAgent, ManagerAgent
from usf_agents.multi_agent.base import _acollect_final_answer as real_collect


@pytest.mark.asyncio
async def test_any_agent_can_add_sub_agent_and_list_tools():
    # Any agent (including SubAgent) can aggregate other agents as sub-agents (agent-as-tool)
    parent = SubAgent({
        'name': 'parent',
        'agent_type': 'sub',
        'context_mode': 'NONE',
        'description': 'Parent agent',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })
    child = SubAgent({
        'name': 'child',
        'agent_type': 'sub',
        'context_mode': 'NONE',
        'description': 'Child tool',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })

    # Attach child as sub-agent tool to parent
    parent.add_sub_agent(child)

    tools = parent.list_tools()
    assert isinstance(tools, list) and len(tools) >= 1
    # Should include a tool with default name agent_child
    names = []
    for t in tools:
        fn = (t.get('function') or {}).get('name')
        if fn:
            names.append(fn)
    assert 'agent_child' in names


@pytest.mark.asyncio
async def test_manager_delegate_passes_target_composed_tools(monkeypatch):
    # M -> B, and B has sub-agent C.
    # When M delegates to B, B should receive its own composed tools (including C) via options.
    mgr = ManagerAgent({
        'name': 'mgr',
        'agent_type': 'manager',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })
    b = SubAgent({
        'name': 'b',
        'agent_type': 'sub',
        'context_mode': 'AGENT_DECIDED',
        'description': 'B tool',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })
    c = SubAgent({
        'name': 'c',
        'agent_type': 'sub',
        'context_mode': 'NONE',
        'description': 'C tool',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })

    # B has C as its sub-agent
    b.add_sub_agent(c)
    # Manager has B as its sub-agent
    mgr.add_sub_agent(b)

    captured = {}

    async def fake_collect(agent, messages, options=None):
        captured['options'] = options or {}
        # Return a final result to complete delegation
        return {'status': 'final', 'content': 'ok'}

    # Intercept _acollect_final_answer to capture options passed to B
    monkeypatch.setattr("usf_agents.multi_agent.base._acollect_final_answer", fake_collect)

    res = await mgr.delegate(sub_id='b', task='run')
    assert res['success'] is True
    assert captured.get('options') is not None
    tools = captured['options'].get('tools') or []
    assert isinstance(tools, list) and len(tools) >= 1

    # Expect agent_C to be present in the tool list passed to B
    names = []
    for t in tools:
        fn = (t.get('function') or {}).get('name')
        if fn:
            names.append(fn)
    assert 'agent_c' in names

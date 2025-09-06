import asyncio
import pytest

from usf_agents.multi_agent.registry import AgentRegistry
from usf_agents.multi_agent.base import SubAgent, ManagerAgent


def make_agent(name: str, agent_type: str = 'sub'):
    spec = {
        'name': name,
        'agent_type': agent_type,
        'context_mode': 'NONE',
        'usf_config': {
            'api_key': 'DUMMY_KEY',  # Replace with real key for integration tests
            'model': 'usf-mini'
        }
    }
    if agent_type == 'manager':
        return ManagerAgent(spec)
    return SubAgent(spec)


def test_registry_add_and_get():
    reg = AgentRegistry()
    a = make_agent('a')
    b = make_agent('b', agent_type='manager')

    reg.add_agent(a)
    reg.add_agent(b)

    assert reg.has('a')
    assert reg.has('b')

    assert reg.get('a').id == 'a'
    assert reg.get('b').id == 'b'

    with pytest.raises(KeyError):
        reg.get('C')


def test_relations_non_exclusive():
    reg = AgentRegistry()
    a = make_agent('a', agent_type='manager')
    b = make_agent('b')
    c = make_agent('c')

    reg.add_agent(a)
    reg.add_agent(b)
    reg.add_agent(c)

    reg.add_relation('a', 'b')
    reg.add_relation('a', 'c')
    # c is also child of b (non-exclusive)
    reg.add_relation('b', 'c')

    assert set(reg.get_children('a')) == {'b', 'c'}
    assert set(reg.get_children('b')) == {'c'}
    assert set(reg.get_parents('c')) == {'a', 'b'}
    assert reg.get_parents('b') == ['a'] or set(reg.get_parents('b')) == {'a'}


def test_all_agents():
    reg = AgentRegistry()
    for i in range(3):
        reg.add_agent(make_agent(f'x{i}'))
    assert set(reg.all_agents()) == {'x0', 'x1', 'x2'}

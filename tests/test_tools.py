import pytest
import agentpy as ap

from agentpy.tools import AgentpyError


def test_attr_dict():

    ad = ap.AttrDict({'a': 1})
    ad.b = 2

    assert ad.a == 1
    assert ad.b == 2
    assert ad.a == ad['a']
    assert ad.b == ad['b']
    assert ad.__repr__() == "AttrDict {'a': 1, 'b': 2}"
    assert ad._short_repr() == "AttrDict {2 entries}"

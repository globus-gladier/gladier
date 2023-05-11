from gladier.utils.tool_alias import StateSuffixVariablePrefix
from gladier.tests.test_data.gladier_mocks import MockToolWithRequirements


def test_get_flow_input():
    tool = MockToolWithRequirements()
    assert tool.get_flow_input() == {
        'default_var': 'is a thing!',
        'compute_endpoint': 'my_compute_endpoint',
    }


def test_get_required_input():
    tool = MockToolWithRequirements()
    assert tool.get_required_input() == [
        'compute_endpoint', 'required_var',
    ]


def test_alias_get_required_input():
    tool = MockToolWithRequirements(alias='MyAlias', alias_class=StateSuffixVariablePrefix)
    assert tool.get_required_input() == [
        'compute_endpoint', 'my_alias_required_var',
    ]


def test_alias_get_flow_input():
    tool = MockToolWithRequirements(alias='MyAlias', alias_class=StateSuffixVariablePrefix)
    assert tool.get_flow_input() == {
        'compute_endpoint': 'my_compute_endpoint',
        'my_alias_default_var': 'is a thing!'
    }

from gladier.utils.tool_alias import StateSuffixVariablePrefix
from gladier.tests.test_data.gladier_mocks import MockToolWithRequirements


def test_get_flow_input():
    tool = MockToolWithRequirements()
    assert tool.get_flow_input() == {
        'default_var': 'is a thing!',
        'funcx_endpoint_non_compute': 'my_non_compute_endpoint_uuid',
    }


def test_get_required_input():
    tool = MockToolWithRequirements()
    assert tool.get_required_input() == [
        'funcx_endpoint_non_compute', 'required_var',
    ]


def test_alias_get_required_input():
    tool = MockToolWithRequirements(alias='MyAlias', alias_class=StateSuffixVariablePrefix)
    assert tool.get_required_input() == [
        'funcx_endpoint_non_compute', 'my_alias_required_var',
    ]


def test_alias_get_flow_input():
    tool = MockToolWithRequirements(alias='MyAlias', alias_class=StateSuffixVariablePrefix)
    assert tool.get_flow_input() == {
        'funcx_endpoint_non_compute': 'my_non_compute_endpoint_uuid',
        'my_alias_default_var': 'is a thing!'
    }

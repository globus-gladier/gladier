import pytest
from gladier.tests.test_data.gladier_mocks import MockGladierClient


@pytest.mark.skip
def test_get_input():
    pass


def test_run_flow(logged_in):
    cli = MockGladierClient()
    cli.run_flow()


@pytest.mark.skip
def test_progress():
    pass


@pytest.mark.skip
def test_get_status():
    pass


@pytest.mark.skip
def test_get_details():
    pass

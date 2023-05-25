
from globus_compute_sdk.sdk.login_manager.protocol import LoginManagerProtocol
from gladier.managers.compute_login_manager import ComputeLoginManager


def test_compute_login_manager_compliance():
    assert isinstance(ComputeLoginManager(None), LoginManagerProtocol)


from funcx.sdk.login_manager.protocol import LoginManagerProtocol
from gladier.utils.funcx_login_manager import FuncXLoginManager


def test_funcx_login_manager_compliance():
    assert isinstance(FuncXLoginManager(None), LoginManagerProtocol)

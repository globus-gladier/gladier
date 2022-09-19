import pytest
from gladier.managers import CallbackLoginManager
from gladier.exc import AuthException


def test_callback_manager_login():
    clm = CallbackLoginManager({}, callback=lambda x: {y: {} for y in x})
    clm.login(['foo', 'bar'])
    assert list(clm.get_authorizers()) == ['foo', 'bar']


def test_callback_manager_no_callback_set():
    with pytest.raises(AuthException):
        CallbackLoginManager({}, callback=None).login(['foo'])

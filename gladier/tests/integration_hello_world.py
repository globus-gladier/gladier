"""
Integration tests for smoke-testing Gladier.

Run with pytest -xvv integration_hello_world.py
"""

import gladier.tests  # noqa -- Ensures logging is enabled
from gladier.client import GladierClient


def test_hello_gladier():

    class HelloGladier(GladierClient):
        client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
        gladier_tools = [
            'gladier.tools.hello_world.HelloWorld',
        ]
        flow_definition = 'gladier.tools.hello_world.HelloWorld'

    hello_cli = HelloGladier()
    flow = hello_cli.start_flow()
    hello_cli.progress(flow['action_id'])
    details = hello_cli.get_details(flow['action_id'], 'HelloFuncXResult')
    assert details['details']['result']
    assert details['details']['exception'] is None


def test_hello_conversation():
    class HelloConversation(GladierClient):
        client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
        gladier_tools = [
            'gladier.tools.hello_world.HelloConversation',
        ]
        flow_definition = 'gladier.tools.hello_world.HelloConversation'

    hello_cli = HelloConversation()
    flow = hello_cli.start_flow({'input': {'delay': .1}})
    hello_cli.progress(flow['action_id'])
    status = hello_cli.get_status(flow['action_id'])
    assert set(status['details']['output'].keys()) == {'ConversationResult', 'GoodbyeResult',
                                                       'GreetingResult', 'input'}


def test_hello_exception():
    class HelloException(GladierClient):
        client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
        gladier_tools = [
            'gladier.tools.hello_world.HelloException',
        ]
        flow_definition = 'gladier.tools.hello_world.HelloException'

    hello_cli = HelloException()
    flow = hello_cli.start_flow({'input': {'exception_message': 'umm, hello?'}})
    hello_cli.progress(flow['action_id'])
    details = hello_cli.get_details(flow['action_id'], 'HelloExceptionResult')
    assert details['details']['result'] is None
    assert details['details']['exception']

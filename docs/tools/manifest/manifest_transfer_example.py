from pprint import pprint
from gladier.client import GladierClient


class GladierManifestTransfer(GladierClient):
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
    gladier_tools = [
        'gladier.tools.manifest.defaults.ManifestToFuncXTasks',
    ]
    flow_definition = 'gladier.tools.manifest.defaults.ManifestToFuncXTasks'


man_cli = GladierManifestTransfer()
flow = man_cli.start_flow()
man_cli.progress(flow['action_id'])
details = man_cli.get_status(flow['action_id'])
pprint(details)

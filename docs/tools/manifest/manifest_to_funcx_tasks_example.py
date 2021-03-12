from pprint import pprint
from gladier.client import GladierClient


class GladierManifestToFuncXTasks(GladierClient):
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
    gladier_tools = [
        'gladier.tools.manifest.defaults.ManifestToFuncXTasks',
    ]
    flow_definition = 'gladier.tools.manifest.defaults.ManifestToFuncXTasks'


man_cli = GladierManifestToFuncXTasks()
gladier_tutorial_ep = '4b116d3c-1703-4f8f-9f6f-39921e5864df'
manifests_to_tasks_input = {
    'input': {
        'manifest_to_tasks_manifest_id': '22ea05b3-a708-4524-b2c7-b3a635ffb1c3',
        'funcx_endpoint_non_compute': gladier_tutorial_ep,
        'manifest_to_funcx_tasks_funcx_endpoint_compute': gladier_tutorial_ep,
        # 'manifest_to_funcx_tasks_callback_funcx_id': 'your-registered-funcx-uuid-goes-here',
    },
}
flow = man_cli.start_flow(flow_input=manifests_to_tasks_input)
man_cli.progress(flow['action_id'])
details = man_cli.get_status(flow['action_id'])
pprint(details)

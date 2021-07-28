"""
Requires Gladier and Gladier Tools.
pip install gladier gladier-tools
"""
from gladier import GladierBaseClient, generate_flow_definition
from pprint import pprint


@generate_flow_definition
class TarAndTransfer(GladierBaseClient):
    gladier_tools = [
        'gladier_tools.posix.Tar',
        'gladier_tools.globus.Transfer',
    ]


if __name__ == '__main__':
    flow_input = {
        'input': {
            'tar_input': '',
            # Set this to your own funcx endpoint where you want to tar files
            'funcx_endpoint_compute': '',
            # Set this to the globus endpoint where your tarred archive has been created
            'transfer_source_endpoint_id': '',
            # By default, this will transfer the tar file to Globus Tutorial Endpoint 1
            'transfer_destination_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
            'transfer_source_path': '',
            'transfer_destination_path': '',
            'transfer_recursive': False,
        }
    }
    tat = TarAndTransfer()
    pprint(tat.flow_definition)
    flow = tat.run_flow(flow_input=flow_input)
    action_id = flow['action_id']
    tat.progress(action_id)
    pprint(tat.get_status(action_id))

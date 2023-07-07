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
            # The directory below should exist with files. It will be archived by the Tar Tool.
            'tar_input': '~/myfiles',
            # Set this to your own funcx endpoint where you want to tar files
            'compute_endpoint': '',
            # Set this to the globus endpoint where your tarred archive has been created
            # 'transfer_source_endpoint_id': '',
            # By default, this will transfer the tar file to Globus Tutorial Endpoint 1
            'transfer_destination_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
            # By default, the Tar Tool will append '.tgz' to the archive it creates
            'transfer_source_path': '~/myfiles.tgz',
            'transfer_destination_path': '~/my_archives/myfiles.tgz',
            'transfer_recursive': False,
        }
    }
    # Instantiate the client
    tar_and_transfer = TarAndTransfer()

    # Optionally, print the flow definition
    # pprint(tar_and_transfer.flow_definition)

    # Run the flow
    flow = tar_and_transfer.run_flow(flow_input=flow_input, label='Tar and Transfer', tags=['tutorial'])

    # Track the progress
    action_id = flow['action_id']
    tar_and_transfer.progress(action_id)
    pprint(tar_and_transfer.get_status(action_id))

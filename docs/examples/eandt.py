from gladier import GladierBaseClient, generate_flow_definition
from pprint import pprint


@generate_flow_definition
class EncryptAndTransfer(GladierBaseClient):
    gladier_tools = [
        'gladier_tools.posix.Encrypt',
        'gladier_tools.globus.Transfer',
    ]


if __name__ == '__main__':
    flow_input = {
        'input': {
            'encrypt_input': '',
            # Set this to the symmetric key you want to use to encrypt/decrypt the file
            'encrypt_key':'', 
            # Set this to your own funcx endpoint where you want to encrypt files
            'funcx_endpoint_compute': '',
            # Set this to the globus endpoint where your encrypted archive has been created
            'transfer_source_endpoint_id': '',
            # By default, this will transfer the encrypt file to Globus Tutorial Endpoint 1
            'transfer_destination_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
            'transfer_source_path': '',
            'transfer_destination_path': '',
            'transfer_recursive': False,
        }
    }
    eat = EncryptAndTransfer()
    pprint(eat.flow_definition)
    flow = eat.run_flow(flow_input=flow_input)
    action_id = flow['action_id']
    eat.progress(action_id)
    pprint(eat.get_status(action_id))
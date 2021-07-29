from gladier import GladierBaseClient, generate_flow_definition, GladierBaseTool
from pprint import pprint


def make_files(**data):
    import os
    
    input_path = pathlib.Path(data['make_input'])

    if '~' in input_path:
        input_path = os.path.expanduser(input_path)

     if not os.path.exists(input_path):
        os.makedirs(input_path)
        
    for number in range(3):
        with open(input_path / f'file{number}.txt', 'w') as f:
            f.write(f'This is file no. {number}')

    return input_path


@generate_flow_definition
class MakeFiles(GladierBaseTool):
    funcx_functions = [make_files]
    required_input = [
        'make_input',
        'funcx_endpoint_compute'
    ]


@generate_flow_definition
class CustomTransfer(GladierBaseClient):
    gladier_tools = [
        MakeFiles,
        'gladier_tools.posix.Tar',
        'gladier_tools.posix.Encrypt',
        'gladier_tools.globus.Transfer',
    ]


if __name__ == '__main__':
    flow_input = {
        'input': {
            # Set this to the folder in which you want to run the makeFiles function in
            'make_input': '/tmp/myfiles',
            # Set this to the same folder as above
            'tar_input': '',
            # Set this to the resultant archive of the above folder
            'encrypt_input': '',
            # Set this to the symmetric key you want to use to encrypt/decrypt the file
            'encrypt_key': '',
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
    ct = CustomTransfer()
    pprint(ct.flow_definition)
    flow = ct.run_flow(flow_input=flow_input)
    action_id = flow['action_id']
    ct.progress(action_id)
    pprint(ct.get_status(action_id))

from gladier import GladierBaseClient, generate_flow_definition, GladierBaseTool
from pprint import pprint


def makeFiles(**data):
    import os
    input_path = data['make_input']

    if '~' in input_path:
        input_path = os.path.expanduser(input_path)

    with open(input_path+"/file1.txt", "w") as file1:
        file1.write("This is file no. 1")

    with open(input_path+"/file2.txt", "w") as file2:
        file2.write("This is file no. 2")

    with open(input_path+"/file3.txt", "w") as file3:
        file3.write("This is file no. 3")

    return input_path


@generate_flow_definition
class MakeFiles(GladierBaseTool):
    funcx_functions = [makeFiles]
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
            'make_input': '',
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

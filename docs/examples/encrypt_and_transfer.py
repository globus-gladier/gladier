from gladier import GladierBaseClient, generate_flow_definition, GladierBaseTool
from pprint import pprint


def make_files(**data):
    from pathlib import Path

    input_path = Path(data['make_input']).expanduser()
    input_path.mkdir(exist_ok=True, parents=True)

    for number in range(3):
        with open(input_path / f'file{number}.txt', 'w') as f:
            f.write(f'This is file no. {number}')

    return str(input_path)


@generate_flow_definition
class MakeFiles(GladierBaseTool):
    compute_functions = [make_files]
    required_input = [
        'make_input',
        'compute_endpoint'
    ]


@generate_flow_definition
class EncryptAndTransfer(GladierBaseClient):
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
            'tar_input': '/tmp/myfiles',
            # Set this to the resultant archive of the above folder
            'encrypt_input': '/tmp/myfiles.tgz',
            # Set this to the symmetric key you want to use to encrypt/decrypt the file
            'encrypt_key': 'my_secret',
            # Set this to your own compute endpoint where you want to encrypt files
            # 'compute_endpoint': '',
            # Set this to the globus endpoint where your encrypted archive has been created
            # 'transfer_source_endpoint_id': '',
            # By default, this will transfer the encrypt file to Globus Tutorial Endpoint 1
            'transfer_destination_endpoint_id': 'ddb59aef-6d04-11e5-ba46-22000b92c6ec',
            'transfer_source_path': '/tmp/myfiles.tgz.aes',
            'transfer_destination_path': 'my_encrypted_files/myfiles.tgz.aes',
            'transfer_recursive': False,
        }
    }

    # Create the Client
    encrypt_and_transfer = EncryptAndTransfer()

    # Optionally print the flow definition
    # pprint(encrypt_and_transfer.flow_definition)

    # Run the flow
    flow = encrypt_and_transfer.run_flow(flow_input=flow_input)

    # Track progress
    action_id = flow['action_id']
    encrypt_and_transfer.progress(action_id)
    pprint(encrypt_and_transfer.get_status(action_id))

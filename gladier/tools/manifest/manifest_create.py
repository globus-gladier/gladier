import requests
from fair_research_login import NativeClient  # pip install fair-research-login

url = 'https://develop.concierge.nick.globuscs.info/api/manifest/remote_file_manifest/'
scope = 'https://auth.globus.org/scopes/524361f2-e4a9-4bd0-a3a6-03e365cac8a9/concierge'

manifest = {
    'remote_file_manifest': [
        {
            'url': 'globus://ddb59aef-6d04-11e5-ba46-22000b92c6ec/share/godata/file1.txt',
            'filename': 'file1.txt',
            'length': 4,
            'sha256': 'c8b08da5ce60398e1f19af0e5dccc744df274b826abe585eaba68c525434806',
        },
        {
            'url': 'globus://ddb59aef-6d04-11e5-ba46-22000b92c6ec/share/godata/file2.txt',
            'filename': 'file2.txt',
            'length': 4,
            'sha256': 'dd8ed44a83ff94d557f9fd0412ed5a8cbca69ea04922d88c01184a07300a5a',
        },
        {
            'url': 'globus://ddb59aef-6d04-11e5-ba46-22000b92c6ec/share/godata/file3.txt',
            'filename': 'file3.txt',
            'length': 6,
            'sha256': 'f6936912184481f5edd4c304ce27c5a1a827804fc7f329f43d273b8621870776',
        }
    ]
}

client = NativeClient(client_id='e6c75d97-532a-4c88-b031-8584a319fa3e')
client.login(requested_scopes=scope)
headers = {'Authorization': f'Bearer {client.load_tokens_by_scope(requested_scopes=scope)[scope]["access_token"]}'}
r = requests.post(url, headers=headers, json=manifest)
r.raise_for_status()
print(f'Created manifest: {r.json()["id"]}')



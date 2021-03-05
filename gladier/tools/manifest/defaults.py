from gladier.defaults import GladierDefaults


class ManifestTutorial(GladierDefaults):

    flow_definition = {
        'Comment': 'Hello Gladier Automate Flow',
        'StartAt': 'ManifestTutorial',
        'States': {
            'ManifestTutorial': {
                'Comment': 'Manifest Transfer Globus Tutorial Endpoint 1 /share/godata/ files',
                'Type': 'Action',
                'ActionUrl': 'https://develop.concierge.nick.globuscs.info/api/automate/transfer',
                'ActionScope': 'https://auth.globus.org/scopes/524361f2-e4a9-4bd0-a3a6-03e365cac8a9/concierge',
                'Parameters': {
                    'manifest_id.$': '$.input.manifest_tutorial_id',
                    'destination.$': '$.input.manifest_tutorial_destination',
                },
                'ResultPath': '$.ManifestTutorialResult',
                'WaitTime': 300,
                'End': True,
            },
        }
    }

    required_input = [
        'manifest_tutorial_id',
        'manifest_tutorial_destination'
    ]

    flow_input = {
        # Contains tutorial files on /share/godata/ for Globus Tutorial Endpoint 1
        'manifest_tutorial_id': '22ea05b3-a708-4524-b2c7-b3a635ffb1c3',
        # By default, this will transfer to Globus Tutorial Endpoint 2
        'manifest_tutorial_destination': 'globus://ddb59af0-6d04-11e5-ba46-22000b92c6ec/~/'
    }

    # Flow uses no FuncX functions
    funcx_functions = []

import os
from gladier.client import GladierBaseClient
from my_repo.flows import analysis_flow


class HelloGladier(GladierBaseClient):
    secret_config_filename = os.path.expanduser('~/.gladier-secrets.cfg')
    config_filename = 'gladier.cfg'
    app_name = 'gladier_client'
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'

    gladier_tools = [
        'my_repo.custom_tools.PrepareData',
        'my_repo.custom_tools.RunAnalysis',
        'my_other_repo.stats.GenerateStatistics',
        'my_other_repo.custom_tools.Publish',
    ]
    flow_definition = analysis_flow


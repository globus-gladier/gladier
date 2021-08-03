import os
from gladier import GladierBaseClient, generate_flow_definition
from my_tools import RunAnalysis


@generate_flow_definition
class ExampleAnalysisPipeline(GladierBaseClient):
    secret_config_filename = os.path.expanduser('~/.gladier-secrets.cfg')
    config_filename = 'gladier.cfg'
    app_name = 'gladier_client'
    client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'

    gladier_tools = [
        'my_repo.custom_tools.PrepareData',
        RunAnalysis,
        'my_other_repo.stats.GenerateStatistics',
        'my_other_repo.custom_tools.Publish',
    ]

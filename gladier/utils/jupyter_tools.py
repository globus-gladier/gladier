from IPython.display import clear_output
import json
from pprint import pprint
from datetime import datetime, timezone
import time

from globus_automate_client import create_flows_client
from globus_automate_client.token_management import CLIENT_ID


def flow_check(flow, flow_action, flows_client=None, refresh=10):
    
    start = datetime.fromisoformat(flow_action['start_time'])
    flow_id = flow['id']
    flow_scope = flow['globus_auth_scope']
    if not flows_client: 
        flows_client = create_flows_client(CLIENT_ID)

    while True:
        flow_action_id = flow_action['action_id']
        flow_action = flows_client.flow_action_status(flow_id, flow_scope, flow_action_id)
        flow_status = flow_action['status']

        print(f'Flow status: {flow_status}')
        
        if flow_status == 'ACTIVE': 
            now = datetime.now(timezone.utc)
            print(f'Time elapsed: {now - start}')
            pprint(json.dumps(flow_action.data, indent = 2, sort_keys=True))
        elif flow_status == 'FAILED':
            complete = datetime.fromisoformat(flow_action['completion_time'])
            print(f'Time elapsed: {complete - start}')
            break
        elif flow_status == 'SUCCEEDED':
            complete = datetime.fromisoformat(flow_action['completion_time'])
            print(f'Time elapsed: {complete - start}')
            break

        clear_output(wait=True)
        time.sleep(refresh)
        
    return flow_action

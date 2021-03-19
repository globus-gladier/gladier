import traceback
import logging
from funcx.serialize import FuncXSerializer

log = logging.getLogger(__name__)

automate_response_keys = {'action_id', 'status', 'state_name'}
funcx_response_keys = {'result', 'status', 'exception', 'task_id'}


def is_automate_response(state_output):
    return (
        isinstance(state_output, dict) and
        set(state_output.keys()).intersection(automate_response_keys)
    )


def is_funcx_response(state_output):
    return (
        is_automate_response(state_output) and
        set(state_output['details'].keys()).intersection(funcx_response_keys)
    )


def get_details(response, state_name=None):
    if state_name and is_automate_response(response['details']['output'].get(state_name)):
        return response['details']['output'][state_name]

    if is_funcx_response(response['details']['output'].get(state_name)):
        resp = response['details']['output'][state_name]
        if resp.get('exception'):
            resp['exception'] = deserialize_exception(resp['exception'])
        return resp

    for flow_state, data in response['details']['output'].items():
        # Reject any output that isn't structured as a response
        if not is_funcx_response(data):
            continue
        if isinstance(data['details'], dict) and data['details'].get('exception'):
            exc = deserialize_exception(data['details']['exception'])
            data['details']['exception'] = exc
    return response


def deserialize_exception(encoded_exc):
    try:
        FuncXSerializer().deserialize(encoded_exc).reraise()
    except Exception:
        return traceback.format_exc()

def find_min_args(flow_def):
    import re

    regex = r"\'\$\.(\w+)\.(\w+)\'"
    rep = re.compile(regex)

    flow_str = str(flow_def)
        
    matches = rep.finditer(flow_str)

    args = {}
    for k, match in enumerate(matches):
        args.setdefault(match.group(1),{})
        args[match.group(1)][match.group(2)] = ''
    return args


def sort_keys(data):
    keys=[]
    for k in data.keys():
        for l in data[k].keys():
            keys.append(k+'.'+l)
    return sorted(keys)

def check_payload(min_data, payload):
    data_keys = sort_keys(payload)
    min_data_keys = sort_keys(min_data)

    missing_keys=[]
    for k in min_data_keys:
        if k not in data_keys:
            print('$.'+k, ' is missing on payload!')
            missing_keys.append(k)
    return sorted(missing_keys)
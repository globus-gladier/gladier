import json
import typing as t
from pathlib import Path

from .helpers import JSONObject

_cache_file = Path.home() / ".globus_flows_cache"


def canonicalize_dict(d: t.Dict[str, t.Any]) -> str:
    return json.dumps(d, sort_keys=True)


def get_globus_flows_cache() -> t.Dict[str, str]:
    try:
        with open(_cache_file) as f:
            cache = json.load(f)
            return cache
    except FileNotFoundError:
        return {}


def save_globus_flows_cache(cache: t.Dict[str, str]) -> None:
    with open(_cache_file, "w") as f:
        json.dump(cache, f, indent=2)


def cache_key_for_flow_and_title(flow_def: JSONObject, title: str) -> str:
    canonical_flow_def = canonicalize_dict(flow_def)
    cache_key = f"Title: {title}#{canonical_flow_def}"
    return cache_key


def flow_id_for_flow_def(flow_def: JSONObject, title: str) -> t.Union[str, None]:
    cache_key = cache_key_for_flow_and_title(flow_def, title)
    flow_cache = get_globus_flows_cache()
    return flow_cache.get(cache_key)


def save_flow_to_cache(flow_def: JSONObject, title: str, flow_id: str) -> None:
    cache_key = cache_key_for_flow_and_title(flow_def, title)
    flow_cache = get_globus_flows_cache()
    flow_cache[cache_key] = flow_id
    save_globus_flows_cache(flow_cache)

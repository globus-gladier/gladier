"""
These modules are taken from fair-research-login

https://github.com/fair-research/native-login

Apache License 2.0
"""


def default_name_key(group_key, key):
    return "{}__{}".format(group_key.replace(".", "_"), key)


def default_fetch_key(key):
    resource_server, token_name = key.split("__")
    return resource_server.replace("_", "."), token_name


def flat_pack(tokens, name_key=default_name_key):
    """
    Take a dict of tokens organized by resource server and return a dict
    that can be easily saved to a config file.
    Resource servers containing '.' in their name will automatically be
    converted to '_' (auth.globus.org == auth_globus_org). Tokens by default
    are prefixed by this name, which you can modify with by setting the
    name_item() function. An example is here:

    name_item = lambda key, token: '{}_{}'.format(key.replace('.', '_'), token)

    which results in a token name being written as:

    auth_globus_org_access_token = <value>

    Int values are converted to string, None values are converted
    to empty string. *No other types are checked*.
    `tokens` should be formatted:
    {
        "auth.globus.org": {
            "scope": "profile openid email",
            "access_token": "<token>",
            "refresh_token": None,
            "token_type": "Bearer",
            "expires_at_seconds": 1539984535,
            "resource_server": "auth.globus.org"
        }, ...
    }
    Returns a flat dict of tokens prefixed by resource server.
    {
        "auth_globus_org_scope": "profile openid email",
        "auth_globus_org_access_token": "<token>",
        "auth_globus_org_refresh_token": "",
        "auth_globus_org_token_type": "Bearer",
        "auth_globus_org_expires_at_seconds": "1540051101",
        "auth_globus_org_resource_server": "auth.globus.org",
        "token_groups": "auth_globus_org"
    }"""

    flattened_items = {}
    for token_set in tokens.values():
        for key, value in token_set.items():
            key_name = name_key(token_set["resource_server"], key)
            if isinstance(value, int):
                value = str(value)
            if value is None:
                value = ""
            flattened_items[key_name] = value

    return flattened_items


def flat_unpack(flat_tokens, fetch_key=default_fetch_key):
    """
    Takes a dict from a config section and returns a dict of tokens by
    resource server. `config_items` is a raw dict of config options
    returned from get_parser().get_section().
    Returns tokens in the format:
    {
        "auth.globus.org": {
            "scope": "profile openid email",
            "access_token": "<token>",
            "refresh_token": None,
            "token_type": "Bearer",
            "expires_at_seconds": 1539984535,
            "resource_server": "auth.globus.org"
        }, ...
    }
    """
    if not flat_tokens:
        return {}

    token_sets = {}
    for fkey, fvalue in flat_tokens.items():
        resource_server, key = fetch_key(fkey)
        tset = token_sets.get(resource_server, {})
        tset[key] = fvalue or None

        if key == "expires_at_seconds":
            tset["expires_at_seconds"] = int(tset["expires_at_seconds"])

        token_sets[resource_server] = tset
    # It's possible for the 'fetch_key' to match the name of the resource
    # server. This shouldn't matter if we only rely on the key for fetching
    # items and use the stored value in 'resource_server' for the real name
    return {tset["resource_server"]: tset for tset in token_sets.values()}

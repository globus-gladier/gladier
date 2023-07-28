import typing as t

from gladier.tools.builtins import ActionState


class SearchIngest(ActionState):
    """
    Ingest a document into Globus Search

    .. code-block:: python

        from gladier.tools import SearchIngest, SearchDelete

        client = GladierClient(flow_definition=SearchIngest().get_flow_definition())

        flow_run = client.run_flow(
            {"input": {
                "compute_endpoint": "4b116d3c-1703-4f8f-9f6f-39921e5864df",
                "content": {
                    "contributors": [
                        "John Smith",
                        "FrobozzCo",
                        "Zaphod Beeblebrox"
                    ],
                    "keywords": ["foo", "bar", "baz"],
                    "title": "My Globus Tutorial Dataset"
                },
                "subject": subject,
                "search_index": '6a045ba6-68d7-41fa-9fae-17d0192fd859',
                "visible_to": ['public'],
            }}
        )
    """

    action_url = "https://actions.globus.org/search/ingest"
    id: t.Optional[str] = None
    search_index: str = "$.input.search_index"
    subject: str = "$.input.subject"
    visible_to: t.Union[list, str] = "$.input.visible_to"
    content: t.Union[dict, str] = "$.input.content"


class SearchDelete(ActionState):
    """
    Delete a single subject in Globus Search

    .. code-block:: python

        from gladier.tools import SearchIngest, SearchDelete

        client = GladierClient(flow_definition=SearchIngest().get_flow_definition())

        flow_run = client.run_flow(
            {"input": {
                "subject": subject,
                "search_index": 'my-search-index-uuid',
                "visible_to": ['public'],
            }}
        )
    """

    action_url = "https://actions.globus.org/search/delete"
    delete_by = "subject"
    search_index: str = "$.input.search_index"
    subject: str = "$.input.subject"


class SearchDeleteByQuery(ActionState):
    """
    Delete many subjects in Globus Search by query

    .. code-block:: python

        from gladier.tools import SearchDeleteByQuery

        client = GladierClient(flow_definition=SearchIngest().get_flow_definition())

        flow_run = client.run_flow(
            {"input": {
                "query": "*",
                "search_index": '6a045ba6-68d7-41fa-9fae-17d0192fd859',
            }}
        )
    """

    action_url = "https://actions.globus.org/search/delete"
    delete_by = "query"
    search_index: str = "$.input.search_index"
    q: str = "$.input.q"
    filters: t.Union[list, str] = None
    # query_template is a mysterious value shown in examples but not defined yet in the docs
    # https://docs.globus.org/api/flows/hosted-action-providers/ap-search-delete/
    query_template: t.Optional[None] = None

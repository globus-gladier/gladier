import typing as t

from gladier.tools.builtins import ActionState


class SearchIngest(ActionState):
    action_url = "https://actions.globus.org/search/ingest"
    id: t.Optional[str] = None
    search_index: str = "$.input.search_index"
    subject: str = "$.input.subject"
    visible_to: t.Union[list, str] = "$.input.visible_to"
    content: t.Union[dict, str] = "$.input.content"


class SearchDelete(ActionState):
    action_url = "https://actions.globus.org/search/delete"
    delete_by = "subject"
    search_index: str = "$.input.search_index"
    subject: str = "$.input.subject"


class SearchDeleteByQuery(ActionState):
    action_url = "https://actions.globus.org/search/delete"
    delete_by = "query"
    search_index: str = "$.input.search_index"
    q: str = None
    filters: t.Union[list, str] = None
    # query_template is a mysterious value shown in examples but not defined yet in the docs
    # https://docs.globus.org/api/flows/hosted-action-providers/ap-search-delete/
    query_template: t.Optional[None] = None

Auth in Gladier
===============

By Default, Gladier will automatically initiate a login as needed. This behavior
can be customized if Glaider needs to be used as part of a larger app.

Scopes
------

Gladier requires scopes for the following Services:

* Globus Flows Service
    * `https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run`
    * `https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run_manage`
    * `https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/view_flows`
    * `https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run_status`
    * `https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/manage_flows`
* FuncX
    * `openid`
    * `urn:globus:auth:scope:search.api.globus.org:all`
    * `https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all`
* Deployed Flow
    * Scope varies per-flow

Note that the Deployed Flow will be unique for each Glaider Client,
and the scope will not exist until the flow is deployed. This sometimes
requires multiple logins with Globus, first to fetch the base flows
service scopes to deploy the flow, then a second login to get tokens
to run the newly deployed flow.

Note also, that dependent scopes underlying the deployed flow may also
change if the flow is modified to add additional services. For example,
a flow could be initially deployed to do a simple transfer task, then
modified and run again but with an additional search ingest task. If this
happens, a new login must take place in order for the modified flow to be
run again.

Storage
-------

By default, tokens in Gladier are stored in ``~/.gladier-secrets.cfg``

Customizing Auth
----------------

The default behavior of Auth in Gladier can be changed by passing a custom Login Manager
into any Gladier Client: 

.. code-block:: python

    from gladier import CallbackLoginManager

    def callback(scopes: List[str]) -> Mapping[str, Union[AccessTokenAuthorizer, RefreshTokenAuthorizer]]:
        authorizers_by_scope = do_my_login(scopes)
        return authorizers_by_scope

    callback_login_manager = CallbackLoginManager(
        # A dict of authorizers mapped by scope can be provided if available
        initial_authorizers,
        # If additional logins are needed, the callback is called.
        callback=callback
    )

    MyGladierClient(login_manager=callback_login_manager)


``my_custom_login_function`` should be capable of both completeing a Globus Auth flow
and storing tokens for future invacations. Ideally, ``initial_authorizers`` will contain
all of the scopes needed so no login is needed.

Complete example
----------------

The complete example below uses Fair Research Login to demontrate a customized login flow.
Please note, this example assumes customization using a Native App. Those using the authorization
code grant, such as in a webservice, must modify their app accordingly.

.. literalinclude:: custom_login.py
   :language: python

Upgrade Migrations
==================


Migrating to v0.4.0
-------------------

Gladier v0.3.x depended on FuncX v0.0.5 and FuncX Endpoint v0.0.3. Gladier v0.4.x
now uses Funcx v0.2.3-v0.3.0+ (funcx-endpoint v0.2.3-v0.3.0+). There are a number
of breaking changes between these two versions of FuncX, including funcx endpoints,
flow definitions, and backend services.

FuncX Endpoints
^^^^^^^^^^^^^^^

All FuncX endpoints will need to be recreated with the never version of FuncX.
Gladier typically names these endpoints as the following:

* ``funcx_endpoint_non_compute``
* ``funcx_endpoint_compute``

Since these use different backend services, using endpoints that don't match the
FuncX version will result in errors. Using 0.0.3 endponits on 0.2.3+ will result
in permission denied, using 0.2.3+ on 0.0.3 will result in Server 500s.

Argument Passing and Function Definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Previously, all arguments in a Flow were passed to FuncX functions as a dict. It
looked like the following:

.. code-block::

  'Parameters': {'tasks': [{'endpoint.$': '$.input.funcx_endpoint_non_compute',
                            'function': '8227609b-4869-4c6f-9a1b-87dc49fcc687',
                            'payload.$': '$.input'}]},

  def my_function(data):
      ...


In the above, ``data`` would get the entire dict from $.input, which was typically
whatever input was passed to start the flow. In the new version of FuncX, this has
changed. All arguments are either positional or keyword arguments and should be named.
This is difficult in automate, since naming arguments requires specifying them
explicitly in the flow definition. An easy migration path is the following:

.. code-block::

  'Parameters': {'tasks': [{'endpoint.$': '$.input.funcx_endpoint_non_compute',
                            'function': '8227609b-4869-4c6f-9a1b-87dc49fcc687',
                            'payload.$': '$.input'}]},

  def my_function(**data):
      ...

Changing data to a keyword argument will allow re-creating the same behavior as
before.


FuncX Functions
^^^^^^^^^^^^^^^

Like FuncX Endpoints, FuncX Functions also need to be changed between versions.
This is an automatic process in most cases if you are running the latest version
of Gladier and saw a big giant warning when upgrading. Gladier will automatically
delete funcx functions that don't match the newly supported version of FuncX
Gladier uses.

However, it's necessary to do a manual upgrade to remove these functions in some
cases. To upgrade manually, edit the file ``~/.gladier-secrets.cfg``, and remove
all config items that end in ``funcx_id`` and ``funcx_id_checksum``:


.. code-block::

   hello_world_funcx_id = 3bccfcdb-bc0e-4549-9297-8e08c6f50bd5
   hello_world_funcx_id_checksum = c590423de52051e7b7bb044dc173673d2c9ad965f7f71bee665494815b3a2046


Flow Definitions
^^^^^^^^^^^^^^^^

Some items in Automate flow definitions also changed. See below for a list of
the attributes.

FuncX Version 0.0.5 flow definitions:

* ``ActionUrl`` -- 'https://api.funcx.org/automate'
* ``ActionScope`` -- 'https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/automate2'


FuncX Version 0.2.3+ flow definitions:


* ``ActionUrl`` -- 'https://automate.funcx.org'
* ``ActionScope`` -- 'https://auth.globus.org/scopes/b3db7e59-a6f1-4947-95c2-59d6b7a70f8c/action_all'


Additionally for FuncX Payloads, Function UUIDs are passed with a different name.


'func.$': '$.input.'

Needs to be changed to:

'function.$': '$.input.'

The Gladier Client
------------------

.. literalinclude:: tools/example_client.py
   :language: python


Gladier Clients store a collection of Glaider Tools and prepare them for a Globus
Flow. Clients will handle registration of flows with Globus Automate, in addition
to registering individual funcx functions for all tools. Flows and FuncX functions
are checked each time a flow is run, so they are always up-to-date.

There are two main components of a Gladier Client:

* ``gladier_tools`` -- A list of Gladier Tools derived from ``gladier.GladierBaseTool``
  More on Gladier Tools below.
* ``flow_definition`` -- A complete Globus Flow

The Gladier Client allows for some extra runtime configuration:

* ``secret_config_filename`` -- defines where login credentials are stored
* ``config_filename`` -- defines where GladierClient specific runtime variables are stored
* ``app_name`` -- The name of the application, as it appears in Globus
* ``client_id`` -- The UUID of the registered Globus Application, from https://developers.globus.org


.. autoclass:: gladier.client.GladierBaseClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members:

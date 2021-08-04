
Clients
-------

.. literalinclude:: example_client.py
   :language: python


Main Components
^^^^^^^^^^^^^^^

There are two main components of a Gladier Client:

* ``gladier_tools`` -- A list of Gladier Tools derived from ``gladier.GladierBaseTool``
  More on Gladier Tools below.
* ``flow_definition`` -- A complete Globus Flow, supplied automatically with ``@generate_flow_definition``

``gladier_tools`` may be specified as a dotted string path (Ex: ``my_repo.custom_tools.PrepareData``)
or as a class that derives from ``gladier.GladierBaseTool`` (Ex: ``RunAnalysis``). If
``@generate_flow_definition`` is used, the order the tools
appear in the list determines the order they will appear in the flow. Each tool *must* have a complete
and valid flow defined on it.

``flow_definition`` may be a python dict which defines a full and complete flow, and can be an
alternative to using ``@generate_flow_definition``. Note that ``@generate_flow_definition will
overwrite the ``flow_definition`` set on the client on instantiation.


Other Attritubes
^^^^^^^^^^^^^^^^


* ``globus_group`` -- adds the Globus Group to all Automate permission levels: visible_to, runnable_by, administered_by, manage_by, monitor_by. See the `Flows Client Docs <https://globus-automate-client.readthedocs.io/en/latest/cli_reference.html?highlight=visible_to#cli-reference>`_ for more info.
* ``secret_config_filename`` -- defines where login credentials are stored. Also stores function/flow ids and checksums
* ``config_filename`` -- defines where GladierClient specific runtime variables are stored
* ``app_name`` -- The name of the application, as it appears in Globus
* ``client_id`` -- The UUID of the registered Globus Application, from https://developers.globus.org


See Also
^^^^^^^^

* The complete :ref:`sdk_reference`
* :ref:`flow_generation`

Publish
=======

Publish takes files or directories and transfers them to another publication endpoint
and ingests metadata about the files into Globus Search. Both the index in Globus Search
and the Globus Endpoint in Globus Pilot must be setup first.

Setup only needs to be done once, then publish can be used freely afterwards.
Both Globus Pilot and Globus Search CLI can be installed with the following:

.. code-block:: bash

   pip install globus-search-cli globus-pilot

Globus Search CLI is responsible for setting up indices in Globus Search. Globus Pilot
is a tool which generates metadata about files and directories and handles both the
transfer to an endpoint and the ingest to search.

Create the index with the following:

.. code-block:: bash

   globus-search index create my-index

Setup your publication endpoint with the index you created above with:

.. code-block:: bash

   globus-pilot index setup <UUID from the step above>

After that, you should be ready to publish to your data. See documentation for both
of the tools above here:

* `Globus Search CLI <https://github.com/globus/globus-search-cli>`_
* `Globus Pilot <https://github.com/globus/globus-pilot>`_


.. autoclass:: gladier_tools.publish.Publish
   :show-inheritance:
Manifest Service
================

The manifest tool can be used to transfer a large number of files
at once.


Creating a Manifest
-------------------

There is no Action Provider for creating a manifest (yet). See ``create_manifest.py``
for creating a new manifest to transfer

For more information about check, register, and batch-register, you can query
the in-code docs.

.. code-block:: bash

  import gladier.tests  # noqa -- Enables debug logging
  from gladier.client import GladierClient
  from pprint import pprint


  class GladierManifest(GladierClient):
      client_id = 'e6c75d97-532a-4c88-b031-8584a319fa3e'
      gladier_tools = [
          'gladier.tools.manifest.ManifestTutorial',
      ]
      flow_definition = 'gladier.tools.manifest.ManifestTutorial'


  g_cli = GladierManifest()
  flow = g_cli.start_flow()
  g_cli.progress(flow['action_id'])
  details = g_cli.get_details(flow['action_id'], 'HelloFuncXResult')
  pprint(details)

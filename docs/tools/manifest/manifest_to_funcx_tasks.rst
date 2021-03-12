.. _manifest-to-funcx-tasks:

Manifest To FuncX Tasks
=======================

Splitting a manifest into FuncX tasks is a two step process. First, the manifest
is fetched. Second, the entries within the manifest are split into discrete FuncX
tasks. Note that the first task requires internet access to fetch manifest information,
and the second does work on the manifest paths.

* ``funcx_endpoint_non_compute`` -- A FuncX Endpoint with internet access for fetching the manifest
* ``manifest_to_funcx_tasks_funcx_endpoint_compute`` -- A FuncX endpoint for running compute tasks
* ``manifest_to_tasks_manifest_id`` -- A UUID to a manifest in the Manifest Service
* ``manifest_to_funcx_tasks_callback_funcx_id`` -- A funcX function id for the task that needs to be run

Notice ``manifest_to_funcx_tasks_callback_funcx_id`` requires an explicit FuncX function id. Since

Manifest Transfer Tool
----------------------

.. autoclass:: gladier.tools.manifest.defaults.ManifestToFuncXTasks
   :show-inheritance:

.. literalinclude:: ../../../gladier/tools/manifest/defaults.py
   :language: python
   :pyobject: ManifestToFuncXTasks

Try It Out
----------

.. literalinclude:: manifest_to_funcx_tasks_example.py
   :language: python

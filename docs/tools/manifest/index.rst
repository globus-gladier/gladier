
Manifests
=========

The Manifest Service is a way to keep track of a large number of files at the
same time. Instead of making many individual transfers, or looping over many
files in a single FuncX function, Manifests allow transferring groups of files
by a ``manifest_id`` and include tooling to easily split manifests into a set of
parallelizable FuncX tasks.

.. toctree::
   :maxdepth: 2
   :caption: Manifest Tools and Resources:

   creating_manifests
   manifest_transfer
   manifest_to_funcx_tasks
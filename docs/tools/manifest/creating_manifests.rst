.. _creating-manifests:

Creating A Manifest
===================

Manifests are created using the BDBag `Remote File Manifest <https://github.com/fair-research/bdbag/blob/master/doc/config.md#remote-file-manifest>`_
and Globus Manifest [citation needed] formats.

Example Create
--------------

There is currently no Globus Action Provider for creating new manifests. You can
create one using the following:

.. literalinclude:: ../../../gladier/tools/manifest/manifest_create.py
   :language: python


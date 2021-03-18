.. _manifest-transfer:

Manifest Transfer
=================

There are only two things required for transferring a manifest:

* ``manifest_id`` -- A UUID to a manifest in the Manifest Service
* ``manifest_destination`` -- A Globus URL to the intended destination

To create a manifest, see :ref:`creating-manifests`. Manifest Destinations can
be any endpoint-path combination. A Globus URLs looks like this:

.. code-block::

   globus://ddb59af0-6d04-11e5-ba46-22000b92c6ec/~/

The URL above points to
a users home directory on `Globus Tutorial 2 <https://app.globus.org/file-manager?origin_id=ddb59af0-6d04-11e5-ba46-22000b92c6ec&origin_path=%2F~%2F>`_

Manifest Transfer Tool
----------------------

.. autoclass:: gladier.tools.manifest.defaults.ManifestTransfer
   :show-inheritance:

.. literalinclude:: ../../../gladier/tools/manifest/defaults.py
   :language: python
   :pyobject: ManifestTransfer

Try It Out
----------

.. literalinclude:: manifest_transfer_example.py
   :language: python

Gladier Tools
=============

Gladier tools is an optional package containing commonly used operations. You can
install Gladier Tools with the following:

.. code-block:: bash

   pip install gladier-tools

Once the Gladier Tools packages is installed, individual tools can be added to
your client like so:

.. literalinclude:: ../examples/tar_and_transfer.py
   :language: python
   :pyobject: TarAndTransfer

The following Gladier Tools are available:

.. code-block:: python

  # Posix
  'gladier_tools.posix.Tar',
  'gladier_tools.posix.UnTar',
  'gladier_tools.posix.Encrypt',
  'gladier_tools.posix.Decrypt',
  'gladier_tools.posix.AsymmetricEncrypt',
  'gladier_tools.posix.AsymmetricDecrypt',
  'gladier_tools.posix.HttpsDownloadFile',

  # Globus
  'gladier_tools.globus.Transfer',

  # Publish
  'gladier_tools.publish.Publish',

See the sections below for detailed information about each tool.

.. toctree::
   :maxdepth: 3
   :caption: Gladier Tools:

   globus/index
   publish/index
   posix/index
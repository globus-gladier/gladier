Gladier
=======

Gladier is a development tool that sits on top of the `Globus Automate Client <https://globus-automate-client.readthedocs.io/en/latest/>`_
and `FuncX <https://funcx.org/>`_. This allows a scientist to write arbitrary
python code for any purpose, deploy it to an HPC, and tie the
workflow together into a complete Globus Flow for execution on demand.

The documentation below will cover the following:

* Installing Gladier
* Setting up your environment (FuncX and GCP)
* Running Gladier Clients

When you are familiar with running Gladier Clients, you should browse the
reference documentation on Gladier Clients, Tools, and how to tweak the final
Globus Flow with flow generation modifiers.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   setup
   getting_started
   client
   tools
   custom_tools
   flow_generation
   passing_payloads
   custom_auth
   sdk_reference

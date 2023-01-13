Gladier
=======

Gladier (the "GLobus Architecture for Data-Intensive Experimental Research") is a Python toolkit
for developing data collection, analysis, and publication pipelines ("flows") for experimental
facilities. A flow might, for example:

* Retrieve data from an instrument, verify its quality, extract metadata, and publish
  data+metadata to a catalog, or:
* Collect data from a series of experiments, train a machine learning model, and deploy the model
  to an instrument.

In these and many other applications, Gladier makes it easy to specify what actions to perform,
and where, and then to execute those actions reliably and securely.

Gladier builds on the powerful cloud-hosted `Globus platform <https://docs.globus.org/>`_, including
`Globus automation services <https://docs.globus.org/globus-automation-services/>`_
for reliable and scalable flow execution; `Globus Auth <https://docs.globus.org/api/auth/>`_ for
secure distributed operation; and services like
`Globus Transfer <https://docs.globus.org/api/transfer/>`_, `funcX <https://funcx.org/>`_, and
`Globus Search <https://docs.globus.org/api/search/>`_ to implement data transfer, compute,
cataloging, and other actions.

You can read more about Gladier, including example applications, in a
`technical report <https://arxiv.org/pdf/2204.05128.pdf>`_; here we
focus on how to install and use it, and provide pointers to sample code.

.. figure:: https://media.githubusercontent.com/media/globus-gladier/gladier/main/docs/gladier/static/001-Overview-Globus-Automation-Services.png
   :scale: 50 %
   :alt: Globus Automation Services

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   setup
   running_flows
   tools
   flow_generation
   passing_payloads
   custom_auth

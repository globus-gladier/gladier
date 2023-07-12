.. _setup:

Setup
=====


We first consider a simple Gladier Flow that transfers data from an instrument computer to an
analysis computer, and then runs an analysis function on the analyasis computer. The flow thus
comprises two steps:

* Transfer: Copy data to the analysis computer.
* Compute: Run the analysis function on the data copied in the first step.

.. figure:: https://media.githubusercontent.com/media/globus-gladier/gladier/main/docs/gladier/static/002-Setup-Transfer-Compute.jpeg
   :scale: 25 %
   :alt: Globus Automation Services

The first step involves a Globus Transfer action, and the second a Globus Compute action.
In order for your computer to be accessible by Globus, it needs to be running a Globus collection.
See the Globus Connect Personal section below. For the second part, you  need to set up a Compute
Endpoint to tell Globus where it should execute functions. See the Comptue Endpoint section below
for details.

Globus Connect Personal
#######################

To run tools like ``gladier_tools.globus.Transfer``, we need access to a Globus collection.
Follow the `Globus Connect Personal <https://www.globus.org/globus-connect-personal>`_ instructions
to set up your own Globus Connect Personal
endpoint and configure a collection, then navigate to
`Globus Web App <https://app.globus.org/collections>`_ collections to see details about the
collections to which you have access.

.. note::

   Your Globus endpoint should be accessible on the same machine you install your FuncX endpoint.

Globus Compute Endpoint
#######################

We also need a Compute Endpoint to run remote functions. Follow the
`Compute Endpoint instructions <https://funcx.readthedocs.io/en/latest/endpoints.html>`_
to set up your own endpoint. Once an endpoint has been configured, you can:

* run ``globus-compute-endpoint list`` to list all endpoints to which you have access
* run ``globus-compute-endpoint start <endpoint-name>`` to start an endpoint

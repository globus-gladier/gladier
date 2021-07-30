
Examples
=========

Pre Requisites
---------------

Before we run the below examples, there are a few things we need to have up and running.
The Examples below show some common real-world problems. They can typically be split into two parts:

   * Transfer data into a location where execution can be performed (usually a super computer)
   * Perform the execution

The first part is solved by Globus Transfer, and the second by FuncX Endpoints. In order for your computer to be accessible by Globus, it needs to be running a Globus Endpoint. See the Globus Connect Personal section below for how to set that up. For the second part, you will need to setup a FuncX Endpoint to tell funcx where it should execute functions. See the funcx-endpoint section below for setting up a funcx-endpoint on your machine.

GlobusConnectPersonal
######################

To run tools like ``gladier_tools.globus.Transfer``, we need access to Globus endpoints. One can use tutorial endpoints `1 <https://app.globus.org/file-manager/collections/ddb59aef-6d04-11e5-ba46-22000b92c6ec/overview>`_ and `2 <https://app.globus.org/file-manager/collections/ddb59af0-6d04-11e5-ba46-22000b92c6ec/overview?back=collections>`_.
However, setting up your own endpoint gives you more control over the data you transfer, which brings us to GlobusConnectPersonal. Follow the instructions `here <https://www.globus.org/globus-connect-personal>`_ to set up your own GCP endpoint, then navigate to `Globus Webapp endpoints <https://app.globus.org/endpoints>`_ to see details about the endpoint. 


**Your Globus endpoint should be accessible on the same machine you install your FuncX endpoint.**

funcx-endpoint
###############

Another thing we need to run flows are an endpoint to run the funcx-functions on. There is a tutorial endpoint that can be used but it is generally preferred to set up a funcx-endpoint. 
Follow the instructions `here <https://funcx.readthedocs.io/en/latest/endpoints.html>`_ to set up your own endpoint. Once an endpoint has been configured, you can list all the endpoints you have using
``funcx-endpoint list``. To start an endpoint, use ``funcx-endpoint start <endpoint-name>``.

Example Flows
--------------

.. toctree::
   :maxdepth: 2

   examples/tar_and_transfer
   examples/encrypt_and_transfer


Examples
========

Pre Requisites
---------------

Before we run the below examples, there are a few things we need to have up and running.
The Examples below show some common real-world problems. They can typically be split into two parts:

   * Transfer data into a location where execution can be performed (usually a super computer)
   * Perform the execution

The first part is solved by Globus Transfer, and the second by FuncX Endpoints. In order for your computer to be accessible by Globus, it needs to be running a Globus Endpoint. See the Globus Connect Personal section below for how to set that up. For the second part, you will need to setup a FuncX Endpoint to tell funcx where it should execute functions. See the funcx-endpoint section below for setting up a funcx-endpoint on your machine.

Globus Connect Personal
#######################

To run tools like ``gladier_tools.globus.Transfer``, we need access to Globus endpoints. One can use `Globus Tutorial Endpoint 1 <https://app.globus.org/file-manager/collections/ddb59aef-6d04-11e5-ba46-22000b92c6ec/overview>`_ and `Globus Tutorial Endpoint 2 <https://app.globus.org/file-manager/collections/ddb59af0-6d04-11e5-ba46-22000b92c6ec/overview?back=collections>`_.
However, setting up your own endpoint gives you more control over the data you transfer, which brings us to Globus Connect Personal. Follow the `Globus Connect Personal <https://www.globus.org/globus-connect-personal>`_ instructions to set up your own GCP endpoint, then navigate to `Globus Web App endpoints <https://app.globus.org/endpoints>`_ to see details about the endpoint.


**Your Globus endpoint should be accessible on the same machine you install your FuncX endpoint.**

FuncX Endpoint
##############

Another thing we need to run flows are an endpoint to run the funcx-functions on. There is a tutorial endpoint that can be used but it is generally preferred to set up a funcx-endpoint. 
Follow the `FuncX Endpoint instructions <https://funcx.readthedocs.io/en/latest/endpoints.html>`_ to set up your own endpoint. Once an endpoint has been configured, you can list all the endpoints you have using
``funcx-endpoint list``. To start an endpoint, use ``funcx-endpoint start <endpoint-name>``.

Example Flows
--------------

.. toctree::
   :maxdepth: 2

   examples/tar_and_transfer
   examples/encrypt_and_transfer


Examples
=========

Pre Requisites
---------------

Before we run the below examples, there are a few things we need to have up and running. 

GlobusConnectPersonal
######################

To run tools like ``gladier_tools.globus.Transfer``, we need access to Globus endpoints. One can use tutorial endpoints `1 <https://app.globus.org/file-manager/collections/ddb59aef-6d04-11e5-ba46-22000b92c6ec/overview>`_ and `2 <https://app.globus.org/file-manager/collections/ddb59af0-6d04-11e5-ba46-22000b92c6ec/overview?back=collections>`_.
However, setting up your own endpoint gives you more control over the data you transfer, which brings us to GlobusConnectPersonal. Follow the instructions `here <https://www.globus.org/globus-connect-personal>`_ to set up your own GCP endpoint, then navigate to `Globus Webapp endpoints <https://app.globus.org/endpoints>`_ to see details about the endpoint. 


funcx-endpoint
###############

Another thing we need to run flows are an endpoint to run the funcx-functions on. There is a tutorial endpoint that can be used but it is generally preferred to set up a funcx-endpoint. 
Follow the instructions `here <https://funcx.readthedocs.io/en/latest/endpoints.html>`_ to set up your own endpoint.

Example Flows
--------------

.. toctree::
   :maxdepth: 2

   examples/tar_and_transfer
   examples/encrypt_and_transfer

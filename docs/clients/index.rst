Gladier Tool
=============

Gladier tools are reusable components that can be strung together to create
a new workflow. Each flow may be unique, but the components of a
workflow can usually be split into three parts: Transfer, Compute, Publication.

Each Gladier tool is a set of two things:

* A reusable set of FuncX functions
* An example introductory flow

.. toctree::
   :maxdepth: 1
   :caption: List of Gladier Tools:

   hello_world/index
   manifest/index


Configuring A Experiment Gladier
--------------------------

Setup your Experiment Gladier with a list of the tools, endpoints, containers, etc; you want to use. 

An Experiment Gladier has built-in functions for automatically registering
and deploying FuncX functions and Automate Flows. Running the example
above looks like this:

.. code-block:: python
   hello_cli = HelloGladier()
   flow = hello_cli.start_flow()
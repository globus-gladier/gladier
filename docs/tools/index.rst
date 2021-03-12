Gladier Tools
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


Configuring A Gladier Tool
--------------------------

Setup your workflow by overriding the Gladier Client with a list of the
tools you want to use. An example looks like this:

.. literalinclude:: gladier_example.py
   :language: python
   :pyobject: HelloGladier

The Gladier Client has built-in functions for automatically registering
and deploying FuncX functions and Automate Flows. Running the example
above looks like this:

.. code-block:: python

   hello_cli = HelloGladier()
   flow = hello_cli.start_flow()

Automatic registration and login are turned on by default when instantiating
``HelloGladier``. See REFERENCE NEEDED for more information.

``hello_cli.start_flow()`` will fetch all the tools needed, register funcx
functions, generate default input for each tool, register the Automate Flow,
and start it.

Running A Gladier Tool
----------------------

A full code snippet for running everything above is here:

.. literalinclude:: gladier_example.py
   :language: python

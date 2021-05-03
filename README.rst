Gladier: The Globus Architecture for Data-Intensive Experimental Research.
==========================================================================
|docs|

.. |docs| image:: https://readthedocs.org/projects/gladier/badge/?version=latest
   :target: https://gladier.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://github.com/globus-gladier/gladier/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/globus-gladier/gladier/actions/workflows/

.. image:: https://img.shields.io/pypi/v/gladier.svg
    :target: https://pypi.python.org/pypi/gladier

.. image:: https://img.shields.io/pypi/wheel/gladier.svg
    :target: https://pypi.python.org/pypi/gladier

.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :alt: License
    :target: https://opensource.org/licenses/Apache-2.0

Gladier is a programmable data capture, storage, and analysis architecture for experimental facilities.
The architecture leverages a data/computing substrate based on 
data and compute agents deployed across computer and storage 
systems at APS, ALCF, and elsewhere, all managed by cloud-hosted Globus services.

Installation
============

Gladier requires Python 3.6 and higher. For a modern version of python,
see the official `Python Installation Guide <https://docs.python-guide.org/starting/installation/>`_.

The easiest way to get Gladier is through Pip on PyPi. Gladier is built with two
main packages, the core Gladier client and Gladier Tools. Gladier Tools include
a set of reusable, common operations. Installing it is highly recommended.

With pip installed, you can do the following:


.. code-block:: bash

   pip install gladier gladier-tools

See the `Read-The-Docs <https://gladier.readthedocs.io/en/stable/?badge=stable>`_ getting started.
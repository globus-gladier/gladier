Awkward Conversations: Handling Exceptions
==========================================


When a funcx function throws an exception, it will be serialized
and returned. Gladier will then deserialized the exception for you.
This module demonstrates that functionality.

Hello Exception Tool
----------------------

.. autoclass:: gladier.tools.hello_world.HelloException
   :show-inheritance:

.. literalinclude:: ../../../gladier/tools/hello_world/hello_exception.py
   :language: python
   :pyobject: HelloException



Try It Out
----------

.. literalinclude:: hello_world_exception.py
   :language: python
Hello Conversations: Chaining Input
===================================

This module demonstrates running more complex tools that
pass input to one another. It contains multiple funcx functions
with their own inputs, with two functions depending on output
from the first.


Hello Conversation Tool
-----------------------

.. autoclass:: gladier.tools.hello_world.HelloConversation
   :show-inheritance:

.. literalinclude:: ../../../gladier/tools/hello_world/hello_conversation.py
   :language: python
   :pyobject: HelloConversation

Try It Out
----------

.. literalinclude:: hello_world_conversation.py
   :language: python
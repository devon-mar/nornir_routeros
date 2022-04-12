Connections
===========

.. automodule:: nornir_routeros.plugins.connections
   :members:

.. topic:: Usage

   If you need to disable SSL (e.g. during initial provisioning), you can use
   set ``use_ssl`` to ``False`` in your inventory's connection options:

.. code-block:: yaml
   :linenos:

   labMT:
     hostname: 192.0.2.1
     platform: routeros
     port: 8728
     connection_options:
       routerosapi:
         extras:
           use_ssl: False

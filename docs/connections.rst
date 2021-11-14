Connections
===========

.. automodule:: nornir_routeros.plugins.connections
   :members:

.. topic:: Usage

   If you need to disable SSL (e.g. during initial provisioning) you need to
   specify the routerosapi driver under connection options, an example on a
   host follows this can just as easily be assigned to a group to use across
   multiple devices:

.. code-block:: yaml
   :linenos:

   labMT:
     hostname: 172.16.1.1
     platform: routeros
     port: 8728
     connection_options:
       routerosapi:
         extras:
           use_ssl: False

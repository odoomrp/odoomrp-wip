.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
MRP Production machine location
===============================
If the work order has a work center that has a machine defined, and this
machine has definied a location:

* The origin location of the products to consume in the work order, will be
  the location of the machine.

And in the work order in which the product is produced, has a machine defined,
and this machine has definied a location:

* The destination location of the product to be produced, will be the location
  of the machine.


In a production order if a product to consume is in a workorder and this
workorder has a machine with a location defined, that product will be taken
from that location.

In a similar way, the destination location of the produced products will be the
location of the machine in the workorder checked as "to produce".

Credits
=======

Contributors
------------
* Ana Juaristi <ajuaristo@gmail.com>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>

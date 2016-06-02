.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
MRP repair analytic
===================
This module performs the following:

* It creates a new field 'Analytic Account' in the object MRP Repair.

* It creates a new field 'User' in the operations, and components of the repair
  order.

* Configuration group which defines if a user can decide if a repair cost is
  going to be created or not.

* When the repair order is confirmed, for each line of operations and 
  components checked as "Load Cost", will create one analytic line.

* When the invoice is created, will take analytic account of repair, and takes
  it to the invoice line.

Credits
=======


Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <ajuaristio@gmail.com>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Ainara Galdona <ainaragaldona@avanzosc.es>
* Esther Martín <esthermartin@avanzosc.es>

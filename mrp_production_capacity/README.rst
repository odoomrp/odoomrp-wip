Capacity in manufacturing
=========================

This module performs the following:

* In routing operations, a boolean flag 'Limited Production Capacity' is added.
* In machine object, two fields, Capacity per Cycle Max. and Capacity per Cycle
  Min are added
* In the MO, when selecting a routing,  the quantity to manufacture is assigned
  by default based on the capacity per cycle of the machine defined in the
  routing.
* If the user manually switches the quantity to be produced, a verification is
  made that such quantity is actually between the minimum and maximum machine
  default values, and if not ... a warning is raised.
* In WO, a function is added which verifies whether the amount of the WO is
  between the capabilities of the new machine assigned to it, if not ... a
  warning is raised that the user has to change the quantity in the WO.

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>


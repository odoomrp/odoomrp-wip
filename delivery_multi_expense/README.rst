Delivery multi expense
======================
This module allows you to define in sales orders, other expenses that are not
transportation, using delivery methods like the one defined in the module
delivery.

Usage
=====
We may indicate in the "Delivery Method" object, if it is a transport or not.
In the "Delivery method" field of the sales order, we will only be able to
select those whose "Is transport" flag is checked.
In the "Other expenses" field of the sales order, we will only be able to 
select those whose "Is transport" flag is not checked.

Known issues / Roadmap
======================
* These other expenses are not propagated nor handled on stock pickings, so 
  you have to add them as sale order lines (with the button) for using them.

Credits
=======


Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <ajuaristo@gmail.com>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>

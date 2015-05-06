MRP Final Product Lot
=====================

This module automatically creates the lot to the final product of the
production order.

In the MRP production object, two new fields are added: Manual Production
Lot of type char, and Concatenate Lots Components of type boolean.

The lot code is generated:

1.- If the new field Manual Production lot has value: This data, if not the
order number.
2.- If the check Concatenate Lots Components, this clicked, to the previous
point code is concatenated all lot numbers of all components used to
make the final product.

Credits
=======

Contributors
------------

* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>


MRP BoM by Percentage
=====================

This module performs the following:

Include in the header of the BoM list, two new fields:

1.- **Produce by percentage**: Type boolean, when you check this new field,
 the quantity to be produced is 100, and the field 'amount to
 produce' will be invisible.

2.- **QTY to consume**: Calculated field. Displays the sum of all amounts
 to consume.

If the BoM list is by_percentage, will be validated that the new field
'QTY to consume' is not greater than 100.

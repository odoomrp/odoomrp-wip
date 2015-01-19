Quality control claim
=====================

If the test has lines at different stages of Ok, a claim is automatically
generated, to accomplish this, we have defined the field 'Automatic Claims',
in "test", and "inspection" objects.

It also defined the field "Automatic Claims by line", when this fiels is
checked, and the test line is in state "tolerable" or "Not tolerable",a claim
is automatically generated. To do this, this module creates two new categories
of claims: 'CR' and 'IDI'. If the test line status is 'tolerable,' a claim of
category IDI is created, when the test line status is "Not tolerable", a claim
of category NC is created.

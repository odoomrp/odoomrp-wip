MRP repair analytic
===================
    This module performs the following:

    1.- It creates a new field 'Analytic Account' in the object MRP Repair.

    2.- It creates a new field 'User' in the operations, and components of
        the repair order.

    3.- Configuration group which defines if a user can decide if a repair
        cost is going to be created or not.

    When the repair order is confirmed, for each line of operations and
    components checked as "Load Cost", will create one analytic line.

    When the invoice is created, will take analytic account of repair, and
    takes it to the invoice line.


    This module performs the following:

    1.- In route operations add a flag 'Limited Production Capacity', of type
        boolean.

    2.- In machin object define two fields: Capacity per Cycle Max., and
        Capacity per Cycle Min.

    3.- In the OF, selecting route, assigned as default amount to manufacture
        the capacity per cycle of the machine is assigned default this
        operation routing.

    4.- If the user switches to hand the quantity to be produced, verify that
        it is between the minimum and maximum machine default the same
        operation, and if not ... give a warning.

    5.- IN OT (WorkOrder) put a onchange on the machine, changing verify
        whether the amount of the OF is between the capabilities of the new
        machine assigned in it, if not ... give notice that they have to change
        the amount in the OF.

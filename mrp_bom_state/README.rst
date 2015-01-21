MRP - BoM state
===============

This module performs the following:

1.- In the MRP BoM list object, 3 new fields are added:

    1.1.- Historical Date, of type date.
    1.2.- Allow re-edit the BoM list. If this field is clicked, you can move
          from "active" status, to "draft" status.
    1.3.- Status, of type selection, with these values: draft, in active
          and historical. This new field has gotten because it has added a
          workflow to MRP BoM list object.

You can only modify the components and / or production process if it is in
draft status. The other fields can only be changed if they are not in
historical state.
when the MRP BoM list is put to active, a record of who has activated,
and when will include in chatter/log.
It also adds a constraint for the sequence field to be unique.

MRP - BoM state
===============

This module provides a state in the LdM whether to allow their use in
manufacturing, to do the following states are defined:

1.- Draft.....: The form will be available for data entry, and may move to 
                "active" state.
2.- Active....: You can modify all of the form fields except for the fields:
                routing, BoM lines, and the new field Active, for false default
                when you create a new BoM.
                The "active" state may be passed back to state "draft", if we
                mark the new field "Allow re-edit the BoM list".
                The active state may move to state "Historical".
3.- Historical: This is the last state of the LdM, you can not change any field
                on the form.

when the MRP BoM list is put to active, a record of who has activated, and when
will include in chatter/log. It also adds a constraint for the sequence field
to be unique.

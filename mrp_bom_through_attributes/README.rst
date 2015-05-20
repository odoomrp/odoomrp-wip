Add raw materials attached to product attribute values
======================================================

This module adds a new field "Raw material" on product attributes values,
with its quantity, that can be put in any product that is intended to be
manufactured.

When you create a manufacturing order for this product, these attributes are
populated as raw materials like if they were in the product bill of material.

Know issues / Roadmap
=====================

* In order to make a production order of a product. You need to have at least
  an empty BoM for it, although you have set raw materials on its attributes.

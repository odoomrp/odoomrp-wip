.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Product Variants
================

This module creates a check in categories and an option in product templates,
so that it does not create the product variants when the attributes are
assigned. This is used by those modules that create the product when it is
estrictly necessary.

Known issues / Roadmap
======================

* On product configurator abstraction, retrieve automatically already defined
  domains on product_id field on inherited class.
* Old onchange methods for product_id field must be called from the object
  instance (not from the model handler - self.pool['model_name'] or
  self.env['model_name'] -), or they will raise an error.

Credits
=======

Contributors
------------
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciobaeza.com>
* Ana Juaristi <ajuaristio@gmail.com>

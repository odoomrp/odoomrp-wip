.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

========================
Product pricelist import
========================

* This module allows to load product price list from a file. The file format
  must have these colummns:
    keys = ['code', 'info', 'price', 'discount_1', 'discount_2', 'retail',
            'pdv1', 'pdv2']
* To search for the product, you can use the "code" (product code), or the
  "info" (product name).
* If the "supplier info" exists, it modifies its price, if "supplier info" not
  exists, create a new one with the new price.

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Daniel Campos <danielcamops@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>

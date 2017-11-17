.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Purchase Homologation
=====================

This module restricts making purchase orders if you don't register an
homologation record. This record can be filled with:

* Supplier and product, so the purchase is allowed for that supplier and the
  concrete product.
* Supplier and product category, so the authorization extends to all the
  products of the category or its child categories for that supplier.
* Only product or product category, allowing to purchase the product or
  products within category for any supplier.
* Start and end date that restrict the homologation to that interval of time.

You can also set the permission "Bypass purchase homologation" to certain users
to not restrict the creation of the purchase order, but only warn about the
lack of the homologation.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/188/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/odoomrp/odoomrp-wip/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
* Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>

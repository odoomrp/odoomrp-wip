.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

MRP - BoM version
=================

This module adds a version control to the Bill of Materials (BoM) and allows
 to control its life cycle.

[es_ES] Este módulo tiene como objetivo el añadir el control de versiones a
la Lista de Materiales (LdM) y controlar su ciclo de vida.

Configuration
=============

In *Configuration > Configuration > Manufacturing*, field "Allow re-edit the
 BoM list" will allow you to define whether a BoM in  "Active" state can be
 changed back to "Draft".

[es_ES] En *Configuración > Configuración > Manufacturing*, campo *Permitir
re-editar las listas de materiales* permite definir si una LdM en estado
"Activa" puede cambiar a "Borrador".

Usage
=====
Manage the life cycle of a BoM
------------------------------
When you create a new BoM it will be set to a state "Draft". In this state
you are allowed to define it. BoM's in this state remain inactive (field
"Active" is set to "False" by default), and therefore not available for use
in manufacturing orders, nor listed by default. If you want to search for
inactive BoM's you'll have to explicitly indicate so in the search.

When you want use in manufacturing orders, you can move it to state "Active".
It will then appear by default in BoM searches. The chatter/log will
indicate who activated the BoM and when did this happen.

In the state "Active" a BoM can still be edited, but with restrictions. Fields
"Routing", "BoM lines", "Active" cannot be changed.

The life cycle of a BoM ends when you move it to the field "Historical". In
this state the BoM is no longer available for use

From state "Active" it is possible to move to state "Historical". This is
the last state of the LdM, you can not change any field on the form.

[es_ES] Cuando se crea una nueva LdM, esta se establecerá en el estado
"Borrador". En este estado la LdM puede ser definida. Las LdM en este estado
 se mantienen inactivas (campo "Activa" con valor "Falso" por defecto), y no
  podrá usarse en órdenes de fabricación, ni aparecerá en las búsquedas por
  defecto. Si se desea buscar por LdM inactivas, habrá que indicarlo
  expícitamente en la búsqueda.

Cuando desees usar la LdM en órdenes de producción, podrás cambiar su estado
 a "Activa". Entonces también aparecerá por defecto en las búsquedas de LdM.
  El historial de modificación mostrará quién activó la LdM, y cuándo.

En el estado "Activa", la LdM aún puede ser editada, aunque con
restricciones. Los campos "Ruta", "Líneas LdM", "Activa" no pueden ser
modificados.

Desde el estado "Activa" es posible cambiar al estado "Histórica". Este es
el último estado de la LdM, en el que ya no será posible cambiar ningún
campo.


Version control
---------------
The version control of a BoM is defined by the ability to historify a BoM. By
 clicking the button "New Version", the BoM is moved to state "Historical",
 and a new BOM is created, based on the previous one, with a new version
 number.

[es_ES] El control de versiones de la LdM se define por su habilidad de ser
historificada y poder crear nuevas versiones a partir de una LdM. Al pulsar
el botón "Nueva Versión", la LdM cambia al estado "Histórica" y se crea una
nueva LdM, a partir de la anterior, con un nuevo número de versión.


Credits
=======

* odooMRP Project, www.odoomrp.com

Contributors
------------

* Eficent, www.eficent.com

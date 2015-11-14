==========================
Samples on quality control
==========================

This module allows to set sample ranks to be informed on each quality control
inspection depending on the quantity of products of the source of the
inspection.

Configuration
=============

Go to Quality control > Tests > Sample ranges, and define a range template
where you specify under a name the quantity intervals and the samples taken
for that interval.

Then, go to Quality control > Tests > Tests and select that sample definition
for a test.

Usage
=====

If you use a test that has a sample definition, the quantity will be taken
into account for duplicating all the lines of the test as many times as
the corresponding samples taken according the quantity, and having them
numerated in the column "# sample".

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciobaeza.com>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Ana Juaristi <ajuaristio@gmail.com>

Estimated costs in manufacturing orders
=======================================

With this module when a production order is confirmed, some analytic lines
are automatically generated, in order to estimate the costs of the production
order.

At the same time, the estimated allocation of materials, machinery operators
and costs will be made.

In materials case, an analytic line will be generated for each material to
consume in the order. For operators imputation in each operation, it will
be generated one line, so that the number of lines will be equal to the number
of operators in the operation. In machines case, there will be created two
analytic lines for each operation in the associated routing, one per hour cost
and the other per cycle cost.

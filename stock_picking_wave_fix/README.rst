Fixes 2 problems on stock_picking_wave module

1. There is a process that launches a raise if the movements of pickings
are already done or canceled. At grouping is not appropriate to do this

2. When generate the wave, all the pickings are transferred as are, 
without giving the opportunity to change their data.
This module raise an advice if at less one of the pickings of the wave 
are not transfered. 
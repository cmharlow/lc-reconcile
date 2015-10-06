##About

An OpenRefine reconciliation service for the Library of Congress Subject Headings and the Library of Congress Name Authority File available via id.loc.gov.

**Tested with, working on python 2.7.10, 3.4.3**

Hosted version at https://lc-reconcile.herokuapp.com/

To run the hosted version:

1. start OpenRefine (**LODRefine is NOT required)
2. find column you want to reconcile
3. go to Reconcile > Start reconciling...
4. click on 'Add standard service button' in bottom left corner of reconciliation dialog box that appears
5. Enter the service's URL: enter the above URL - https://lc-reconcile.herokuapp.com/
6. Click Add Service.
7. /lc searches LCNAF and LCSH, other options just search the one chosen
8. click 'start reconciling'.

Lots of improvements to this forthcoming, but needed basic service like yesterday for massive metadata migration project we're doing.

##Provenance

Michael Stephens wrote a [demo reconcilliation service](https://github.com/mikejs/reconcile-demo) and Ted Lawless wrote a [FAST reconciliation service](https://github.com/lawlesst/fast-reconcile) that this code modifies and builds off of.

##Special Notes

TBW

##Instructions

Runs directly on localhost:5000 (no /reconcile needed for this recon service)

##Plans for Improvement

Getting to work with skos:altLabels for match points. I WILL GET THAT TO WORK.

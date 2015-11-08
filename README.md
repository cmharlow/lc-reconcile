##About

An OpenRefine reconciliation service for the Library of Congress Subject Headings and 
the Library of Congress Name Authority File available via [id.loc.gov](http://id.loc.gov).

**Tested with, working on python 2.7.10, 3.4.3**

See **Special Notes**, below, to explain the use of the various [id.loc.gov](http://id.loc.gov) data APIs in this service.

See the [OpenRefine Standard Reconciliation Service API documentation (admittedly out of date)](https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API) 
 and [my own presentation notes on building an OpenRefine Reconciliation Service (admittedly, from POV of a non-developer)](https://github.com/cmh2166/c4lMDCpres)
 to gather some understanding about what this OpenRefine Reconciliation Service attempts to do.
 
As ever, I'm writing this from the viewpoint of a metadataist who had a need to fill for work projects, not a developer 
with the ability or time to make something perfect. Improvements, corrections or suggestions are greatly welcomed.

##Hosted Version Instructions

Hosted version at [https://lc-reconcile.herokuapp.com/](https://lc-reconcile.herokuapp.com/). 
This works, but easily gets overloaded. For big recon jobs, its recommended to download this repo and run locally. See 
the **Run Locally** section below.

To run the hosted version:

1. Start OpenRefine (**LODRefine is NOT required, though it also works for this).
2. Find column you want to reconcile.
3. Go to Reconcile > Start reconciling...
4. Click on 'Add standard service button' in bottom left corner of reconciliation dialog box that appears.
5. Enter the service's URL: enter the above URL - https://lc-reconcile.herokuapp.com/
6. Click Add Service.
7. /LoC searches LCNAF and LCSH, other options just search the one chosen.
8. Click 'start reconciling'.

##Run Locally Instructions

Runs directly on localhost:5000 (no /reconcile needed for this recon service)

##Provenance

Michael Stephens wrote a [demo reconciliation service](https://github.com/mikejs/reconcile-demo) and 
Ted Lawless wrote a [FAST reconciliation service](https://github.com/lawlesst/fast-reconcile) 
that this code modifies and builds off of.

All of the access to [id.loc.gov](http://id.loc.gov/) that this OpenRefine Reconciliation service builds off of is 
indebted to those who made/make id.loc.gov an option. Special thanks to Kevin Ford for reaching out and helping with 
understanding the various id.loc.gov query options.

##Special Notes

This service runs off a number of ways to access Library of Congress Name Authority File and Subject Headings through [id.loc.gov](http://id.loc.gov/).

I'm not an expert in how these services work, just an enthusiastic fan who needed an OpenRefine LCNAF reconciliation service
(and one that didn't build off the VIAF API, as VIAF doesn't contain the full LCNAF) to get a project done. The following
is not meant to be documentation on the id.loc.gov possibilities, but just explain my understanding of them and how they 
are used in this service.

The test case for the following examples is the musician [Prince](http://id.loc.gov/authorities/names/n84079379), aka TAFKAP (among other alternate names).
 
(If you want to test the following yourself, and aren't sure how, check out [Postman Chrome Add-on](https://www.getpostman.com/), 
though most of these can be tested by entering in your web browser.)

###id.loc.gov/authorities/label/QUERY

Content negotiation built into id.loc.gov means that this URL pattern, when QUERY exactly matches either a preferred label/heading 
or an alternate label/heading/cross-reference, will return the id.loc.gov record for the preferred label. If QUERY does 
not exactly match either a preferred label or an alternate label, it returns the id.loc.gov record for that entity's authority.

The default response is the HTML id.loc.gov record, though you can also receive RDF/XML, Json-LD, and possibly other formats in response. 
This service uses the RDF/XML response.

You do not need to indicate the particular authority file (names or subjects) in the URL for this to work, though you can 
indicate either if you just want responses for headings from either the NAF or the LCSH.

####Examples

* http://id.loc.gov/authorities/label/Prince
* http://id.loc.gov/authorities/label/TAFKAP
* http://id.loc.gov/authorities/names/label/Prince
* http://id.loc.gov/authorities/names/label/TAFKAP

All of the above, entered without other information into a web browser, return http://id.loc.gov/authorities/names/n84079379.html.

* http://id.loc.gov/authorities/subjects/label/Prince
* http://id.loc.gov/authorities/subjects/label/TAFKAP

The above, entered without other information into a web browser, return 'No matching term found - authoritative, variant, or deprecated - for Prince' 
as Prince is in the Name Authority File, not the Subject Headings.

* http://id.loc.gov/authorities/label/Prince
* http://id.loc.gov/authorities/label/TAFKAP
* http://id.loc.gov/authorities/names/label/Prince
* http://id.loc.gov/authorities/names/label/TAFKAP

A HTTP Get request for any of the above URLs issued with the header parameter Accept: application/rdf+xml will return the 
RDF/XML representation of the record with URI http://id.loc.gov/authorities/names/n84079379.

A HTTP Get request for any of the above URLs issued with the header parameter Accept: application/json will return the 
JSON-LD representation of the record with URI http://id.loc.gov/authorities/names/n84079379.

* http://id.loc.gov/authorities/subjects/label/Prince
* http://id.loc.gov/authorities/subjects/label/TAFKAP

A HTTP Get request for any of the above URLs issued with any header parameter Accept will still return the above 'No matching term found...'
text as well as a 404-Not found.

Any URL with a part of the label will return a 404 Not found - this only works with exact matches.

###id.loc.gov/authorities/suggest/?q=QUERY

This is a service built into id.loc.gov that returns a number of top matches for QUERY from id.loc.gov. 

As far as I can tell, Suggest only returns matches based off of a preferred label/heading, not for alternate labels/headings/cross-references (see the examples below).

It will return a JSON list of arrays, the first array being the preferred labels for the found top matches, the second array
being the number of results for each entity of the labels in the the first array, the third being the URIs for the authorities
for each label in the first array. Here is a simplified explanation of the output:

```json
[
  "QUERY",
  [
    "QUERY Matched Label 1",
    "QUERY Matched Label 2",
    "QUERY Matched Label 3",
    "QUERY Matched Label 4",
    "QUERY Matched Label 5",
    "QUERY Matched Label 6",
    "QUERY Matched Label 7",
    "QUERY Matched Label 8",
    "QUERY Matched Label 9",
    "QUERY Matched Label 10"
  ],
  [
    "1 result",
    "1 result",
    "1 result",
    "1 result",
    "1 result",
    "1 result",
    "1 result",
    "1 result",
    "1 result",
    "1 result"
  ],
  [
    "http://id.loc.gov/authorities/names/label1URI",
    "http://id.loc.gov/authorities/names/label2URI",
    "http://id.loc.gov/authorities/names/label3URI",
    "http://id.loc.gov/authorities/names/label4URI",
    "http://id.loc.gov/authorities/names/label5URI",
    "http://id.loc.gov/authorities/names/label6URI",
    "http://id.loc.gov/authorities/names/label7URI",
    "http://id.loc.gov/authorities/names/label8URI",
    "http://id.loc.gov/authorities/names/label9URI",
    "http://id.loc.gov/authorities/names/label10URI"
  ]
]
```

You do not need to indicate the particular authority file (names or subjects) in the URL for this to work, though you can 
indicate either if you just want responses for headings from either the NAF or the LCSH.

####Examples

* http://id.loc.gov/authorities/suggest/?q=Prince
* http://id.loc.gov/authorities/names/suggest/?q=Prince

Both of the above, entered without other information into a web browser, return the following:

```json
[
"Prince",
[
"PRINCE Programme",
"Prince",
"Prince & Co. (Nigeria)",
"Prince & Docker (Liverpool, England)",
"Prince & me",
"Prince (Ship)",
"Prince Agbodjan, Joseph L.",
"Prince Albert (Musical group)",
"Prince Albert (Sask.)",
"Prince Albert (Ship)"
],
[
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result"
],
[
"http://id.loc.gov/authorities/names/no99017484",
"http://id.loc.gov/authorities/names/n84079379",
"http://id.loc.gov/authorities/names/no2002049690",
"http://id.loc.gov/authorities/names/n2012037490",
"http://id.loc.gov/authorities/names/no2004051678",
"http://id.loc.gov/authorities/names/n2006017735",
"http://id.loc.gov/authorities/names/no2005062452",
"http://id.loc.gov/authorities/names/no2006097687",
"http://id.loc.gov/authorities/names/n82032086",
"http://id.loc.gov/authorities/names/n86856559"
]
]
```

Note the results can change for names versus subjects versus searching both, however. But, as there are preferred labels matching the query
'Prince' in both LCSH and LCNAF (including the Prince we're searching), performing a Suggest search with QUERY 'Prince' for
either names or both returns suggestions with our Prince included.

* http://id.loc.gov/authorities/subjects/suggest/?q=Prince

The above, entered without other information into a web browser, return matches that don't include the Prince we're searching for, 
as it includes results only from the LCSH. However, as there are terms that match/contain the query term 'Prince' in LCSH, it 
returns those. Below is the response:

```json
[
"Prince",
[
"Prince Albert Hills (Nunavut)",
"Prince Albert National Park (Sask.)",
"Prince Charles Mountains (Antarctica)",
"Prince Creek Formation (Alaska)",
"Prince Edward Island (Prince Edward Islands)",
"Prince Edward Island National Park (P.E.I.)",
"Prince Edward Islands",
"Prince Edward's Bastion (England)",
"Prince Gallitzin State Park (Pa.)",
"Prince George's County (Md.)--Maps"
],
[
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result",
"1 result"
],
[
"http://id.loc.gov/authorities/subjects/sh85106711",
"http://id.loc.gov/authorities/subjects/sh2010013966",
"http://id.loc.gov/authorities/subjects/sh92006770",
"http://id.loc.gov/authorities/subjects/sh91002523",
"http://id.loc.gov/authorities/subjects/sh85106713",
"http://id.loc.gov/authorities/subjects/sh2002010534",
"http://id.loc.gov/authorities/subjects/sh85106714",
"http://id.loc.gov/authorities/subjects/sh2011004575",
"http://id.loc.gov/authorities/subjects/sh85106716",
"http://id.loc.gov/authorities/subjects/sh2008116644"
]
]
```

* http://id.loc.gov/authorities/subjects/suggest/?q=TAFKAP
* http://id.loc.gov/authorities/suggest/?q=TAFKAP

The above, entered without other information into a web browser, return matches that don't include the Prince we're searching for. 
 In fact, querying TAFKAP returns no results whatsoever, although it is a captured cross-reference/alternate label in the LCNAF 
 authority record for Prince. See the response below:
 
```json
[
"TAFKAP",
[ ],
[ ],
[ ]
]
```

###id.loc.gov/authorities/[names|subjects]/didyoumean/?label=QUERY

##Plans for Improvement

There are lots of improvements and repairs to this code forthcoming, but I needed a basic LCNAF Openrefine Recon Service 
like yesterday for a massive metadata migration project. Please submit pull requests and/or issues on this for any 
improvements or bugs found. 

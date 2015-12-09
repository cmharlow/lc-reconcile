##About

An OpenRefine reconciliation service for the Library of Congress Subject Headings and the Library of Congress Name Authority File available via [id.loc.gov](http://id.loc.gov).

**Tested with, working on python 2.7.10, 3.4.3. It works, but expect bugs. I needed for a particular project, the need is passed, but want to get this cleaned up for others to easily use. Please add issues or comments as able.**

See **Special Notes**, below, to explain the use of the various [id.loc.gov](http://id.loc.gov) data APIs in this service.

See the [OpenRefine Standard Reconciliation Service API documentation (admittedly out of date)](https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API) and [my own presentation notes on building an OpenRefine Reconciliation Service (admittedly, from POV of a non-developer)](https://github.com/cmh2166/c4lMDCpres)to gather some understanding about what this OpenRefine Reconciliation Service attempts to do.
 
As ever, I'm writing this from the viewpoint of a metadataist who had a need to fill for work projects, not a developer with the ability or time to make something perfect. Improvements, corrections or suggestions are greatly welcomed.

##Hosted Version Instructions

Hosted version at [https://lc-reconcile.herokuapp.com/](https://lc-reconcile.herokuapp.com/). This works, but easily gets overloaded. For big recon jobs, its recommended to download this repo and run locally. See the **Run Locally** section below.

**Second hosted version available for testing: [http://lc-reconcile.cmh2166.webfactional.com/](http://lc-reconcile.cmh2166.webfactional.com/). Please try it out and report back to Christina - @cm_harlow, cmharlow at gmail dot com. Consider this second URL the hosted version for now; the heroku hosted version, above, will be removed in the near future.**

To run the hosted version:

1. Start OpenRefine (**LODRefine is NOT required, though it also works for this).
2. Find column you want to reconcile.
3. Go to Reconcile > Start reconciling...
4. Click on 'Add standard service button' in bottom left corner of reconciliation dialog box that appears.
5. Enter the service's URL: enter the above URL - http://lc-reconcile.cmh2166.webfactional.com/
6. Click Add Service.
7. /LoC searches LCNAF and LCSH, other options just search the one chosen.
8. Click 'start reconciling'.

##Run Locally Instructions

Runs directly on localhost:5000 (no /reconcile needed for this recon service)

Before getting started, you'll need python on your computer (this was built with python 2.7.8, updated to work with python3.4, most recently tested and worked with python 2.7.10 and 3.4.3) and be comfortable using LODRefine/OpenRefine/Google Refine.

1. Clone/download/get a copy of this code repository on your computer.
2. In the Command Line Interface, change to the directory where you downloaded this code: `cd directory/with/code/`
3. Install the requirements needed: `pip install -r requirements.txt` (note, I'm updating that to reflect what is currently used - expect bugs + bumps + beautiful mistakes on my part right now).
4. Type in: `python reconcile.py --debug` (you don't need to use debug but this is helpful for knowing what this service is up to while you are working with it). 
5. You should see a screen telling you that the service is `Running on http://0.0.0.0:5000/`
6. Leaving that terminal window open and the service running, go start up OpenRefine (however you normally go about it). Open a project in OpenRefine.
7. On the column you would like to reconcile with LCNAF or LCSH (or both), click on the arrow at the top, choose 
`Reconcile` > `Start Reconciling...`
8. Click on the `Add Standard Service` button in the bottom left corner.
9. Now enter the URL that the local service is running on - if you've changed nothing in the code, it should be `http://0.0.0.0:5000/`. Click Add Service. If nothing happens upon entering `http://0.0.0.0:5000/`, try `http://localhost:5000/` or `http://127.0.0.1:5000/` instead.
10. You should now be greeted by a list of possible reconciliation types for the LC Reconciliation Service. They should be fairly straight-forward to understand, and use /LoC if you want to search LCNAF and LCSH together.
11. Click `Start Reconciling` in the bottom right corner.
12. Once finished, you should see the closest options that the LC Services, grouped, found for each cell. You can click on the options and be taken to the id.loc.gov site for that entity's authority. Once you find the appropriate reconciliation choice, click the single arrow box beside it to use that choice just for the one cell, or the double arrows box to use that choice for all other cells containing that text.
13. Once you've got your reconciliation choices done or rejected, you then need to store the LC label and URI (or any subset of those that you want to keep in the data) in your OpenRefine project. This is important:

**Although it appears that you have retrieved your reconciled data into your OpenRefine project, OpenRefine is actually storing the original data still. You need to explicit save the reconciled data in order to make sure it appears/exists when you export your data.**

So, depending on whether or not you wish to keep the original data, you can replace the column with the reconciled data or add a column that contains the reconciled data. I'll do the latter here. On the reconciled data column, click the  arrow at the top, then Choose `Edit Columns` > `Add a new column based on this column`
14. In the GREL box that appears, put the following depending on what you want to pull:

* Label only: `cell.recon.match.name`
* URI: `cell.recon.match.id`
* Label and URI each separated by | (for easier column splitting later): `cell.recon.match.name + " | " + cell.recon.match.id`

When you're down, shut down OpenRefine as you normally would. Go to the terminal where the LC Reconcile service is running and type in cntl + c. This will stop the service. Shut down the terminal window.

Let me know if you have questions - email is charlow2(at)utk(dot)edu and Twitter handle is @cm_harlow

##Plans for Improvement

There are lots of improvements and repairs to this code forthcoming, but I needed a basic LCNAF Openrefine Recon Service like yesterday for a massive metadata migration project. Please submit pull requests and/or issues on this for any improvements or bugs found. 

I do want to add a new service that can handle in-OpenRefine-project search refinements. The documentation sucks on thisfunctionality for OpenRefine or the no-longer-existent Freebase API that it was built off of, so if you have any advice on this, please do let me know.

##Provenance

Michael Stephens wrote a [demo reconciliation service](https://github.com/mikejs/reconcile-demo) and Ted Lawless wrote a [FAST reconciliation service](https://github.com/lawlesst/fast-reconcile) that this code modifies and builds off of.

All of the access to [id.loc.gov](http://id.loc.gov/) that this OpenRefine Reconciliation service builds off of is 
indebted to those who made/make id.loc.gov an option. Special thanks to Kevin Ford for reaching out and helping with understanding the various id.loc.gov query options.

##How This Service Handles Your Query

This service takes the query from your OpenRefine project - i.e. the terms you have listed in your chosen column for reconciliation in your OpenRefine project - and according to the index you choose, works in this way at the moment:

###For the LoC index (search LCNAF and LCSH at same time):

1. Normalize the query with the text.py normalize function, edited for LC headings peculiarities.
2. Run the query against the id.loc.gov Suggest API (see **Special Notes**) for both authorities and capture the returned possible matches based off of preferred labels.
3. Run the query against the id.loc.gov DidYouMean API (see **Special Notes**) for both names then subjects, capture the returned possible matches from both based off of alternate labels, and return all of those labels.
4. Rank all the possible matches founded in steps 2 and 3 based off of fuzzy wuzzy matching/rankings between the original, normalized query and the normalized returned labels.
5. Return the top 3 results from step 4, along with their URIs.

###For the LCNAF:

1. Normalize the query with the text.py normalize function, edited for LC headings peculiarities.
2. Run the query against the id.loc.gov Suggest API (see **Special Notes**) for names only and capture the returned possible matches based off of preferred labels.
3. Run the query against the id.loc.gov DidYouMean API (see **Special Notes**) for names only and capture the returned possible matches based off of alternate labels.
4. Rank all the possible matches founded in steps 2 and 3 based off of fuzzy wuzzy matching/rankings between the original, normalized query and the normalized returned labels.
5. Return the top 3 results from step 4, along with their URIs.

###For the LCSH:

1. Normalize the query with the text.py normalize function, edited for LC headings peculiarities.
2. Run the query against the id.loc.gov Suggest API (see **Special Notes**) for subjects only and capture the returned possible matches based off of preferred labels.
3. Run the query against the id.loc.gov DidYouMean API (see **Special Notes**) for subjects only and capture the returned possible matches based off of alternate labels.
4. Rank all the possible matches founded in steps 2 and 3 based off of fuzzy wuzzy matching/rankings between the original, normalized query and the normalized returned labels.
5. Return the top 3 results from step 4, along with their URIs.

###What I'm considering:

Adding a new step 2 for all the above cases that first sees if there is an exact match found view id.loc.gov/authorities/label API (see **Special Notes**) and if such exists, return that as a match to OpenRefine, skipping the suggest and didyoumean (i.e. the fuzzy matching) services.

###Why do this?

The above allows us to take our OpenRefine terms - which could be any manner of format/style/etc. - and get the top results based off of both preferred and alternate labels in the LCSH and LCNAF (or just one as chosen). Using one of the id.loc.gov services mentioned below alone would only allow us to:

1. find perfect matches only, missing fuzzy matching opportunities unless built out in this service
2. find fuzzy matches based off of the preferred labels/headings only, missing cross-references or alternate labels, 
3. find fuzzy matches based off of the alternate labels/cross-references only, missing out on the preferred labels.

We cannot say for all OpenRefine projects or even metadata generally (which this service is built to handle) which of the above cases only we should target; instead, we want to support all of them and get the best results from the aggregates.

##Special Notes

This service runs off a number of ways to access Library of Congress Name Authority File and Subject Headings through [id.loc.gov](http://id.loc.gov/).

I'm not an expert in how these services work, just an enthusiastic fan who needed an OpenRefine LCNAF reconciliation service (and one that didn't build off the VIAF API, as VIAF doesn't contain the full LCNAF) to get a project done. The following is not meant to be documentation on the id.loc.gov possibilities, but just explain my understanding of them and how they  are used in this service.

The test case for the following examples is the musician [Prince](http://id.loc.gov/authorities/names/n84079379), aka TAFKAP (among other alternate names).
 
(If you want to test the following yourself, and aren't sure how, check out [Postman Chrome Add-on](https://www.getpostman.com/), though most of these can be tested by entering in your web browser.)

###id.loc.gov/authorities/label/QUERY

Content negotiation built into id.loc.gov means that this URL pattern, when QUERY exactly matches either a preferred label/heading or an alternate label/heading/cross-reference, will return the id.loc.gov authority record for the entity. If QUERY does not exactly match either a preferred label or an alternate label, it returns a 404 No match found page.

The default response is the HTML id.loc.gov record, though you can also receive RDF/XML, Json-LD, and possibly other formats in response. This service uses the RDF/XML response.

You do not need to indicate the particular authority file (names or subjects) in the URL for this to work, though you can indicate either if you just want responses for headings from either the NAF or the LCSH.

####Examples

* http://id.loc.gov/authorities/label/Prince
* http://id.loc.gov/authorities/label/TAFKAP
* http://id.loc.gov/authorities/names/label/Prince
* http://id.loc.gov/authorities/names/label/TAFKAP

All of the above, entered without other information into a web browser, return http://id.loc.gov/authorities/names/n84079379.html.

* http://id.loc.gov/authorities/subjects/label/Prince
* http://id.loc.gov/authorities/subjects/label/TAFKAP

The above, entered without other information into a web browser, return 'No matching term found - authoritative, variant, or deprecated - for Prince' as Prince is in the Name Authority File, not the Subject Headings.

* http://id.loc.gov/authorities/label/Prince
* http://id.loc.gov/authorities/label/TAFKAP
* http://id.loc.gov/authorities/names/label/Prince
* http://id.loc.gov/authorities/names/label/TAFKAP

A HTTP Get request for any of the above URLs issued with the header parameter Accept: application/rdf+xml will return the RDF/XML representation of the record with URI http://id.loc.gov/authorities/names/n84079379.

A HTTP Get request for any of the above URLs issued with the header parameter Accept: application/json will return the JSON-LD representation of the record with URI http://id.loc.gov/authorities/names/n84079379.

* http://id.loc.gov/authorities/subjects/label/Prince
* http://id.loc.gov/authorities/subjects/label/TAFKAP

A HTTP Get request for any of the above URLs issued with any header parameter Accept will still return the above 'No matching term found...' text as well as a 404-Not found.

Any URL with a part of the label will return a 404 Not found - this only works with exact matches.

###id.loc.gov/authorities/suggest/?q=QUERY

This is a service built into id.loc.gov that returns a number of top matches for QUERY from id.loc.gov. 

As far as I can tell, Suggest only returns matches based off of a preferred label/heading, not for alternate labels/headings/cross-references (see the examples below).

It will return a JSON list of arrays, the first array being the preferred labels for the found top matches, the second array being the number of results for each entity of the labels in the the first array, the third being the URIs for the authorities for each label in the first array. Here is a simplified explanation of the output:

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

You do not need to indicate the particular authority file (names or subjects) in the URL for this to work, though you can indicate either if you just want responses for headings from either the NAF or the LCSH.

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

Note the results can change for names versus subjects versus searching both, however. But, as there are preferred labels matching the query 'Prince' in both LCSH and LCNAF (including the Prince we're searching), performing a Suggest search with QUERY 'Prince' for either names or both returns suggestions with our Prince included.

* http://id.loc.gov/authorities/subjects/suggest/?q=Prince

The above, entered without other information into a web browser, return matches that don't include the Prince we're searching for, as it includes results only from the LCSH. However, as there are terms that match/contain the query term 'Prince' in LCSH, it returns those. Below is the response:

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
* http://id.loc.gov/authorities/names/suggest/?q=TAFKAP
* http://id.loc.gov/authorities/suggest/?q=TAFKAP

The above, entered without other information into a web browser, return matches that don't include the Prince we're searching for. In fact, querying TAFKAP returns no results whatsoever, although it is a captured cross-reference/alternate label in the LCNAF  authority record for Prince. See the response below:
 
```json
[
"TAFKAP",
[ ],
[ ],
[ ]
]
```

###id.loc.gov/authorities/[names|subjects]/didyoumean/?label=QUERY

This is a service built into id.loc.gov that returns possible preferred labels and URIs for the top matches between QUERY and cross-reference or alternate heading in a LCNAF/LCSH authority record from id.loc.gov. 

As far as I can tell, it expects cross-reference or alternate labels for the QUERY, not the preferred headings/labels. It will return up to 10 possible matches, with record URIs and preferred labels included, along with a match score. A didyoumean QUERY that matches a preferred label will not return top results/matches based off the preferred label, but the top cross-references/alternate labels that match that QUERY instead. See the examples below.

You must select either the LCSH or the LCNAF (i.e. authorities/names or authorities/subjects in the base URL pattern) for this to work. You cannot run this service for both LCSH and LCNAF at once.

It will return a XML object, a simplified form of the response given below:

```xml
<idservice:service xmlns:idservice="http://id.loc.gov/ns/id_service#" service-name="didyoumean" search-status="success" search-hits="10" label-searched="QUERY">
<idservice:term term-type="authorized" score="##" uri="http://id.loc.gov/authorities/names/match1URI">QUERY Matched Pref Label 1</idservice:term>
<idservice:term term-type="authorized" score="##" uri="http://id.loc.gov/authorities/names/match2URI">QUERY Matched Pref Label 2</idservice:term>
<idservice:term term-type="authorized" score="##" uri="http://id.loc.gov/authorities/names/match3URI">QUERY Matched Pref Label 3</idservice:term>
...
</idservice:service>
```

####Examples

* http://id.loc.gov/authorities/names/didyoumean/?label=TAFKAP

The above, entered without other information into a web browser, returns the following, containing a reference to the authority for the Prince entity we're searching:

```xml
<idservice:service xmlns:idservice="http://id.loc.gov/ns/id_service#" service-name="didyoumean" search-status="success" search-hits="1" label-searched="TAFKAP">
<idservice:term term-type="authorized" score="13" uri="http://id.loc.gov/authorities/names/n84079379">Prince</idservice:term>
</idservice:service>
```

* http://id.loc.gov/authorities/subjects/didyoumean/?label=TAFKAP

The above, entered without other information into a web browser, returns the following - i.e. no results, as it searched the cross-references/alternate labels in the LCSH, not the LCNAF:

```xml
<idservice:service xmlns:idservice="http://id.loc.gov/ns/id_service#" service-name="didyoumean" search-status="success" search-hits="0" label-searched="TAFKAP"></idservice:service>
```

* http://id.loc.gov/authorities/didyoumean/?label=TAFKAP

The above and any such URL configuration for the didyoumean service without either names or subjects included returns a generic id.loc.gov 404 Not found (service or entity).

* http://id.loc.gov/authorities/names/didyoumean/?label=Prince

The above URL, entered without other information into a web browser, returns the following results that searching the  NAF authorities cross-references or alternate labels only, hence no result that matches the Prince we mean (which is a preferred label for that authority record):

```xml
<idservice:service xmlns:idservice="http://id.loc.gov/ns/id_service#" service-name="didyoumean" search-status="success" search-hits="10" label-searched="Prince">
<idservice:term term-type="authorized" score="13" uri="http://id.loc.gov/authorities/names/n94037457">Prince-A-Cuba (Prince Allah Cuba)</idservice:term>
<idservice:term term-type="authorized" score="9" uri="http://id.loc.gov/authorities/names/n94085428">
Prince George's Voluntary Action Center (Prince George's County, Md.)
</idservice:term>
<idservice:term term-type="authorized" score="9" uri="http://id.loc.gov/authorities/names/n2007016024">
Prince George's County Agricultural Society (Prince George's County, Md.)
</idservice:term>
<idservice:term term-type="authorized" score="9" uri="http://id.loc.gov/authorities/names/n78052654">
Prince Edward Island. Commission of Inquiry into the Purchase of Gregors-by-the-Sea Property by the Prince Edward Island Land Development Corporation and Sixty-Three (63) Acres of Land in East Royalty by the Prince Edward Island Housing Authority
</idservice:term>
<idservice:term term-type="authorized" score="7" uri="http://id.loc.gov/authorities/names/n86071268">Preston, Prince H. (Prince Hulon), 1908-1961</idservice:term>
<idservice:term term-type="authorized" score="7" uri="http://id.loc.gov/authorities/names/no2005006134">
Prince Edward Island. Laws, etc. (Acts of the General Assembly of Prince Edward Island)
</idservice:term>
<idservice:term term-type="authorized" score="5" uri="http://id.loc.gov/authorities/names/nb2010021742">
Princes Risborough Baptist Church (Princes Risborough, England)
</idservice:term>
<idservice:term term-type="authorized" score="4" uri="http://id.loc.gov/authorities/names/n88087297">
Task Force on Child Care in Prince George's County (Prince George's County, Md.)
</idservice:term>
<idservice:term term-type="authorized" score="3" uri="http://id.loc.gov/authorities/names/n2007028920">
Prince Edward Island. Laws, etc. (Revised regulations of Prince Edward Island : 1979)
</idservice:term>
<idservice:term term-type="authorized" score="2" uri="http://id.loc.gov/authorities/names/n2007016025">
Prince George's County Agricultural Society (Prince George's County, Md.). Proceedings
</idservice:term>
</idservice:service>
```

* http://id.loc.gov/authorities/subjects/didyoumean/?label=Prince

The above URL, entered without other information into a web browser, returns the following results that searching the LCSH authorities cross-references or alternate labels only, hence no result that matches the Prince we mean since it is a preferred label for that NAF, not LCSH, authority record:

```xml
<idservice:service xmlns:idservice="http://id.loc.gov/ns/id_service#" service-name="didyoumean" search-status="success" search-hits="10" label-searched="Prince">
<idservice:term term-type="authorized" score="10" uri="http://id.loc.gov/authorities/subjects/sh85106713">Prince Edward Island (Prince Edward Islands)</idservice:term>
<idservice:term term-type="authorized" score="9" uri="http://id.loc.gov/authorities/subjects/sh2010110524">
Regional planning--Maryland--Prince George's County
</idservice:term>
<idservice:term term-type="authorized" score="8" uri="http://id.loc.gov/authorities/subjects/sh2008116644">Prince George's County (Md.)--Maps</idservice:term>
<idservice:term term-type="authorized" score="7" uri="http://id.loc.gov/authorities/subjects/sh00009460">National parks and reserves--Prince Edward Island</idservice:term>
<idservice:term term-type="authorized" score="6" uri="http://id.loc.gov/authorities/subjects/sh2008109990">Princes--Austria--Biography</idservice:term>
<idservice:term term-type="authorized" score="6" uri="http://id.loc.gov/authorities/subjects/sh87003464">Prince Rupert Forest Region (B.C.)</idservice:term>
<idservice:term term-type="authorized" score="5" uri="http://id.loc.gov/authorities/subjects/sh95003062">Bays--Prince Edward Island</idservice:term>
<idservice:term term-type="authorized" score="3" uri="http://id.loc.gov/authorities/subjects/sh95001562">Indian reservations--Prince Edward Island</idservice:term>
<idservice:term term-type="authorized" score="2" uri="http://id.loc.gov/authorities/subjects/sh2008109992">Princes--Drama</idservice:term>
<idservice:term term-type="authorized" score="1" uri="http://id.loc.gov/authorities/subjects/sh2010106678">Princes--Japan--Biography</idservice:term>
</idservice:service>
```

"""
An OpenRefine reconciliation service for the id.loc.gov LCNAF/LCSH suggest/suggest2 APIs.
"""
from collections import Counter
import json
import xml.etree.ElementTree as ET
from datetime import timedelta
from operator import itemgetter
from typing import Dict, Any

import requests
from flask import Flask, request, jsonify
from rapidfuzz import fuzz
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import text

app = Flask(__name__)

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)

# If it's installed, use the requests_cache library to
# cache calls to the FAST API.
try:
    import requests_cache
    # The expire_after parameter can be used to control expiration times.
    # by default entries never expire. The cache lives in a subdirectory called lc_cache, which may grow substantially.
    http: requests.Session = requests_cache.CachedSession(cache_name='lc_cache')
    http.remove_expired_responses()  # No-op in the current configuration
except ImportError:
    http: requests.Session = requests.Session()
    app.logger.warn("No request cache found.")

http.mount("https://", adapter)
http.mount("http://", adapter)
http.headers.update({
    "User-Agent": "LCNAF Reconciliation Service - operated by {opts.operator} - source https://github.com/tfmorris/lc-reconcile "
})


BASE_URL = "https://id.loc.gov"
ENABLE_DID_YOU_MEAN = True  # Not sure this adds much value
ENABLE_SUGGEST = True
ENABLE_SUGGEST2 = False
DEFAULT_LIMIT = 5
MATCH_SCORE_THRESHOLD = 95  # Anything above this score will be considered an automatic match
REQUEST_TIMEOUT_SECONDS = 5


# Map the LoC query indexes to service types
DEFAULT_QUERY = {
    "id": "LoC",
    "name": "LCNAF & LCSH",
    "index": "/authorities"
}

# TODO There are a bunch of things which could be added here.
# We could also have separate entries for suggest2 vs suggest
REFINE_TO_LC_MAP = [{
    "id": "Names",
    "name": "Library of Congress Name Authority File",
    "index": "/authorities/names"
}, {
    "id": "Subjects",
    "name": "Library of Congress Subject Headings",
    "index": "/authorities/subjects"
}, {
    "id": "ChildrensSubjects",
    "name": "LC Children's Subject Headings",
    "index": "/authorities/childrensSubjects"
}, {
    "id": "Classification",
    "name": "Library of Congress Classification",
    "index": "/authorities/classification"
},
{
    "id": "GenreForms",
    "name": "Library of Congress Genre/Form Terms",
    "index": "/authorities/genreForms"
},
    DEFAULT_QUERY]

# Basic service metadata.
METADATA = {
    "name": "LoC Reconciliation Service",
    "defaultTypes": [{'id': item['id'], 'name': item['name']} for item in REFINE_TO_LC_MAP],
    "identifierSpace": "http://localhost/identifier",
    "schemaSpace": "http://localhost/schema",
    "view": {
        "url": "{{id}}"
    },
}

total_gets: int = Counter()  # Uncached network GETs by status code
total_cached: int = 0
total_elapsed: timedelta = timedelta(0)


def jsonpify(obj: Any):
    """
    Helper to support JSONP
    """
    try:
        callback = request.args['callback']
        response = app.make_response("%s(%s)" % (callback, json.dumps(obj)))
        response.mimetype = "text/javascript"
        return response
    except KeyError:
        return jsonify(obj)


def http_get(url: str, params: Dict[str, str]):
    """
    Send an HTTP GET request with timeout and update all our stats on reply
    """
    app.logger.debug("Making GET request to url: " + url)
    # TODO: Add rate limiting?
    resp = http.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    global total_gets, total_cached, total_elapsed
    if hasattr(resp, 'from_cache') and resp.from_cache:
        total_cached += 1
    else:
        total_elapsed += resp.elapsed
        total_gets[resp.status_code] += 1
    return resp


def build_result(name: str, query: str, query_type_meta: dict, uri: str):
    score: float = fuzz.token_sort_ratio(query, name)
    resource = {
        "id": uri,
        "name": name,
        "score": score,
        "match": score > MATCH_SCORE_THRESHOLD,
        "type": query_type_meta
    }
    app.logger.debug(f"Label is {name}. Score is {score}. URI is {uri}")
    return resource


def search(raw_query: str, query_type='/lc', limit=DEFAULT_LIMIT):
    out = []
    query: str = text.normalize(raw_query).strip()
    query_type_meta = [i for i in REFINE_TO_LC_MAP if i['id'] == query_type]
    if not query_type_meta:
        query_type_meta = DEFAULT_QUERY
    query_index = query_type_meta[0]['index']

    if ENABLE_SUGGEST:
        out.extend(get_suggest(query, query_index, query_type_meta, limit))
    if ENABLE_SUGGEST2:
        out.extend(get_suggest2(query, query_index, query_type_meta, limit))
    if ENABLE_DID_YOU_MEAN:
        out.extend(get_didyoumean(query_index, query, query_type_meta))

    # Sort this list containing preflabels and crossrefs by descending score
    sorted_out = sorted(out, key=itemgetter('score'), reverse=True)
    return sorted_out[:limit]


def get_suggest(query, query_index, query_type_meta, limit):
    """ Get the results for the primary suggest API (primary headings, no cross-refs, left-anchored)"""
    out = []
    url = BASE_URL + query_index + '/suggest/'
    params = {'q': query,
              # 'searchType': 'keyword',  # suggest2 only
              'count': limit,
              }
    resp = http_get(url, params)
    if resp.ok:
        results = resp.json()
        # Results are returned an array with 0) query term, 1) result labels, 2) results counts (always 1?), 3) URIs
        if results:
            for name, uri in zip(results[1], results[3]):
                out.append(build_result(name, query, query_type_meta, uri))
        else:
            app.logger.warn('Got malformed suggest response with empty top level array')
    return out


def get_suggest2(query, query_index, query_type_meta, limit):
    """ Get the results for the suggest2 API - all indexes, keyword search"""
    out = []
    url = BASE_URL + query_index + '/suggest2/'
    params = {'q': query,
              'searchType': 'keyword',
              'count': limit,
              }
    resp = http_get(url, params)
    if resp.ok:
        results = resp.json()
        if 'hits' in results:
            for hit in results['hits']:
                # TODO: We get a score return in hit['rank'], but it's not clear how to scale it appropriately
                out.append(build_result(hit['aLabel'], query, query_type_meta, hit['uri']))
    return out


def get_didyoumean(query_index, query, query_type_meta):
    """
    Query the XML-based Did You Mean API for additional results (cross-refs, no primary headings)
    """
    results = []
    if query_index == '/authorities':
        paths = ["/authorities/subjects", "/authorities/names", "/authorities/genreForm"]
    else:
        paths = [query_index]
    for path in paths:
        url = BASE_URL + path + '/didyoumean/'
        resp = http_get(url, {"label": query})
        if resp.ok:
            tree = ET.fromstring(resp.content)
            for child in tree.iter('{http://id.loc.gov/ns/id_service#}term'):
                results.append(build_result(child.text, query, query_type_meta, child.get('uri')))

        else:
            app.logger.error(f"Got non-success status {resp.status_code} for url {resp.url}")
    return results


@app.route("/", methods=['POST', 'GET'])
def reconcile():
    # If a 'queries' parameter is supplied then it is a dictionary
    # of (key, query) pairs representing a batch of queries. We
    # should return a dictionary of (key, results) pairs.
    queries = request.form.get('queries')
    if queries:
        queries = json.loads(queries)
        results = {}
        for (key, query) in queries.items():
            qtype = query.get('type')
            # type_strict = query.get('type_strict')  # We always assume strict typing, so this is ignored
            limit = query.get('limit')
            if not qtype:
                dump_stats()
                return jsonpify(METADATA)
            data = search(query['query'], query_type=qtype, limit=limit)
            results[key] = {"result": data}
        dump_stats()
        return jsonpify(results)
    # If neither a 'query' nor 'queries' parameter is supplied then
    # we should return the service metadata.
    return jsonpify(METADATA)


def dump_stats():
    # print(total_gets, total_cached, total_elapsed)
    if total_gets[200]:
        latency = total_elapsed / total_gets[200]
    else:
        latency = 0
    # TODO: This logging doesn't work at shutdown, perhaps using print() instead?
    app.logger.debug(
        f"Network requests: {total_gets}. Avg latency: {latency}. Cached requests: {total_cached}")


if __name__ == '__main__':
    from optparse import OptionParser

    oparser = OptionParser()
    oparser.add_option('-d', '--debug', action='store_true', default=False)
    opts, args = oparser.parse_args()
    app.debug = opts.debug
    if not args:
        print("First argument must be a string identifying the operator of this service (required by LoC)")
        exit(1)
    app.logger.debug(f'Setting operator string to "{args[0]}"')
    app.run(host='0.0.0.0')
    # TODO: The logging doesn't work in this function at shutdown
    dump_stats()

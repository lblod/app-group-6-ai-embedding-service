from SPARQLWrapper import SPARQLWrapper, JSON

SPARQL = SPARQLWrapper("https://triplestore.hackathon-ai-6.s.redhost.be/sparql")
SPARQL.setReturnFormat(JSON)

# TODO: load from file
QUERY_GET_ALL_PRODUCTS = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ipdc-lpdc: <https://productencatalogus.data.vlaanderen.be/ns/ipdc-lpdc#>

SELECT ?subject, ?title, ?description
WHERE {
    ?subject ?p ipdc-lpdc:InstancePublicServiceSnapshot .
    ?subject dcterms:title ?title .
    FILTER (lang(?title) = "nl")
    ?subject dcterms:description ?description
    FILTER (lang(?description) = "nl")
}
ORDER BY ?subject
"""

def get_all_products() -> dict:
    results_raw = query_sparql(QUERY_GET_ALL_PRODUCTS)

    products = {}
    for prod in results_raw['results']['bindings']:
        products[prod['subject']['value']] = prod['title']['value'] + " | " + prod["description"]['value']
    return products


def query_sparql(query: str):
    SPARQL.setQuery(query)
    return SPARQL.query().convert()

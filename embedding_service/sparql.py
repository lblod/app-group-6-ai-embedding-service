from escape_helpers import sparql_escape_string, sparql_escape_uri
from helpers import query, update
from string import Template

from SPARQLWrapper import SPARQLWrapper, JSON

# TODO: load from file
QUERY_GET_ALL_PRODUCTS = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ipdc: <https://productencatalogus.data.vlaanderen.be/ns/ipdc-lpdc#>

SELECT ?subject ?title ?description
WHERE {
  GRAPH <http://mu.semte.ch/graphs/public> {
    ?subject ?p ipdc:InstancePublicServiceSnapshot .
    ?subject dcterms:title ?title .
    FILTER (lang(?title) = "nl")
    ?subject dcterms:description ?description .
    FILTER (lang(?description) = "nl")
  }
}
ORDER BY ?subject
"""

def get_all_products():
    results_raw = query(QUERY_GET_ALL_PRODUCTS)

    print("We have {} products".format( len(results_raw['results']['bindings']) ))

    products = {}
    for prod in results_raw['results']['bindings']:
        products[prod['subject']['value']] = prod['title']['value'] + " | " + prod["description"]['value']

    return products

def save_product( uri, embedding ):
    template = Template("""
      PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
      INSERT DATA {
        $uri ext:hasEmbedding $embedding.
      }""")

    update( template.substitute( uri=sparql_escape_uri( uri ), embedding=sparql_escape_string( embedding ) )

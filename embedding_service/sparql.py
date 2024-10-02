from escape_helpers import sparql_escape_string, sparql_escape_uri
from helpers import query, update
from string import Template
import logging
import json

LOG = logging.getLogger(__name__)

def paginated_bindings(sparql_query, offset=0, limit=200):
    execute_query = lambda: query("{} LIMIT {} OFFSET {}".format(sparql_query, limit, offset))['results']['bindings']
    bindings = []
    last_execution = execute_query()
    while len(last_execution):
        bindings += last_execution
        offset += limit
        last_execution = execute_query()

    return bindings

def query_products_without_embedding():
    all_results = paginated_bindings("""
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX ipdc: <https://productencatalogus.data.vlaanderen.be/ns/ipdc-lpdc#>
        PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>

        SELECT ?subject ?title ?description
        WHERE {
          GRAPH <http://mu.semte.ch/graphs/public> {
            ?subject ?p ipdc:InstancePublicServiceSnapshot .
            ?subject dcterms:title ?title .
            FILTER NOT EXISTS { ?subject ext:hasEmbedding ?embedding }
            FILTER (lang(?title) = "nl")
            ?subject dcterms:description ?description .
            FILTER (lang(?description) = "nl")
          }
        }
        ORDER BY ?subject""")

    LOG.info("We have {} products".format(len(all_results['results']['bindings'])))

    products = {}
    for prod in all_results:
        products[prod['subject']['value']] = prod['title']['value'] + " | " + prod["description"]['value']

    return products

def save_embeddings( uri, embedding ):
    template = Template("""
      PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
      INSERT DATA {
        $uri ext:hasEmbedding $embedding.
      }""")
    update( template.substitute( uri=sparql_escape_uri( uri ), embedding=sparql_escape_string( embedding ) ) )

def query_embeddings():
    bindings = paginated_bindings("""PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
SELECT ?sub ?embedding
WHERE {
    ?sub ext:hasEmbedding ?embedding.
    ?sub a <https://productencatalogus.data.vlaanderen.be/ns/ipdc-lpdc#InstancePublicServiceSnapshot>.
}""")

    return [(binding["sub"]["value"], json.loads(binding["embedding"]["value"]))
            for binding in bindings]

from embedding_service.embed import calculate_embedding
from embedding_service.sparql import get_all_products
from embedding_service.sparql import save_embeddings
import json
from threading import Thread
from requests import post
from escape_helpers import sparql_escape_string, sparql_escape_uri
from helpers import query, update
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask import request

def getEmbeddings():
    queryResults = query("""PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
SELECT ?sub ?embedding
WHERE {
    ?sub ext:hasEmbedding ?embedding.
    ?sub a <https://productencatalogus.data.vlaanderen.be/ns/ipdc-lpdc#InstancePublicServiceSnapshot>.
} LIMIT 500""")

    return [(binding["sub"]["value"], json.loads(binding["embedding"]["value"]))
            for binding in queryResults["results"]["bindings"]]

#@app.route("/query-weights")
def queryWeights(queryEmbeddings):    
    dataEmbeddings = getEmbeddings()
    similarities = [cosine_similarity([queryEmbeddings], [embedding[1]])[0][0] for embedding in dataEmbeddings]
    most_similar_index = np.argmax(similarities)
    return dataEmbeddings[most_similar_index]

@app.route("/query-sentence",methods=["GET"])
def querySentence():
    query = request.args.get('source')
    queryEmbeddings = calculate_embedding(query)
    product = queryWeights(queryEmbeddings)

    return product[0]

###################
### FUTURE WORK ###
###################

# FUTURE: ingest embeddings at boot

# embeddings = [
#   # ("http://something/23423", [34,.433,4.43,.34,.34,34.,34534,.3,]), ...
# ]
#

@app.route("/ingest", methods=["POST"])
def ingest():
    # TODO inject in DB
    print("Starting ingest process")
    products = get_all_products()

    for id, prod_descript in products.items():
        emb = calculate_embedding(prod_descript)
        save_embeddings(id, json.dumps(emb.tolist()))

    print("Wrapping up ingestion process")


def ingestWithDelay():
    time.sleep(1)
    post("http://localhost/ingest")

Thread(target = lambda: ingestWithDelay()).start()

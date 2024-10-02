from embedding_service.embed import calculate_embedding
from embedding_service.sparql import query_products_without_embedding, save_embeddings, query_embeddings
import json
from threading import Thread
from requests import post
from helpers import query
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask import request
import logging

LOG = logging.getLogger(__name__)

cachedEmbeddings = None

def queryWeights(queryEmbeddings, solutions=20):
    global cachedEmbeddings
    if cachedEmbeddings == None:
        cachedEmbeddings = query_embeddings()
    dataEmbeddings = cachedEmbeddings

    similarities = np.array([cosine_similarity([queryEmbeddings], [embedding[1]])[0][0] for embedding in dataEmbeddings])
    # We could get the max index like this:
    # most_similar_index = np.argmax(similarities)
    # But we get a few more by getting the N most similar (unsorted)
    n_most_similar_indexes = np.argpartition(similarities,-solutions)[-solutions:]
    # And then sorting those indexes based on the similarity
    sorted_n_best_indexes = n_most_similar_indexes[np.argsort(-similarities[n_most_similar_indexes])] # sort indexes by similarity
    # To finally return the dataEmbedding containing (product,embedding) for best -> worst index
    return [dataEmbeddings[i] for i in sorted_n_best_indexes]

@app.route("/query-sentence",methods=["GET"])
def querySentence():
    query = request.args.get('source')
    queryEmbeddings = calculate_embedding(query)
    products_and_embeddings = queryWeights(queryEmbeddings)

    return [product[0] for product in products_and_embeddings]

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
    LOG.info('start ingest process')
    products = query_products_without_embedding()

    for id, prod_descript in products.items():
        LOG.info(f'processing {id}')
        emb = calculate_embedding(prod_descript)
        save_embeddings(id, json.dumps(emb.tolist()))

    LOG.info('Wrapping up ingestion process')

    return "OK"

@app.route("/delta", methods=["POST"])
def delta():
    global cachedEmbeddings
    # TODO: delete weights for products which have changed
    ingest()
    # clear cached embeddings
    cachedEmbeddings = None

def ingestWithDelay():
    time.sleep(30)
    # This is somewhat inline with receiving a call from the
    # delta-notifier, though a good implementation would clear the
    # embeddings of the relevant snapshots.
    post("http://localhost/ingest")

Thread(target = lambda: ingestWithDelay()).start()

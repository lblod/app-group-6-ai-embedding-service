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

def queryWeights(queryEmbeddings, solutions=20):
    dataEmbeddings = query_embeddings()
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
    print("Starting ingest process")
    products = query_products_without_embedding()

    for id, prod_descript in products.items():
        print("Processing {}".format(id), flush=True)
        emb = calculate_embedding(prod_descript)
        save_embeddings(id, json.dumps(emb.tolist()))

    print("Wrapping up ingestion process", flush=True)

    return "OK"


def ingestWithDelay():
    time.sleep(1)
    # This is somewhat inline with receiving a call from the
    # delta-notifier, though a good implementation would clear the
    # embeddings of the relevant snapshots.
    post("http://localhost/ingest")

Thread(target = lambda: ingestWithDelay()).start()

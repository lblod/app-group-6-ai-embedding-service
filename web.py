from embedding_service.embed import get_embedding
from embedding_service.sparql import get_all_products

products = get_all_products()

for id, prod_descript in products.items():
    emb = get_embedding(prod_descript)

    # TODO inject in DB



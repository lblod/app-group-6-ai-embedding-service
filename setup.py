from transformers import AutoTokenizer, AutoModel
from pathlib import Path
import logging

LOG = logging.getLogger(__name__)

MODEL_NAME = "pdelobelle/robbert-v2-dutch-base"

DATA_PATH = Path("/data")

if DATA_PATH.exists():
    # TODO: link data path with persistent volume to store models permanently instead of loading at runtime
    LOG.info(f"skipping model download as it already exists at '{DATA_PATH}'")
else:
    LOG.info(f"no model found at '{DATA_PATH}', downloading...")

    # Load the pre-trained RobBERT model and tokenizer (only the base transformer, no classification head)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)  # Load without the classification head

    # save to /data
    tokenizer.save_pretrained("/data/tokenizer")
    model.save_pretrained("/data/model")

    LOG.info(f"saved model to '{DATA_PATH}'")

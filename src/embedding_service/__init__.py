from transformers import AutoTokenizer, AutoModel
from pathlib import Path

MODEL_NAME = "pdelobelle/robbert-v2-dutch-base"
DATA_PATH = Path("/data")

if DATA_PATH.exists():
    # TODO: link data path with persistent volume to store models permanently instead of loading at runtime
    print("model is already loaded")
else:
    # Load the pre-trained RobBERT model and tokenizer (only the base transformer, no classification head)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)  # Load without the classification head

    # save to /data
    tokenizer.save_pretrained("/data/tokenizer")
    model.save_pretrained("/data/model")

    print("Saved models in the image to /data/")

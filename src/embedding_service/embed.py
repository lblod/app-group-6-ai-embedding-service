from transformers import RobertaModel, RobertaTokenizer
import torch

TOKENIZER = RobertaTokenizer.from_pretrained("/data/tokenizer")
MODEL = RobertaModel.from_pretrained("/data/model", torch_dtype="auto")

def get_embedding(text: str) -> list:
    inputs = TOKENIZER(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():  # We don't need gradients for embeddings
        outputs = MODEL(**inputs)

    # Extract the hidden state of the [CLS] token for sentence embedding
    cls_embedding = outputs.last_hidden_state[:, 0, :]  # [batch_size, seq_len, hidden_dim], we take the [CLS] token

    return cls_embedding.squeeze().numpy()
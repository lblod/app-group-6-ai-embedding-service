import src.embedding_service

from transformers import RobertaModel, RobertaTokenizer
import torch

TOKENIZER = RobertaTokenizer.from_pretrained("/data/tokenizer")
MODEL = RobertaModel.from_pretrained("/data/model", torch_dtype="auto")

# TODO: query triplestore to give back
# Sentence to be embedded
sentence = "Dit is een voorbeeldzin."

# Tokenize and encode the sentence
inputs = TOKENIZER(sentence, return_tensors="pt", truncation=True, padding=True)

# Get the outputs (hidden states) from the model
with torch.no_grad():  # We don't need gradients for embeddings
    outputs = MODEL(**inputs)

# Extract the hidden state of the [CLS] token for sentence embedding
cls_embedding = outputs.last_hidden_state[:, 0, :]  # [batch_size, seq_len, hidden_dim], we take the [CLS] token

# Convert to a numpy array (optional)
sentence_embedding = cls_embedding.squeeze().numpy()

# Print the embedding
print(sentence_embedding)

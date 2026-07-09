import os
import numpy as np


def save_embedding(user_id, embedding):
    np.save(f"embeddings/{user_id}.npy", embedding)


def load_embedding(user_id):
    return np.load(f"embeddings/{user_id}.npy")


def load_all_embeddings():

    embeddings = {}

    for file in os.listdir("embeddings"):

        if file.endswith(".npy"):

            user_id = int(file.replace(".npy", ""))

            embeddings[user_id] = np.load(
                os.path.join("embeddings", file)
            )

    return embeddings
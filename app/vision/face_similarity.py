import numpy as np


def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Tính Cosine Similarity giữa hai embedding.

    Giá trị trả về:
        1.0   -> Cùng khuôn mặt gần như tuyệt đối
        0.8+  -> Rất giống
        0.5   -> Có thể cùng người
        <0.5 -> Khác người
    """

    embedding1 = embedding1 / np.linalg.norm(embedding1)
    embedding2 = embedding2 / np.linalg.norm(embedding2)

    similarity = np.dot(embedding1, embedding2)

    return float(similarity)
from app.vision.storage import load_all_embeddings
from app.vision.face_similarity import cosine_similarity


THRESHOLD = 0.5


def recognize(current_embedding):
    embeddings = load_all_embeddings()

    best_user_id = None
    best_score = -1

    for user_id, saved_embedding in embeddings.items():

        score = cosine_similarity(
            current_embedding,
            saved_embedding
        )

        if score > best_score:
            best_score = score
            best_user_id = user_id

    if best_score < THRESHOLD:
        return None, best_score

    return best_user_id, best_score
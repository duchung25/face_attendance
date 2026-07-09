from insightface.app import FaceAnalysis

face_app = FaceAnalysis()
face_app.prepare(ctx_id=0)


def detect_faces(frame):
    return face_app.get(frame)
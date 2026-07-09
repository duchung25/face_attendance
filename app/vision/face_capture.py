import cv2

from app.vision.camera import open_camera, read_frame, release_camera
from app.vision.face_detector import detect_faces
from app.vision.embedding import extract_embedding


def capture_embedding():

    camera = open_camera()

    while True:

        frame = read_frame(camera)

        if frame is None:
            break

        faces = detect_faces(frame)

        if len(faces) == 1:

            embedding = extract_embedding(faces[0])

            release_camera(camera)

            return embedding

        cv2.imshow("Capture Face", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    release_camera(camera)

    return None
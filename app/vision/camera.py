import cv2


def open_camera():
    return cv2.VideoCapture(0)


def read_frame(camera):
    success, frame = camera.read()

    if not success:
        return None

    return frame


def release_camera(camera):
    camera.release()
    cv2.destroyAllWindows()

import sys
import os

# Đảm bảo import đúng package gốc khi chạy từ thư mục dự án
sys.path.insert(0, os.path.dirname(__file__))

import cv2
import numpy as np

from app.vision.face_detector import detect_faces, face_app
from app.vision.face_recognizer import recognize
from app.vision.storage import load_all_embeddings
from app.database.database import SessionLocal
from app.repositories.user_repository import UserRepository

# ──────────────────────────────────────────────
# Cấu hình giao diện
# ──────────────────────────────────────────────
COLOR_KNOWN   = (0, 220, 100)    # Xanh lá  → đã nhận diện
COLOR_UNKNOWN = (0, 80, 255)     # Đỏ       → chưa nhận diện
COLOR_BG      = (20, 20, 20)     # Nền text
FONT          = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE    = 0.75
THICKNESS     = 2


def load_user_map():
    """Lấy dict {user_id: name} từ database."""
    db = SessionLocal()
    try:
        repo = UserRepository()
        users = repo.get_all(db)
        return {u.id: u.name for u in users}
    finally:
        db.close()


def draw_face_box(frame, face, label: str, score: float | None, color):
    """Vẽ bounding box + label lên frame."""
    bbox = face.bbox.astype(int)
    x1, y1, x2, y2 = bbox

    # Bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, THICKNESS)

    # Label text
    if score is not None:
        text = f"{label}  ({score:.2f})"
    else:
        text = label

    (tw, th), _ = cv2.getTextSize(text, FONT, FONT_SCALE, THICKNESS)
    text_y = y1 - 10 if y1 - 10 > th else y1 + th + 10

    # Nền mờ cho text
    cv2.rectangle(
        frame,
        (x1, text_y - th - 4),
        (x1 + tw + 6, text_y + 4),
        color,
        -1,
    )
    cv2.putText(
        frame, text,
        (x1 + 3, text_y),
        FONT, FONT_SCALE,
        (255, 255, 255),
        THICKNESS,
        cv2.LINE_AA,
    )


def draw_status_bar(frame, num_faces: int, num_users: int):
    """Vẽ thanh thông tin ở dưới cùng."""
    h, w = frame.shape[:2]
    bar_h = 36
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - bar_h), (w, h), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    info = (
        f"  Faces detected: {num_faces}   |   "
        f"Registered users: {num_users}   |   "
        f"Press Q to quit"
    )
    cv2.putText(
        frame, info,
        (8, h - 10),
        FONT, 0.55,
        (200, 200, 200),
        1,
        cv2.LINE_AA,
    )


def main():
    print("=" * 55)
    print("  FACE ATTENDANCE — Live Recognition Test")
    print("=" * 55)

    # Load user map
    print("[*] Loading user database...")
    user_map = load_user_map()
    if not user_map:
        print("[!] Chưa có user nào đăng ký trong database.")
        print("    Hãy đăng ký user qua API /users/register trước.")
    else:
        print(f"[+] Tìm thấy {len(user_map)} user(s):")
        for uid, name in user_map.items():
            print(f"    • ID {uid}: {name}")
    print("-" * 55)
    print("[*] Mở camera... (nhấn Q để thoát)")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[!] Không thể mở camera.")
        return

    cv2.namedWindow("Face Attendance — Live Test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Face Attendance — Live Test", 960, 600)

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[!] Không đọc được frame từ camera.")
            break

        frame_count += 1

        # Nhận diện mỗi frame (insightface nhanh, không cần skip)
        faces = detect_faces(frame)

        for face in faces:
            embedding = face.embedding

            user_id, score = recognize(embedding)

            if user_id is not None:
                name  = user_map.get(user_id, f"ID {user_id}")
                label = f"✓ {name}"
                color = COLOR_KNOWN
            else:
                label = "? Unknown"
                color = COLOR_UNKNOWN
                score = None  # Không hiển thị score nếu unknown

            draw_face_box(frame, face, label, score if user_id else None, color)

        draw_status_bar(frame, len(faces), len(user_map))

        cv2.imshow("Face Attendance — Live Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:   # Q hoặc ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[*] Đã thoát.")


if __name__ == "__main__":
    main()

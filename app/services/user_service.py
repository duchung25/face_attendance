from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository

from app.vision.face_capture import capture_embedding
from app.vision.face_recognizer import recognize
from app.vision.storage import save_embedding


class UserService:

    def __init__(self):
        self.user_repository = UserRepository()

    def create_user(self, db: Session, name: str):

        # Mở camera và lấy embedding
        embedding = capture_embedding()

        if embedding is None:
            raise Exception("Cannot detect exactly one face.")

        # Kiểm tra khuôn mặt đã đăng ký chưa
        user_id, score = recognize(embedding)

        if user_id is not None:
            raise Exception(
                f"Face already registered (User ID: {user_id})"
            )

        # Tạo User
        user = User(
            name=name,
            embedding_path=""
        )

        user = self.user_repository.create(db, user)

        # Lưu embedding
        save_embedding(user.id, embedding)

        # Cập nhật đường dẫn
        user.embedding_path = f"embeddings/{user.id}.npy"

        user = self.user_repository.update(db, user)

        return user

    def create_user_from_image(self, db: Session, name: str, frame):
        from app.vision.face_detector import detect_faces
        from app.vision.embedding import extract_embedding

        faces = detect_faces(frame)
        if len(faces) != 1:
            raise Exception("Không thể phát hiện chính xác một khuôn mặt trong ảnh.")

        embedding = extract_embedding(faces[0])

        # Kiểm tra khuôn mặt đã đăng ký chưa
        user_id, score = recognize(embedding)

        if user_id is not None:
            raise Exception(
                f"Khuôn mặt này đã được đăng ký trước đó (Nhân viên ID: {user_id})"
            )

        # Tạo User
        user = User(
            name=name,
            embedding_path=""
        )

        user = self.user_repository.create(db, user)

        # Lưu embedding
        save_embedding(user.id, embedding)

        # Cập nhật đường dẫn
        user.embedding_path = f"embeddings/{user.id}.npy"

        user = self.user_repository.update(db, user)

        return user

    def get_users(self, db: Session):
        return self.user_repository.get_all(db)
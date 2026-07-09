from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.user_repository import UserRepository
from app.vision.face_capture import capture_embedding
from app.vision.face_recognizer import recognize


class AttendanceService:

    def __init__(self):
        self.attendance_repository = AttendanceRepository()
        self.user_repository = UserRepository()

    def check_in(self, db: Session):
        # 1. Chụp ảnh từ camera để lấy embedding khuôn mặt
        embedding = capture_embedding()

        if embedding is None:
            raise HTTPException(
                status_code=400,
                detail="Không thể phát hiện chính xác một khuôn mặt. Vui lòng thử lại."
            )

        # 2. Nhận diện khuôn mặt xem khớp với User nào
        user_id, score = recognize(embedding)

        if user_id is None:
            raise HTTPException(
                status_code=400,
                detail="Khuôn mặt chưa được đăng ký hoặc không thể nhận diện."
            )

        # 3. Kiểm tra xem user này đã check-in hôm nay chưa
        existing_attendance = self.attendance_repository.get_today_attendance_by_user(db, user_id)

        if existing_attendance is not None:
            # Lấy thông tin user để hiển thị lỗi chi tiết hơn
            user = self.user_repository.get_by_id(db, user_id)
            user_name = user.name if user else f"ID {user_id}"
            raise HTTPException(
                status_code=400,
                detail=f"Nhân viên {user_name} (ID: {user_id}) đã thực hiện check-in hôm nay rồi."
            )

        # 4. Ghi nhận check-in mới
        attendance = self.attendance_repository.create(db, user_id)
        return attendance

    def check_in_from_image(self, db: Session, frame):
        from app.vision.face_detector import detect_faces
        from app.vision.embedding import extract_embedding

        faces = detect_faces(frame)
        if len(faces) != 1:
            raise HTTPException(
                status_code=400,
                detail="Không thể phát hiện chính xác một khuôn mặt trong ảnh. Vui lòng thử lại."
            )

        embedding = extract_embedding(faces[0])

        # Nhận diện khuôn mặt
        user_id, score = recognize(embedding)

        if user_id is None:
            raise HTTPException(
                status_code=400,
                detail="Khuôn mặt chưa được đăng ký hoặc không thể nhận diện."
            )

        # Kiểm tra xem user này đã check-in hôm nay chưa
        existing_attendance = self.attendance_repository.get_today_attendance_by_user(db, user_id)

        if existing_attendance is not None:
            user = self.user_repository.get_by_id(db, user_id)
            user_name = user.name if user else f"ID {user_id}"
            raise HTTPException(
                status_code=400,
                detail=f"Nhân viên {user_name} (ID: {user_id}) đã thực hiện check-in hôm nay rồi."
            )

        # Ghi nhận check-in mới
        attendance = self.attendance_repository.create(db, user_id)
        return attendance

    def detect_faces_from_image(self, db: Session, frame):
        from app.vision.face_detector import detect_faces
        from app.vision.embedding import extract_embedding

        faces = detect_faces(frame)
        results = []

        for face in faces:
            embedding = extract_embedding(face)
            user_id, score = recognize(embedding)
            name = None

            if user_id is not None:
                user = self.user_repository.get_by_id(db, user_id)
                name = user.name if user else f"ID {user_id}"

            bbox = face.bbox.tolist()  # [x1, y1, x2, y2]
            results.append({
                "bbox": bbox,
                "user_id": user_id,
                "name": name,
                "score": score
            })
        return results

    def get_all_attendances(self, db: Session):
        return self.attendance_repository.get_all(db)



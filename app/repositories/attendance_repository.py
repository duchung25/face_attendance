from datetime import datetime, time
from sqlalchemy.orm import Session, joinedload

from app.models.attendance import Attendance


class AttendanceRepository:

    def create(self, db: Session, user_id: int, check_in_time: datetime = None):
        if check_in_time is None:
            check_in_time = datetime.now()

        attendance = Attendance(
            user_id=user_id,
            check_in=check_in_time
        )

        db.add(attendance)
        db.commit()
        db.refresh(attendance)

        # Reload with user relation eagerly
        return db.query(Attendance).options(joinedload(Attendance.user)).filter(Attendance.id == attendance.id).first()

    def get_today_attendance_by_user(self, db: Session, user_id: int):
        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        return db.query(Attendance).filter(
            Attendance.user_id == user_id,
            Attendance.check_in >= today_start,
            Attendance.check_in <= today_end
        ).first()

    def get_all(self, db: Session):

        return db.query(Attendance).options(joinedload(Attendance.user)).all()
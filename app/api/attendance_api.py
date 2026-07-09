from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import cv2
import numpy as np

from app.database.database import get_db
from app.schemas.attendance_schema import AttendanceResponse
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])

attendance_service = AttendanceService()


@router.post("/check-in", response_model=AttendanceResponse)
async def check_in(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Không thể giải mã file ảnh gửi lên.")

        return attendance_service.check_in_from_image(db, frame)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/detect")
async def detect_faces_endpoint(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Không thể giải mã file ảnh gửi lên.")

        faces_data = attendance_service.detect_faces_from_image(db, frame)
        return {"faces": faces_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[AttendanceResponse])
def get_attendances(
    db: Session = Depends(get_db)
):
    return attendance_service.get_all_attendances(db)


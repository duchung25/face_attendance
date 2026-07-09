from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import cv2
import numpy as np

from app.database.database import get_db
from app.schemas.user_schema import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

user_service = UserService()


@router.post("/register", response_model=UserResponse)
async def create_user(
    name: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Đọc nội dung file ảnh được upload từ camera của frontend
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Không thể giải mã file ảnh gửi lên.")

        return user_service.create_user_from_image(db, name, frame)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db)
):
    return user_service.get_users(db)
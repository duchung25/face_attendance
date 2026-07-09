from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.models.user import User
from app.models.attendance import Attendance
from app.database.database import Base, engine
from app.api.user_api import router as user_router
from app.api.attendance_api import router as attendance_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Face Attendance")

app.include_router(user_router)
app.include_router(attendance_router)

# Serve static frontend files at /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def home():
    return RedirectResponse(url="/static/index.html")
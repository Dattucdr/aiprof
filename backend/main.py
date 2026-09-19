from fastapi import FastAPI
from api.test_security import router as security_test_router
from core.config import settings
from api.auth import router as auth_router
from api.hospitals import router as hospitals_router
from api.patients import router as patients_router
from api.campaigns import router as campaigns_router
from api.queue import router as queue_router
from api.calls import router as calls_router
from api.ai_tools import router as ai_tools_router
from backend.api.ai_tools import router as ai_tools_router
from api.escalations import router as escalations_router
from api.ehr import router as ehr_router
from api.analytics import router as analytics_router
from api.safety import router as safety_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(security_test_router)
app.include_router(hospitals_router)
app.include_router(patients_router)
app.include_router(campaigns_router)
app.include_router(queue_router)
app.include_router(calls_router)
app.include_router(ai_tools_router)
app.include_router(escalations_router)
app.include_router(ehr_router)
app.include_router(analytics_router)
app.include_router(safety_router)



@app.get("/")
def root():
    return {
        "message": "AIProf Healthcare Platform API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
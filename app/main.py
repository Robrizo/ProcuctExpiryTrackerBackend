import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.auth.jwt import user_dependancy
from app.config.database import Base, SessionLocal, db_dependency, engine
from app.routers import auth, products, user
from app.services.email import sent_emails_log
from app.tasks.expiry_checker import check_and_send_expiry_reminders

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("expiry_tracker")

Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()


def scheduled_job():
    logger.info("Running scheduled product expiry check...")

    db: Session = SessionLocal()

    try:
        result = check_and_send_expiry_reminders(db)
        logger.info("Expiry check completed: %s", result)

    except Exception:
        logger.exception("Error during scheduled expiry check")

    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting expiry reminder scheduler...")

    scheduler.add_job(
        scheduled_job,
        trigger="interval",
        hours=12,
        id="expiry_check_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()

    try:
        scheduled_job()
        yield
    finally:
        logger.info("Shutting down scheduler...")

        if scheduler.running:
            scheduler.shutdown(wait=False)


app = FastAPI(
    title="Product Expiry Tracker API",
    description="REST API for household product tracking and 7-day expiry notifications",
    version="1.0.0",
    lifespan=lifespan,
)


cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(user.router)


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": "OK",
        "service": "Product Expiry Tracker API",
    }


@app.post("/api/tasks/check-expiry", tags=["Tasks"])
def manual_expiry_check(db: db_dependency):
    # Manually trigger the expiry reminder checker
    try:
        result = check_and_send_expiry_reminders(db)

        return {
            "status": "success",
            "message": (
                f"Expiry check executed. "
                f"Sent {result['reminders_sent']} reminder(s)."
            ),
            "details": result,
        }

    except Exception:
        logger.exception("Manual expiry check failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to execute expiry check.",
        )


@app.get("/api/notifications/logs", tags=["Tasks"])
def get_notification_logs(current_user: user_dependancy, db: db_dependency):
    # Return email reminders for the logged-in user.
    from app.models.user import User

    user_data = db.query(User).filter(User.id == current_user.get("user_id")).first()
    if not user_data:
        return {"notifications": []}

    user_logs = [
        log
        for log in sent_emails_log
        if log.get("recipient") == user_data.email
    ]

    return {"notifications": user_logs}

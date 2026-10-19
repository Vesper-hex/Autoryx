import threading
import time
import asyncio
from typing import Optional
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.logging import logger
from app.models.job import Job
from app.workers.tasks import execute_job_pipeline

class PersistentJobQueue:
    """
    Persistent, fault-tolerant background queue that processes jobs asynchronously.
    Jobs are stored in PostgreSQL/SQLite and picked up by background workers.
    Even if the browser is closed or laptop put to sleep, jobs persist in the database
    and resume when the service runs.
    """

    _worker_thread: Optional[threading.Thread] = None
    _is_running: bool = False

    @classmethod
    def enqueue(cls, job_id: str):
        """Marks job as queued in database and triggers worker processing."""
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "queued"
                job.current_step = "Queued for background processing"
                db.commit()
                logger.info(f"Enqueued job {job_id} for processing.")
        finally:
            db.close()

        # Start worker if not already running
        cls.ensure_worker_running()

    @classmethod
    def ensure_worker_running(cls):
        """Ensures the background processing loop is active."""
        if cls._worker_thread is None or not cls._worker_thread.is_alive():
            cls._is_running = True
            cls._worker_thread = threading.Thread(target=cls._worker_loop, daemon=True, name="AutoryxJobWorker")
            cls._worker_thread.start()
            logger.info("Background persistent worker thread started.")

    @classmethod
    def recover_stale_jobs(cls):
        """Recovers any jobs left in interrupted state after server reboot."""
        db = SessionLocal()
        try:
            stale_jobs = db.query(Job).filter(
                Job.status.in_(["generating", "compiling", "testing", "repairing"])
            ).all()
            for job in stale_jobs:
                logger.warning(f"Recovering interrupted job {job.id}; re-queuing...")
                job.status = "queued"
                job.current_step = "Re-queued following server restart"
            db.commit()
        except Exception as e:
            logger.error(f"Error during job recovery: {e}")
        finally:
            db.close()

    @classmethod
    def _worker_loop(cls):
        """Continuous background worker loop checking database for queued jobs."""
        logger.info("Autoryx Persistent Background Worker is active and listening for jobs.")
        cls.recover_stale_jobs()

        while cls._is_running:
            try:
                db = SessionLocal()
                # Find oldest queued job
                job = db.query(Job).filter(Job.status == "queued").order_by(Job.created_at.asc()).first()
                if job:
                    job_id = job.id
                    db.close()
                    # Execute async pipeline synchronously inside worker thread
                    logger.info(f"Worker picked up job {job_id}...")
                    asyncio.run(execute_job_pipeline(job_id))
                else:
                    db.close()
                    time.sleep(1.0)
            except Exception as e:
                logger.error(f"Error in background worker loop: {e}")
                time.sleep(2.0)

    @classmethod
    def stop(cls):
        cls._is_running = False
        if cls._worker_thread and cls._worker_thread.is_alive():
            cls._worker_thread.join(timeout=3)

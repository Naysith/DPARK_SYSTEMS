from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.utils.sesi_auto import generate_auto_sesi

scheduler = BackgroundScheduler()

def start_scheduler(app):
    """
    Start a background job that generates new sessions daily.
    """
    def job():
        with app.app_context():
            print(f"[{datetime.now()}] Running auto sesi generation...")
            generate_auto_sesi()
            print(f"[{datetime.now()}] ✅ Done generating sessions.")

    # Run once per day at 00:10 AM
    scheduler.add_job(job, 'cron', hour=0, minute=10, id='auto_sesi_job', replace_existing=True)
    scheduler.start()
    print("🕒 Daily session generation scheduler started (00:10 AM).")

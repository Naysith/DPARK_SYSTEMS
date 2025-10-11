from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.utils.sesi_auto import generate_auto_sesi

scheduler = BackgroundScheduler()
last_run_info = {
    "last_run_time": None,
    "last_result": None
}

def start_scheduler(app):
    """
    Start a background job that generates new sessions daily.
    """
    def job():
        with app.app_context():
            print(f"[{datetime.now()}] Running auto sesi generation...")
            try:
                generate_auto_sesi()
                last_run_info["last_run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                last_run_info["last_result"] = "✅ Success"
            except Exception as e:
                last_run_info["last_run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                last_run_info["last_result"] = f"❌ Error: {str(e)}"
                print(f"⚠️ Error in scheduler job: {e}")

    # Run every day at 00:10 AM
    scheduler.add_job(job, 'cron', hour=0, minute=10, id='auto_sesi_job', replace_existing=True)
    scheduler.start()
    print("🕒 Daily session generation scheduler started (00:10 AM).")

def get_scheduler_status():
    """
    Returns a dictionary with scheduler health info.
    """
    running = scheduler.running if scheduler else False
    return {
        "running": running,
        "next_run": str(scheduler.get_jobs()[0].next_run_time) if scheduler.get_jobs() else None,
        "last_run_time": last_run_info["last_run_time"],
        "last_result": last_run_info["last_result"]
    }

import schedule
from mcl_v2.utils import write_heartbeat
from mcl_v2.tasks import task_auto_git_sync

def setup_schedules() -> None:
    schedule.clear()
    schedule.every(30).seconds.do(write_heartbeat)
    schedule.every(15).minutes.do(task_auto_git_sync)

from celery import Celery
from datetime import datetime, timedelta
import logging
from redis import Redis
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery = Celery(broker=Config.CELERY_BROKER_URL)
redis = Redis.from_url(Config.CELERY_BROKER_URL)

def monitor_tasks():
    """Monitor active and failed tasks"""
    try:
        # Get active tasks
        active = celery.control.inspect().active()
        if active:
            for worker, tasks in active.items():
                logger.info(f"Worker {worker} has {len(tasks)} active tasks")
                for task in tasks:
                    logger.info(f"Active task: {task['id']} - {task['name']}")
        
        # Get failed tasks from Redis
        failed_tasks = []
        for key in redis.scan_iter("celery-task-meta-*"):
            task_data = redis.get(key)
            if task_data and b'FAILURE' in task_data:
                failed_tasks.append(key.decode())
        
        if failed_tasks:
            logger.warning(f"Found {len(failed_tasks)} failed tasks")
            for task_key in failed_tasks[:5]:  # Log first 5 failures
                task_data = redis.get(task_key)
                logger.warning(f"Failed task {task_key}: {task_data}")
        
        return {
            "active_tasks": sum(len(t) for t in active.values()) if active else 0,
            "failed_tasks": len(failed_tasks)
        }
    except Exception as e:
        logger.error(f"Error monitoring tasks: {str(e)}")
        raise

def cleanup_old_task_results(days=7):
    """Cleanup task results older than specified days"""
    try:
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        
        for key in redis.scan_iter("celery-task-meta-*"):
            task_data = redis.get(key)
            if task_data:
                try:
                    # Simple check for timestamp in task data
                    if str(cutoff.timestamp()).encode() in task_data:
                        redis.delete(key)
                        count += 1
                except:
                    continue
        
        logger.info(f"Cleaned up {count} old task results")
        return count
    except Exception as e:
        logger.error(f"Error cleaning up task results: {str(e)}")
        raise
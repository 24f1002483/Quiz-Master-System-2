from celery import Celery
from datetime import datetime, timedelta
import logging
from redis import Redis
from config import Config
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery = Celery(broker=Config.broker_url)
redis = Redis.from_url(Config.broker_url)

def monitor_tasks():
    """Monitor active and failed tasks with enhanced metrics"""
    try:
        # Get active tasks
        active = celery.control.inspect().active()
        if active:
            for worker, tasks in active.items():
                logger.info(f"Worker {worker} has {len(tasks)} active tasks")
                for task in tasks:
                    logger.info(f"Active task: {task['id']} - {task['name']} - Started: {task.get('time_start', 'N/A')}")
        
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
        
        # Get queue statistics
        queue_stats = get_queue_statistics()
        
        return {
            "active_tasks": sum(len(t) for t in active.values()) if active else 0,
            "failed_tasks": len(failed_tasks),
            "queue_stats": queue_stats
        }
    except Exception as e:
        logger.error(f"Error monitoring tasks: {str(e)}")
        raise

def get_queue_statistics():
    """Get detailed queue statistics"""
    try:
        stats = {}
        queues = ['default', 'reminders', 'reports', 'notifications', 'maintenance']
        
        for queue in queues:
            queue_length = redis.llen(f'celery:{queue}')
            stats[queue] = {
                'length': queue_length,
                'status': 'active' if queue_length > 0 else 'idle'
            }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting queue statistics: {str(e)}")
        return {}

def cleanup_old_task_results(days=7):
    """Cleanup task results older than specified days with enhanced logic"""
    try:
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        total_size_before = 0
        total_size_after = 0
        
        # Get Redis memory info before cleanup
        memory_info = redis.info('memory')
        total_size_before = memory_info.get('used_memory_human', '0B')
        
        for key in redis.scan_iter("celery-task-meta-*"):
            task_data = redis.get(key)
            if task_data:
                try:
                    # Parse task data to check timestamp
                    task_info = json.loads(task_data.decode())
                    if 'date_done' in task_info:
                        task_date = datetime.fromisoformat(task_info['date_done'].replace('Z', '+00:00'))
                        if task_date < cutoff:
                            redis.delete(key)
                            count += 1
                except (json.JSONDecodeError, ValueError, KeyError):
                    # If we can't parse the data, delete old keys based on pattern
                    continue
        
        # Get Redis memory info after cleanup
        memory_info = redis.info('memory')
        total_size_after = memory_info.get('used_memory_human', '0B')
        
        logger.info(f"Cleaned up {count} old task results")
        logger.info(f"Memory before: {total_size_before}, after: {total_size_after}")
        return count
    except Exception as e:
        logger.error(f"Error cleaning up task results: {str(e)}")
        raise

def optimize_redis_connection():
    """Optimize Redis connection settings"""
    try:
        # Set Redis configuration for better performance
        redis.config_set('maxmemory-policy', 'allkeys-lru')
        redis.config_set('save', '900 1 300 10 60 10000')
        redis.config_set('tcp-keepalive', '300')
        
        # Enable Redis slow log for monitoring
        redis.config_set('slowlog-log-slower-than', '10000')  # 10ms
        redis.config_set('slowlog-max-len', '128')
        
        logger.info("Redis optimization completed")
        return True
    except Exception as e:
        logger.error(f"Error optimizing Redis: {str(e)}")
        return False

def get_redis_performance_metrics():
    """Get Redis performance metrics"""
    try:
        info = redis.info()
        metrics = {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory_human': info.get('used_memory_human', '0B'),
            'used_memory_peak_human': info.get('used_memory_peak_human', '0B'),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'total_connections_received': info.get('total_connections_received', 0),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'uptime_in_seconds': info.get('uptime_in_seconds', 0),
            'uptime_in_days': info.get('uptime_in_days', 0)
        }
        
        # Calculate hit ratio
        total_requests = metrics['keyspace_hits'] + metrics['keyspace_misses']
        if total_requests > 0:
            metrics['hit_ratio'] = round((metrics['keyspace_hits'] / total_requests) * 100, 2)
        else:
            metrics['hit_ratio'] = 0
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting Redis metrics: {str(e)}")
        return {}

def monitor_celery_workers():
    """Monitor Celery worker status and performance"""
    try:
        inspect = celery.control.inspect()
        
        # Get worker stats
        stats = inspect.stats()
        active = inspect.active()
        registered = inspect.registered()
        
        worker_info = {}
        
        if stats:
            for worker_name, worker_stats in stats.items():
                worker_info[worker_name] = {
                    'status': 'online',
                    'pool_size': worker_stats.get('pool', {}).get('max-concurrency', 0),
                    'active_tasks': len(active.get(worker_name, [])),
                    'registered_tasks': len(registered.get(worker_name, [])),
                    'load': worker_stats.get('load', [0, 0, 0]),
                    'processed': worker_stats.get('total', {}).get('processed', 0)
                }
        
        return worker_info
    except Exception as e:
        logger.error(f"Error monitoring Celery workers: {str(e)}")
        return {}

def get_task_performance_metrics():
    """Get task performance metrics"""
    try:
        metrics = {
            'total_tasks_processed': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'retried_tasks': 0,
            'average_task_duration': 0
        }
        
        # Count task results
        for key in redis.scan_iter("celery-task-meta-*"):
            task_data = redis.get(key)
            if task_data:
                try:
                    task_info = json.loads(task_data.decode())
                    metrics['total_tasks_processed'] += 1
                    
                    if task_info.get('status') == 'SUCCESS':
                        metrics['successful_tasks'] += 1
                    elif task_info.get('status') == 'FAILURE':
                        metrics['failed_tasks'] += 1
                    
                    # Count retries
                    if task_info.get('retries', 0) > 0:
                        metrics['retried_tasks'] += 1
                        
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting task metrics: {str(e)}")
        return {}

def generate_performance_report():
    """Generate comprehensive performance report"""
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'redis_metrics': get_redis_performance_metrics(),
            'celery_workers': monitor_celery_workers(),
            'task_metrics': get_task_performance_metrics(),
            'queue_stats': get_queue_statistics(),
            'active_tasks': monitor_tasks()
        }
        
        # Save report to Redis for historical tracking
        report_key = f"performance_report:{datetime.now().strftime('%Y%m%d_%H%M')}"
        redis.setex(report_key, 86400, json.dumps(report))  # Keep for 24 hours
        
        logger.info("Performance report generated and saved")
        return report
    except Exception as e:
        logger.error(f"Error generating performance report: {str(e)}")
        return {}

def cleanup_old_performance_reports(days=7):
    """Clean up old performance reports"""
    try:
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        
        for key in redis.scan_iter("performance_report:*"):
            try:
                # Extract timestamp from key
                timestamp_str = key.decode().split(':')[1]
                report_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M')
                
                if report_date < cutoff:
                    redis.delete(key)
                    count += 1
            except (ValueError, IndexError):
                continue
        
        logger.info(f"Cleaned up {count} old performance reports")
        return count
    except Exception as e:
        logger.error(f"Error cleaning up performance reports: {str(e)}")
        return 0
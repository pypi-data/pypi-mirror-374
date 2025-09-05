from celery import current_app

def get_active_queues():
    """
    Returns a dict of workers and the queues they are subscribed to.
    """
    try:
        inspect = current_app.control.inspect()
        return inspect.active_queues() or {}
    except Exception:
        return {}

def is_celery_running():
    try:
        return bool(current_app.control.ping(timeout=1))
    except Exception:
        return False

def is_queue_available(queue_name):
    active_queues = get_active_queues()
    for worker_queues in active_queues.values():
        for q in worker_queues:
            if q['name'] == queue_name:
                return True
    return False
from celery import current_app as current_celery_app
from celery.result import AsyncResult

from .celery_config import settings


def create_celery():
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace='CELERY')
    celery_app.conf.update(task_track_started=True)
    celery_app.conf.update(task_serializer='pickle')
    celery_app.conf.update(result_serializer='pickle')
    celery_app.conf.update(accept_content=['pickle', 'json'])
    celery_app.conf.update(result_expires=200)
    celery_app.conf.update(result_persistent=True)
    celery_app.conf.update(worker_send_task_events=False)
    celery_app.conf.update(worker_prefetch_multiplier=1)

    return celery_app


def get_task_info(task_id):
    """
    return task info for the given task_id
    """
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result

def exist_pending_task_with_title(title):
    """
    return task info for the given task_id
    """
    active_task = current_celery_app.control.inspect().active()
    print(active_task)
    filterd_task = []
    for key in active_task:
        for task in active_task[key]:
            if task['args'][0] == title:
                filterd_task.append(task)
    # print
    return len(filterd_task) > 0


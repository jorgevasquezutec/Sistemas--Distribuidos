from celery import current_app as current_celery_app
from celery.result import AsyncResult

from app.config.celery_config import settings


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


def get_queued_jobs(queue_name, celery_app):
    connection = celery_app.connection()

    try:
        channel = connection.channel()
        name, jobs, consumers = channel.queue_declare(queue=queue_name, passive=True)
        active_jobs = []

        def dump_message(message):
            # print(message.properties)
            obj = message.properties['application_headers']
            argsrepr = obj['argsrepr']  # Define the variable argsrepr
            body = {
                'task': obj['task'],
                'argsrepr': argsrepr,
                'id': obj['id'],
            }
            active_jobs.append(body)

        channel.basic_consume(queue=queue_name, callback=dump_message)

        for job in range(jobs):
            connection.drain_events()

        return active_jobs
    finally:
        connection.close()


def exist_pending_task_with_title(celeryapp,title):
    items = get_queued_jobs('celery',celeryapp)
    print(items)
    #items = [{'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '86d60274-734c-49c3-8325-c8a6d4a72fea'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '71d64ec4-339d-4d91-9242-a7c023fbc6bf'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '6d63f4c3-9085-45c5-be9a-a45d875c25f0'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '96014ce6-9aeb-4f5e-b2d4-900a2a45642e'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'c0f72068-e760-4937-8660-06cb22dcc7c9'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '772a4aa0-c636-41a7-901f-2f85d08d9a83'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '8d713fc5-4e85-431c-86dd-cd1e736753a6'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'e4117654-1a2e-4c8b-a4c9-b2c741b98a34'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '521c29a6-1914-4402-94ed-bfac3285e95b'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '3fff7d45-7d0a-43b8-b70b-0718a27e3159'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '4e6947c0-7464-4a9b-a75b-1f12dc135921'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'd50dd238-e134-4f98-8523-e928bd609ec0'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'fe7988ed-1d9a-40c3-8ba2-f89cb6688bef'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '45cc347f-7182-4547-be6d-582129156411'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '445b967a-1604-4ae0-a45a-8fa5413e7e6e'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '162ed334-3e2e-4845-9761-4e13dcc63582'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'b8889fab-06cb-487f-825d-d9ee1ddef47b'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '1339cdf5-704c-4724-bce2-db0d184449f7'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '2fe68b57-ccc1-402c-b037-337edb85783e'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '0c9cf5c1-0b9d-4e6f-bd3a-5fdb4973885d'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '85efa471-5112-45eb-b36a-1ec63bc7478f'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'ab6de8f7-79b3-4945-89ab-afe7028b75aa'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '37291909-2dd8-40ae-9565-8665f4a6be31'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'bac478e4-4ab4-4222-9d01-c315a96349e1'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'ef0533df-b2cc-4cfa-b26f-5e0261d8a946'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '4d88f689-dd89-408b-9c40-856236464428'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'da0cd954-a021-496e-a659-5946b36608a5'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'cf3e021a-c558-42e0-b74e-578cb91c4057'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'a9e05416-e099-4860-8261-ba0c95196c1a'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': '4641d2c2-e4e9-48ff-8423-f6896ebaa3cb'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'ac4afdcf-ea55-418f-9643-f31cc27d6598'}, {'task': 'celery:insert_anime_task', 'argsrepr': "['naruto']", 'id': 'de008c3f-663a-4498-894b-1031750d3291'}]
    for item in items:
        if item['argsrepr'] == f"['{title}']":
            return True
    return False




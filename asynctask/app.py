import pathlib
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from server import app as flask_app
from asynctask.loader import TaskDirsLoader, AsyncTaskLoader
from asynctask.task import ContextTask


def init_celery(_app):

    base_dir = pathlib.Path(__name__).parent
    task_dirs_loader = [TaskDirsLoader(base_dir, 'tasks')]

    task_dir = AsyncTaskLoader(
        task_dirs_loader, base_dir
    ).generate_load_path()

    config = _app.config.copy()
    _celery = Celery(
        __name__,
        task_cls=ContextTask,
        backend=config['CELERY_RESULT_BACKEND'],
        broker=config['CELERY_BROKER_URL'],
        include=task_dir,
    )
    return _celery


celery = init_celery(flask_app)
celery.conf.update(
    timezone='Asia/Shanghai',
    beat_schedule={
        'event_polling': {
            'task': 'app.tasks.event_schedule.event_polling',
            'schedule': timedelta(minutes=1)
        }
    },
    task_default_queue='default',
    task_queues=(
        Queue('default', routing_key='apps.#'),
    ),
    task_default_exchange_type='direct',
    task_default_routing_key='tasks.default',
    task_routes=([('app.*', {'queue': 'default'}), ],),
    broker_transport_options={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    },
    broker_heartbeat=0,
    worker_max_tasks_per_child=20,
)
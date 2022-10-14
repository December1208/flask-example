from abc import ABC

import celery

from server import app as flask_app
from common.extensions import db, logger
from common.logging import set_logger_config


class ContextTask(celery.Task, ABC):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            set_logger_config('celery')
            result = None
            try:
                result = super(ContextTask, self).__call__(*args, **kwargs)
                db.session.close()
            except Exception as e:
                db.session.rollback()
                db.session.close()
                logger.exception(e)

            return result

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        super(ContextTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        super(ContextTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(ContextTask, self).on_failure(exc, task_id, args, kwargs, einfo)

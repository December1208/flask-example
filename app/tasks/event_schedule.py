from app.constants.event_schedule import EventStatus, EVENT_STATUS_DISPLAY_NAME
from app.models.event_schedule import EventSchedule
from app.services.event_schedule import EventService
from asynctask.app import celery
from app.extensions import db, logger
from app.utils import helper, time as time_util


@celery.task()
def event_polling():
    now = time_util.int_timestamp()
    event_count = 500

    qs = db.session.query(EventSchedule).filter(
        EventSchedule.event_status == EventStatus.PENDING,
        EventSchedule.trigger_time <= now
    ).order_by(EventSchedule.id).limit(event_count).with_for_update()

    event_ids = []
    for event in qs:
        event: EventSchedule
        event.event_status = EventStatus.RECEIVED
        event_ids.append(event.id)

    logger.info(f"[event polling], get event: {event_ids}")

    helper.safe_commit()
    for event_id in event_ids:
        run.delay(event_id)


@celery.task(bind=True, max_retries=3, routing_key='event_schedule')
def run(self, event_id):
    event: EventSchedule = db.session.query(EventSchedule).get(event_id)
    if event.event_status not in {EventStatus.RECEIVED, EventStatus.RETRY}:
        logger.warning(f"任务状态错误, 取消执行..event_status: {EVENT_STATUS_DISPLAY_NAME[event.event_status]}")
        return

    event.event_status = EventStatus.STARTED
    helper.safe_commit()

    params = EventService.get_params_obj(event.event_type)(**event.event_params)
    try:
        EventService.run(event.event_type, event_params=params)
    except Exception as e:
        if self.request.retries >= self.max_retries:
            logger.exception(e)
            event.event_status = EventStatus.FAILURE
            event.done_time = time_util.int_timestamp()
            logger.info(f'task error. failure. event_id: {event.id}')
            helper.safe_commit()
            return

        logger.info(f'task error. retry. event_id: {event.id}')
        event.event_status = EventStatus.RETRY
        helper.safe_commit()
        self.retry(countdown=3)

    else:
        event.event_status = EventStatus.SUCCESS
        event.done_time = time_util.int_timestamp()
        logger.info(f'task success. success. event_id: {event.id}')
        helper.safe_commit()

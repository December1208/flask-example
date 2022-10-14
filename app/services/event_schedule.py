import dataclasses
from typing import Callable

from app.constants.event_schedule import EventStatus
from common.extensions import db, logger
from app.models.event_schedule import EventSchedule, EventRelation
from app.value_objects.event_schedule import BaseParams


class EventService:

    @classmethod
    def register_event(
        cls,
        event_type: int,
        params: BaseParams,
        trigger_time: int,
        content_type: int,
        object_id: int
    ):
        """
        注册事件
        :param event_type:
        :param params:
        :param trigger_time:
        :param content_type:
        :param object_id:
        :return:
        """
        logger.info(f"[REGISTER] event_type: {event_type}, params: {dataclasses.asdict(params)}, "
                    f"trigger_time: {trigger_time}, content_type: {content_type}, object_id: {object_id}")
        event = EventSchedule(
            event_type=event_type,
            event_params=dataclasses.asdict(params),
            trigger_time=trigger_time,
            event_status=EventStatus.PENDING
        )
        db.session.add(event)
        db.session.flush()

        relation = EventRelation(
            content_type=content_type,
            object_id=object_id,
            event_id=event.id,
        )
        db.session.add(relation)
        db.session.flush()

    @classmethod
    def revoke_event(cls, content_type, object_id, event_type):
        """
        撤销事件
        :param content_type:
        :param object_id:
        :param event_type:
        :return:
        """
        logger.info(f"[REVOKE] content_type: {content_type}, object_id: {object_id}, event_type: {event_type}")
        qs = db.session.query(EventSchedule).join(
            EventRelation, EventRelation.event_id == EventSchedule.id,
        ).filter(
            EventSchedule.event_type == event_type,
            EventSchedule.event_status.in_([EventStatus.PENDING, EventStatus.RECEIVED]),
            EventRelation.content_type == content_type,
            EventRelation.object_id == object_id,
        )

        for event in qs:
            event: EventSchedule
            event.event_status = EventStatus.REVOKED

    @classmethod
    def get_callback(cls, event_type: int) -> Callable:
        mapped = {

        }
        return mapped[event_type]

    @classmethod
    def get_params_obj(cls, event_type: int):
        mapped = {

        }
        return mapped[event_type]

    @classmethod
    def run(cls, event_type: int, event_params: BaseParams):

        callback = cls.get_callback(event_type)
        callback(event_params)

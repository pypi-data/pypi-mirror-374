import logging

from . import State

logger = logging.getLogger(__name__)


class Failed(State):
    can_send = False
    can_send_application_data = False

    def process(self, message):
        logger.warning("connection failed, skip incoming %s", message.__name__)

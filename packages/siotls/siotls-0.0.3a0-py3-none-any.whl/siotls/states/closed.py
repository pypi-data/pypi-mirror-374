import logging

from .connected import Connected

logger = logging.getLogger(__name__)


class Closed(Connected):
    def __init__(self, connection):
        super().__init__(connection)
        self.can_send = True
        self.can_receive = True

    @property
    def can_send_application_data(self):
        return self.can_send

    def process(self, message):
        if self.can_receive:
            return super().process(message)
        logger.warning("receiving end closed, skip incoming %s", message.__name__)
        return None

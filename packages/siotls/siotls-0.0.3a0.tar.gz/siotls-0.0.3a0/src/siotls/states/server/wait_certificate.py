from .. import State


class ServerWaitCertificate(State):
    can_send = True
    can_send_application_data = True

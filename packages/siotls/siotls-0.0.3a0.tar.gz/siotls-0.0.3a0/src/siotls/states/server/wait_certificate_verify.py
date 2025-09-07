from .. import State


class ServerWaitCertificateVerify(State):
    can_send = True
    can_send_application_data = True

import dataclasses
import secrets
import textwrap

from siotls.iana import ContentType, HeartbeatMessageType, MaxFragmentLengthOctets
from siotls.language import Serializable

from . import Content, alerts


@dataclasses.dataclass(init=False)
class Heartbeat(Content, Serializable):
    """
    The Heartbeat protocol message as defined in :rfc:`6520#section-4`.

    Random padding is automatically added at serialization, with respect
    for :rfc:`6066#section-4` (Maximum Fragment Length).
    """

    content_type = ContentType.HEARTBEAT
    can_fragment = False

    _struct = textwrap.dedent("""
        struct {
            HeartbeatMessageType type;
            uint16 payload_length;
            opaque payload[HeartbeatMessage.payload_length];
            opaque padding[padding_length];
        } HeartbeatMessage;
    """).strip('\n')

    heartbeat_type: HeartbeatMessageType
    """ Either ``heartbeat_request`` or ``heartbeat_response``. """

    payload: bytes
    """ The opaque payload. """

    def __init__(
        self,
        heartbeat_type,
        payload,
        *,
        max_fragment_length=MaxFragmentLengthOctets.MAX_16384
    ):
        # 19 = 1 (type) + 2 (payload_length) + 16 (minimum padding length)
        if len(payload) > max_fragment_length - 19:
            e = f"payload too long: {len(payload)} > {max_fragment_length - 19}"
            raise ValueError(e)
        self.heartbeat_type = heartbeat_type
        self.payload = payload
        self._max_fragment_length = max_fragment_length

    @classmethod
    def parse(cls, stream, *, config=None, nconfig=None):
        try:
            heartbeat_type = HeartbeatMessageType(stream.read_int(1))
        except ValueError as exc:
            raise alerts.IllegalParameter(*exc.args) from exc
        payload = stream.read_var(2)
        padding = stream.read()
        return cls(heartbeat_type, payload, padding, max_fragment_length=(
            (nconfig and nconfig.max_fragment_length)
         or (config and config.max_fragment_length)
        ))

    def serialize(self):
        padding_length = self._max_fragment_length - len(self.payload) - 3
        padding = secrets.token_bytes(padding_length)

        return b''.join(
            self.heartbeat_type.to_bytes(1, 'big'),
            len(self.payload).to_bytes(2, 'big'),
            self.payload,
            padding,
        )

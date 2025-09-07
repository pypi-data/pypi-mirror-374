import dataclasses

from siotls.iana import HandshakeType
from siotls.language import SerializableBody

from . import Handshake


@dataclasses.dataclass(init=False)
class KeyUpdate(Handshake, SerializableBody):  # type: ignore[misc]
    msg_type = HandshakeType.KEY_UPDATE
    # TODO

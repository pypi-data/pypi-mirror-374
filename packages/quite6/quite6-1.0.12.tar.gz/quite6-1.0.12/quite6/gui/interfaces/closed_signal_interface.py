from . import BaseInterface
from .. import SignalSender


class ClosedSignalInterface(BaseInterface):
    @property
    def quite_closed(self) -> SignalSender:
        return self._create(SignalSender)

    @property
    def cannot_closed(self) -> SignalSender:
        return self._create(SignalSender)

    @property
    def can_close(self) -> bool:
        return self._create(lambda: True)

    @can_close.setter
    def can_close(self, value):
        self.assign(value)

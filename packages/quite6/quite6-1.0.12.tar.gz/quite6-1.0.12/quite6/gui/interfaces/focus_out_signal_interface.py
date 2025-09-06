from . import BaseInterface
from .. import SignalSender


class FocusOutSignalInterface(BaseInterface):
    @property
    def focus_out(self) -> SignalSender:
        return self._create(SignalSender)
